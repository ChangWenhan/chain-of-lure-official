#!/usr/bin/env python3
"""Materialize clean TS artifacts from an append-only retry log.

The source log is preserved. For every sample ID this tool selects its latest
record, verifies that all historically failed samples were subsequently judged
successfully, and writes both the repaired subset and a full clean snapshot in
canonical input order.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                yield line_number, json.loads(line)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True, help="Append-only TS judge log")
    parser.add_argument("--canonical", type=Path, required=True, help="Canonical corpus defining output order")
    parser.add_argument("--clean-output", type=Path, required=True)
    parser.add_argument("--repaired-output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    args = parser.parse_args()

    history: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    physical_records = 0
    for line_number, row in read_jsonl(args.source):
        sample_id = row.get("sample_id")
        if not sample_id:
            raise ValueError(f"Missing sample_id at {args.source}:{line_number}")
        history[str(sample_id)].append((line_number, row))
        physical_records += 1

    canonical_ids: list[str] = []
    for line_number, row in read_jsonl(args.canonical):
        sample_id = row.get("sample_id")
        if not sample_id:
            raise ValueError(f"Missing sample_id at {args.canonical}:{line_number}")
        canonical_ids.append(str(sample_id))
    if len(canonical_ids) != len(set(canonical_ids)):
        raise ValueError("Canonical input contains duplicate sample IDs")

    historical_error_ids = {
        sample_id
        for sample_id, records in history.items()
        if any(row.get("parse_status") != "ok" for _, row in records)
    }
    latest = {sample_id: records[-1][1] for sample_id, records in history.items()}
    missing = [sample_id for sample_id in canonical_ids if sample_id not in latest]
    extra = sorted(set(latest) - set(canonical_ids))
    latest_errors = [
        sample_id for sample_id in canonical_ids
        if sample_id in latest and latest[sample_id].get("parse_status") != "ok"
    ]
    unrepaired = sorted(historical_error_ids & set(latest_errors))
    if missing or extra or latest_errors:
        raise RuntimeError(
            f"Cannot materialize clean artifact: missing={len(missing)}, "
            f"extra={len(extra)}, latest_errors={len(latest_errors)}, "
            f"historical_errors_unrepaired={len(unrepaired)}"
        )

    clean_rows = [latest[sample_id] for sample_id in canonical_ids]
    repaired_rows = [latest[sample_id] for sample_id in canonical_ids if sample_id in historical_error_ids]
    write_jsonl(args.clean_output, clean_rows)
    write_jsonl(args.repaired_output, repaired_rows)

    audit = {
        "source": str(args.source),
        "canonical": str(args.canonical),
        "physical_source_records": physical_records,
        "unique_source_samples": len(history),
        "canonical_samples": len(canonical_ids),
        "historical_error_samples": len(historical_error_ids),
        "historical_error_samples_repaired": len(repaired_rows),
        "historical_error_samples_unrepaired": len(unrepaired),
        "latest_parse_valid_samples": len(clean_rows),
        "clean_output": str(args.clean_output),
        "repaired_output": str(args.repaired_output),
    }
    if args.audit_output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.audit_output}")
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    with args.audit_output.open("x", encoding="utf-8") as handle:
        json.dump(audit, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    print(json.dumps(audit, ensure_ascii=False))


if __name__ == "__main__":
    main()
