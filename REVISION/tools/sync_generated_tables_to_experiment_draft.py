#!/usr/bin/env python3
"""Render and sync completed revision tables into EXPERIMENT_SECTION_DRAFT.md.

The script is deliberately narrow: it replaces only the main leaderboard,
main robustness, and generator-sensitivity placeholder blocks. It refuses to run
unless the four full-corpus guard outputs have complete latest-ok coverage.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from generate_revision_md_tables import render_report


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "REVISION" / "review-stage" / "outputs"
DRAFT = ROOT / "REVISION" / "EXPERIMENT_SECTION_DRAFT.md"

REQUIRED_OUTPUTS = {
    OUT / "safeguard_main_col.jsonl": 43346,
    OUT / "safeguard_baselines.jsonl": 20675,
    OUT / "qwen3guard_main_col.jsonl": 43346,
    OUT / "qwen3guard_baselines.jsonl": 20675,
}


def latest_ok_count(path: Path) -> tuple[int, int]:
    latest: dict[str, str | None] = {}
    json_errors = 0
    if not path.exists():
        return 0, 0
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                json_errors += 1
                continue
            sample_id = row.get("sample_id")
            if sample_id:
                latest[str(sample_id)] = row.get("parse_status")
    return sum(1 for status in latest.values() if status == "ok"), json_errors


def require_complete_outputs() -> None:
    problems = []
    for path, expected in REQUIRED_OUTPUTS.items():
        ok, errors = latest_ok_count(path)
        if ok != expected or errors:
            problems.append(f"{path.name}: latest_ok={ok}/{expected}, json_errors={errors}")
    if problems:
        raise SystemExit("Guard outputs are incomplete; refusing to sync tables:\n" + "\n".join(problems))


def clean_generated_table(block: str) -> str:
    block = re.sub(r'<span style="color:red">(.*?)</span>', r"\1", block)
    block = block.strip()
    return block


def extract_between(text: str, start: str, end: str) -> str:
    start_idx = text.index(start) + len(start)
    end_idx = text.index(end, start_idx)
    return clean_generated_table(text[start_idx:end_idx])


def extract_first_table_after(text: str, marker: str) -> str:
    marker_idx = text.index(marker)
    table_start = text.index("\n|", marker_idx) + 1
    lines = []
    for line in text[table_start:].splitlines():
        if not line.startswith("|"):
            break
        lines.append(line)
    return clean_generated_table("\n".join(lines))


def replace_between(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start_idx = text.index(start_marker)
    content_start = text.index("\n\n", start_idx) + 2
    end_idx = text.index(end_marker, content_start)
    return text[:content_start] + "\n" + replacement.strip() + "\n\n" + text[end_idx:]


def restore_final_metric_language(text: str) -> str:
    text = text.replace(
        "The final revised cell format is `TS / Actionable-ASR / Policy-risk-ASR`; this interim draft fills `TS / GPT-OSS-ASR` first while Qwen3Guard is still running.",
        "The revised cell format is `TS / Actionable-ASR / Policy-risk-ASR`, replacing the earlier `ASR / TS` view.",
    )
    text = text.replace(
        "**Table 1: Interim main method leaderboard on AdvBench.** Each cell is `TS / GPT-OSS-ASR`; Policy-risk-ASR will be filled after Qwen3Guard completes.",
        "**Table 1: Main three-dimensional method leaderboard on AdvBench.** Each cell is `TS / Actionable-ASR / Policy-risk-ASR`.",
    )
    text = text.replace(
        "**Table 2: Interim main method leaderboard on GPTFuzz.** Each cell is `TS / GPT-OSS-ASR`.",
        "**Table 2: Main three-dimensional method leaderboard on GPTFuzz.** Each cell is `TS / Actionable-ASR / Policy-risk-ASR`.",
    )
    text = text.replace(
        "**Table 3: Interim main-leaderboard robustness statistics.** This table reports TS and GPT-OSS-ASR only; Policy-risk-ASR will be added after Qwen3Guard completes.",
        "**Table 3: Main-leaderboard robustness statistics.** For each method and each metric, report the number of dataset-victim cells, mean, variance, standard deviation, and 95% confidence interval over the available victim-model groups. The CoL rows use only the DeepSeek-V3 generator, matching Tables 1 and 2.",
    )
    text = text.replace(
        "Interim cells are `TS / GPT-OSS-ASR`; Policy-risk-ASR is pending Qwen3Guard completion.",
        "Each cell is `TS / Actionable-ASR / Policy-risk-ASR` after the full-corpus guard rerun.",
    )
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate coverage, rendering, and replacement markers without writing the draft.",
    )
    args = parser.parse_args()
    require_complete_outputs()
    generated = render_report()
    draft = restore_final_metric_language(DRAFT.read_text(encoding="utf-8"))

    replacements = [
        (
            "**Table 1:",
            "**Table 2:",
            extract_between(generated, "### AdvBench\n", "\n### GPTFuzz"),
        ),
        (
            "**Table 2:",
            "**Table 3:",
            extract_between(generated, "### GPTFuzz\n", "\n## Test-Generator Sensitivity Tables"),
        ),
        (
            "**Table 3:",
            "These two leaderboard tables are the primary performance result",
            extract_first_table_after(generated, "## Main-Table Statistical / Dataset-Shift Analysis"),
        ),
        (
            "**Table 8:",
            "**Table 9:",
            extract_between(generated, "### AdvBench / CoL-single\n", "\n### AdvBench / CoL-multi"),
        ),
        (
            "**Table 9:",
            "**Table 10:",
            extract_between(generated, "### AdvBench / CoL-multi\n", "\n### GPTFuzz / CoL-single"),
        ),
        (
            "**Table 10:",
            "**Table 11:",
            extract_between(generated, "### GPTFuzz / CoL-single\n", "\n### GPTFuzz / CoL-multi"),
        ),
        (
            "**Table 11:",
            "## 5.6 Controlled Component Diagnostic",
            extract_between(generated, "### GPTFuzz / CoL-multi\n", "\n## Additional Safeguard Metrics"),
        ),
    ]

    for start, end, replacement in replacements:
        draft = replace_between(draft, start, end, replacement)

    if args.check:
        print("Coverage, rendering, and draft replacement markers are valid")
        return
    DRAFT.write_text(draft, encoding="utf-8")
    print(f"Synced generated tables into {DRAFT}")


if __name__ == "__main__":
    main()
