#!/usr/bin/env python3
"""Create matched-judge CoL-single / Random Restart / CoL-multi tables."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


METHOD_DISPLAY = {
    "col_single_turn": "CoL-single",
    "random_restart": "Random Restart",
    "col_multi_turn": "CoL-multi",
}
METHOD_ORDER = ["col_single_turn", "random_restart", "col_multi_turn"]
VICTIM_DISPLAY = {
    "vicuna-7b-v1.5": "Vicuna-7B",
    "llama-3-8b-instruction": "Llama-3-8B",
    "llama-2-7b-chat-hf": "Llama-2-7B",
    "mistral-7b-v0.3": "Mistral-7B",
    "mistral-7b": "Mistral-7B",
}
VICTIM_ORDER = ["Vicuna-7B", "Llama-3-8B", "Llama-2-7B", "Mistral-7B"]


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def latest(paths: list[Path]) -> dict[str, dict[str, Any]]:
    result = {}
    for path in paths:
        for row in read_jsonl(path):
            if row.get("sample_id"):
                result[row["sample_id"]] = row
    return result


def summarize(
    canonical_paths: list[Path],
    ts_paths: list[Path],
    safeguard_paths: list[Path],
    qwen_paths: list[Path],
) -> list[dict[str, Any]]:
    ts = latest(ts_paths)
    safeguard = latest(safeguard_paths)
    qwen = latest(qwen_paths)
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    seen = set()
    for path in canonical_paths:
        for row in read_jsonl(path):
            if row["sample_id"] in seen:
                continue
            seen.add(row["sample_id"])
            if row.get("method") not in METHOD_DISPLAY:
                continue
            victim = VICTIM_DISPLAY.get(row.get("victim_model"), row.get("victim_model"))
            groups[(row["dataset"], row["method"], victim)].append(row)

    output = []
    for (dataset, method, victim), rows in sorted(groups.items()):
        ts_values, action_values, policy_values = [], [], []
        for row in rows:
            sample_id = row["sample_id"]
            if sample_id in ts and ts[sample_id].get("parse_status") == "ok":
                ts_values.append(float(ts[sample_id]["score"]))
            if sample_id in safeguard and safeguard[sample_id].get("parse_status") == "ok":
                action_values.append(int(safeguard[sample_id]["success_label"]))
            if sample_id in qwen and qwen[sample_id].get("parse_status") == "ok":
                policy_values.append(int(qwen[sample_id]["success_label_wide"]))
        output.append({
            "dataset": dataset,
            "method": method,
            "method_display": METHOD_DISPLAY[method],
            "victim": victim,
            "n": len(rows),
            "ts_n": len(ts_values),
            "ts": mean(ts_values) if ts_values else None,
            "actionable_n": len(action_values),
            "actionable": mean(action_values) if action_values else None,
            "policy_n": len(policy_values),
            "policy": mean(policy_values) if policy_values else None,
        })
    return output


def fmt(value: float | None, digits: int) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def report(rows: list[dict[str, Any]]) -> str:
    indexed = {(r["dataset"], r["method"], r["victim"]): r for r in rows}
    lines = [
        "# Matched-Judge Equal-Budget Restart Comparison",
        "",
        "All TS cells in this table were scored with the legacy 1--5 TS rubric. Actionable-ASR uses gpt-oss-safeguard; Policy-risk-ASR uses Qwen3Guard Unsafe+Controversial.",
        "",
        "Cell format: `TS / Actionable-ASR / Policy-risk-ASR`.",
        "",
    ]
    macro: dict[tuple[str, str], tuple[float, float, float]] = {}
    for dataset in ("advbench", "gptfuzz"):
        lines.extend([
            f"## {'AdvBench' if dataset == 'advbench' else 'GPTFuzz'}",
            "",
            "| Strategy | " + " | ".join(VICTIM_ORDER) + " |",
            "|---|" + "---:|" * len(VICTIM_ORDER),
        ])
        for method in METHOD_ORDER:
            cells = []
            available = []
            for victim in VICTIM_ORDER:
                row = indexed.get((dataset, method, victim))
                if not row or None in (row["ts"], row["actionable"], row["policy"]):
                    cells.append("—")
                    continue
                cells.append(f"{fmt(row['ts'], 2)} / {fmt(row['actionable'], 3)} / {fmt(row['policy'], 3)}")
                available.append(row)
            lines.append(f"| {METHOD_DISPLAY[method]} | " + " | ".join(cells) + " |")
            if available:
                macro[(dataset, method)] = (
                    mean(r["ts"] for r in available),
                    mean(r["actionable"] for r in available),
                    mean(r["policy"] for r in available),
                )
        lines.append("")

    lines.extend([
        "## Open-victim macro averages",
        "",
        "Macro averages give equal weight to each available victim. The recovered AdvBench CoL-multi/Mistral group is included as a real measured cell; no value is imputed.",
        "",
        "| Dataset | Strategy | TS | Actionable-ASR | Policy-risk-ASR |",
        "|---|---|---:|---:|---:|",
    ])
    for dataset in ("advbench", "gptfuzz"):
        for method in METHOD_ORDER:
            values = macro.get((dataset, method))
            if values:
                lines.append(f"| {dataset} | {METHOD_DISPLAY[method]} | {values[0]:.3f} | {values[1]:.3f} | {values[2]:.3f} |")

    lines.extend([
        "",
        "## Strict common-victim macro averages",
        "",
        "These rows use only victims with complete cells for all three strategies. Both datasets now include all four open victims.",
        "",
        "| Dataset | Strategy | Victims | TS | Actionable-ASR | Policy-risk-ASR |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for dataset in ("advbench", "gptfuzz"):
        complete_sets = []
        for method in METHOD_ORDER:
            complete_sets.append({
                victim for victim in VICTIM_ORDER
                if (dataset, method, victim) in indexed
                and None not in (
                    indexed[(dataset, method, victim)]["ts"],
                    indexed[(dataset, method, victim)]["actionable"],
                    indexed[(dataset, method, victim)]["policy"],
                )
            })
        common = set.intersection(*complete_sets)
        ordered_common = [victim for victim in VICTIM_ORDER if victim in common]
        for method in METHOD_ORDER:
            selected = [indexed[(dataset, method, victim)] for victim in ordered_common]
            lines.append(
                f"| {dataset} | {METHOD_DISPLAY[method]} | {len(selected)} | "
                f"{mean(r['ts'] for r in selected):.3f} | "
                f"{mean(r['actionable'] for r in selected):.3f} | "
                f"{mean(r['policy'] for r in selected):.3f} |"
            )

    lines.extend([
        "",
        "## Coverage",
        "",
        "| Dataset | Strategy | Victim | n | TS n | Actionable n | Policy-risk n |",
        "|---|---|---|---:|---:|---:|---:|",
    ])
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['method_display']} | {row['victim']} | {row['n']} | {row['ts_n']} | {row['actionable_n']} | {row['policy_n']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, nargs="+", required=True)
    parser.add_argument("--ts", type=Path, nargs="+", required=True)
    parser.add_argument("--safeguard", type=Path, nargs="+", required=True)
    parser.add_argument("--qwen", type=Path, nargs="+", required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument(
        "--markdown",
        type=Path,
        help="Optional disposable Markdown preview; CSV is the retained summary.",
    )
    args = parser.parse_args()
    outputs = [args.csv]
    if args.markdown is not None:
        outputs.append(args.markdown)
    for output in outputs:
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite {output}")
    rows = summarize(args.canonical, args.ts, args.safeguard, args.qwen)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    if args.markdown is not None:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(report(rows), encoding="utf-8")
        print(f"Wrote optional preview to {args.markdown}")
    print(f"Wrote {len(rows)} matched comparison groups to {args.csv}")


if __name__ == "__main__":
    main()
