#!/usr/bin/env python3
"""Join TS, gpt-oss, and Qwen3Guard results for Random Restart."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


VICTIM_DISPLAY = {
    "vicuna-7b-v1.5": "Vicuna-7B",
    "llama-3-8b-instruction": "Llama-3-8B",
    "llama-2-7b-chat-hf": "Llama-2-7B",
    "mistral-7b-v0.3": "Mistral-7B",
    "mistral-7b": "Mistral-7B",
}
VICTIM_ORDER = ["vicuna-7b-v1.5", "llama-3-8b-instruction", "llama-2-7b-chat-hf", "mistral-7b"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def latest_by_sample(path: Path) -> dict[str, dict[str, Any]]:
    latest = {}
    for row in load_jsonl(path):
        if row.get("sample_id"):
            latest[row["sample_id"]] = row
    return latest


def wilson(successes: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if not n:
        return None, None
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return center - half, center + half


def mean_normal_ci(values: list[float], z: float = 1.96) -> tuple[float | None, float | None, float | None]:
    if not values:
        return None, None, None
    m = mean(values)
    if len(values) == 1:
        return m, m, m
    variance = sum((value - m) ** 2 for value in values) / (len(values) - 1)
    half = z * math.sqrt(variance / len(values))
    return m, m - half, m + half


def summarize(
    canonical: list[dict[str, Any]],
    ts: dict[str, dict[str, Any]],
    safeguard: dict[str, dict[str, Any]],
    qwen: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in canonical:
        groups[(row["dataset"], row["victim_model"])].append(row)
    result = []
    for (dataset, victim), rows in sorted(groups.items()):
        ts_values = []
        action_values = []
        policy_values = []
        attempts = []
        for row in rows:
            sample_id = row["sample_id"]
            ts_row = ts.get(sample_id)
            if ts_row and ts_row.get("parse_status") == "ok" and ts_row.get("score") is not None:
                ts_values.append(float(ts_row["score"]))
            safeguard_row = safeguard.get(sample_id)
            if safeguard_row and safeguard_row.get("parse_status") == "ok":
                action_values.append(int(safeguard_row["success_label"]))
            qwen_row = qwen.get(sample_id)
            if qwen_row and qwen_row.get("parse_status") == "ok":
                policy_values.append(int(qwen_row["success_label_wide"]))
            if row.get("generation_attempts") is not None:
                attempts.append(int(row["generation_attempts"]))
        ts_mean, ts_low, ts_high = mean_normal_ci(ts_values)
        action_low, action_high = wilson(sum(action_values), len(action_values))
        policy_low, policy_high = wilson(sum(policy_values), len(policy_values))
        result.append({
            "dataset": dataset,
            "victim_model": victim,
            "victim_display": VICTIM_DISPLAY.get(victim, victim),
            "n": len(rows),
            "ts_n": len(ts_values),
            "ts_mean": ts_mean,
            "ts_ci95_low": ts_low,
            "ts_ci95_high": ts_high,
            "actionable_n": len(action_values),
            "actionable_asr": sum(action_values) / len(action_values) if action_values else None,
            "actionable_ci95_low": action_low,
            "actionable_ci95_high": action_high,
            "policy_risk_n": len(policy_values),
            "policy_risk_asr": sum(policy_values) / len(policy_values) if policy_values else None,
            "policy_risk_ci95_low": policy_low,
            "policy_risk_ci95_high": policy_high,
            "mean_attempts": mean(attempts) if attempts else None,
            "max_attempts": max(attempts) if attempts else None,
        })
    return result


def fmt(value: float | None, digits: int = 3) -> str:
    return "NA" if value is None else f"{value:.{digits}f}"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    indexed = {(row["dataset"], row["victim_model"]): row for row in rows}
    lines = [
        "# Equal-Budget Random Restart Results",
        "",
        "Cell format: `TS / Actionable-ASR / Policy-risk-ASR`. TS uses the legacy 1--5 rubric with the actual judge model recorded in raw outputs; Actionable-ASR is gpt-oss `success_label`; Policy-risk-ASR is Qwen3Guard Unsafe+Controversial.",
        "",
    ]
    for dataset in ("advbench", "gptfuzz"):
        lines.extend([
            f"## {'AdvBench' if dataset == 'advbench' else 'GPTFuzz'}",
            "",
            "| Strategy | " + " | ".join(VICTIM_DISPLAY[victim] for victim in VICTIM_ORDER) + " |",
            "|---|" + "---:|" * len(VICTIM_ORDER),
        ])
        cells = []
        for victim in VICTIM_ORDER:
            row = indexed.get((dataset, victim))
            if not row:
                cells.append("NA")
            else:
                cells.append(
                    f"{fmt(row['ts_mean'], 2)} / {fmt(row['actionable_asr'])} / {fmt(row['policy_risk_asr'])}"
                )
        lines.extend(["| Random Restart | " + " | ".join(cells) + " |", ""])
    lines.extend([
        "## Coverage and Search Diagnostics",
        "",
        "| Dataset | Victim | n | TS n | Actionable n | Policy-risk n | Mean attempts | Max attempts |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['victim_display']} | {row['n']} | {row['ts_n']} | {row['actionable_n']} | {row['policy_risk_n']} | {fmt(row['mean_attempts'], 3)} | {row['max_attempts']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--ts", type=Path, required=True)
    parser.add_argument("--safeguard", type=Path, required=True)
    parser.add_argument("--qwen", type=Path, required=True)
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
        output.parent.mkdir(parents=True, exist_ok=True)
    rows = summarize(
        load_jsonl(args.canonical),
        latest_by_sample(args.ts),
        latest_by_sample(args.safeguard),
        latest_by_sample(args.qwen),
    )
    write_csv(args.csv, rows)
    if args.markdown is not None:
        write_markdown(args.markdown, rows)
        print(f"Wrote optional preview to {args.markdown}")
    print(f"Wrote {len(rows)} Random Restart groups to {args.csv}")


if __name__ == "__main__":
    main()
