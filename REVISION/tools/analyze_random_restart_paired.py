#!/usr/bin/env python3
"""Paired statistics for CoL strategies versus equal-budget random restart."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import binomtest


METHODS = ("col_single_turn", "random_restart", "col_multi_turn")
COMPARISONS = ("col_single_turn", "col_multi_turn")
DISPLAY = {
    "col_single_turn": "CoL-single - Random Restart",
    "col_multi_turn": "CoL-multi - Random Restart",
}
METRICS = ("ts", "actionable", "policy")
VICTIM_ALIASES = {
    "mistral-7b": "mistral-7b-v0.3",
}


def jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def latest(paths: list[Path]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in paths:
        for row in jsonl(path):
            if row.get("sample_id"):
                rows[row["sample_id"]] = row
    return rows


def holm(pvalues: list[float]) -> list[float]:
    order = sorted(range(len(pvalues)), key=pvalues.__getitem__)
    adjusted = [1.0] * len(pvalues)
    running = 0.0
    m = len(pvalues)
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[idx]))
        adjusted[idx] = running
    return adjusted


def format_p(value: float) -> str:
    return "<0.001" if value < 0.001 else f"{value:.4g}"


def stable_seed(dataset: str, comparison: str, metric: str, base: int) -> int:
    digest = hashlib.sha256(f"{dataset}|{comparison}|{metric}|{base}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % (2**32)


def stratified_bootstrap(
    differences: dict[str, np.ndarray], *, iterations: int, seed: int
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    draws = np.zeros(iterations, dtype=np.float64)
    for values in differences.values():
        indices = rng.integers(0, len(values), size=(iterations, len(values)))
        draws += values[indices].mean(axis=1) / len(differences)
    low, high = np.quantile(draws, [0.025, 0.975])
    return float(low), float(high)


def sign_flip_p(differences: np.ndarray, *, iterations: int, seed: int) -> float:
    observed = abs(float(differences.mean()))
    if not np.any(differences):
        return 1.0
    rng = np.random.default_rng(seed)
    exceed = 0
    remaining = iterations
    while remaining:
        size = min(1000, remaining)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(size, len(differences)))
        exceed += int(np.count_nonzero(np.abs((signs * differences).mean(axis=1)) >= observed))
        remaining -= size
    return (exceed + 1) / (iterations + 1)


def mcnemar_exact(reference: np.ndarray, comparison: np.ndarray) -> tuple[int, int, float]:
    reference_only = int(np.count_nonzero((reference == 1) & (comparison == 0)))
    comparison_only = int(np.count_nonzero((reference == 0) & (comparison == 1)))
    discordant = reference_only + comparison_only
    pvalue = 1.0 if discordant == 0 else float(
        binomtest(
            min(reference_only, comparison_only),
            discordant,
            0.5,
            alternative="two-sided",
        ).pvalue
    )
    return reference_only, comparison_only, pvalue


def analyze(args: argparse.Namespace) -> list[dict[str, Any]]:
    ts = latest(args.ts)
    safeguard = latest(args.safeguard)
    qwen = latest(args.qwen)
    judged: dict[tuple[str, str, str], dict[str, dict[str, float]]] = defaultdict(dict)

    seen: set[str] = set()
    for path in args.canonical:
        for row in jsonl(path):
            sid = str(row["sample_id"])
            if sid in seen or row.get("method") not in METHODS:
                continue
            seen.add(sid)
            if not all(
                sid in source and source[sid].get("parse_status") == "ok"
                for source in (ts, safeguard, qwen)
            ):
                raise RuntimeError(f"Missing parse-valid judgment for {sid}")
            victim = VICTIM_ALIASES.get(str(row["victim_model"]), str(row["victim_model"]))
            key = (str(row["dataset"]), victim, str(row["task_id"]))
            method = str(row["method"])
            if method in judged[key]:
                raise RuntimeError(f"Duplicate method record for {key}/{method}")
            judged[key][method] = {
                "ts": float(ts[sid]["score"]),
                "actionable": float(safeguard[sid]["success_label"]),
                "policy": float(qwen[sid]["success_label_wide"]),
            }

    common_victims: dict[str, list[str]] = {}
    for dataset in ("advbench", "gptfuzz"):
        method_victims = []
        for method in METHODS:
            method_victims.append({
                victim
                for (ds, victim, _), values in judged.items()
                if ds == dataset and method in values
            })
        common_victims[dataset] = sorted(set.intersection(*method_victims))
        expected = 4
        if len(common_victims[dataset]) != expected:
            raise RuntimeError(
                f"{dataset}: expected {expected} common victims, got {common_victims[dataset]}"
            )

    results: list[dict[str, Any]] = []
    for dataset in ("advbench", "gptfuzz"):
        victims = common_victims[dataset]
        for comparison in COMPARISONS:
            paired = {
                key: values
                for key, values in judged.items()
                if key[0] == dataset
                and key[1] in victims
                and "random_restart" in values
                and comparison in values
            }
            result: dict[str, Any] = {
                "dataset": dataset,
                "comparison": comparison,
                "comparison_display": DISPLAY[comparison],
                "n_pairs": len(paired),
                "victims": len(victims),
                "victim_models": ",".join(victims),
            }
            for metric in METRICS:
                restart = np.array([values["random_restart"][metric] for values in paired.values()])
                col = np.array([values[comparison][metric] for values in paired.values()])
                difference = col - restart
                by_victim = {
                    victim: np.array([
                        values[comparison][metric] - values["random_restart"][metric]
                        for key, values in paired.items()
                        if key[1] == victim
                    ])
                    for victim in victims
                }
                if any(len(values) == 0 for values in by_victim.values()):
                    raise RuntimeError(f"{dataset}/{comparison}/{metric}: empty victim stratum")
                macro_delta = float(np.mean([values.mean() for values in by_victim.values()]))
                low, high = stratified_bootstrap(
                    by_victim,
                    iterations=args.iterations,
                    seed=stable_seed(dataset, comparison, metric, args.seed),
                )
                result[f"{metric}_restart"] = float(restart.mean())
                result[f"{metric}_comparison"] = float(col.mean())
                result[f"{metric}_delta"] = macro_delta
                result[f"{metric}_ci_low"] = low
                result[f"{metric}_ci_high"] = high
                if metric == "ts":
                    result[f"{metric}_p"] = sign_flip_p(
                        difference,
                        iterations=args.iterations,
                        seed=stable_seed(dataset, comparison, "ts_p", args.seed),
                    )
                else:
                    restart_only, comparison_only, pvalue = mcnemar_exact(restart, col)
                    result[f"{metric}_restart_only"] = restart_only
                    result[f"{metric}_comparison_only"] = comparison_only
                    result[f"{metric}_p"] = pvalue
            results.append(result)

    for dataset in ("advbench", "gptfuzz"):
        subset = [row for row in results if row["dataset"] == dataset]
        for metric in METRICS:
            adjusted = holm([float(row[f"{metric}_p"]) for row in subset])
            for row, value in zip(subset, adjusted):
                row[f"{metric}_p_holm"] = value
    return results


def signed(value: float) -> str:
    return f"{value:+.3f}"


def report(rows: list[dict[str, Any]], iterations: int) -> str:
    lines = [
        "# Paired Equal-Budget Random-Restart Statistics",
        "",
        "Deltas are `CoL strategy - Random Restart`. After recovery of the missing AdvBench CoL-multi/Mistral group, both datasets use all four open victims. Confidence intervals use "
        f"{iterations:,} stratified paired bootstrap draws (resampling goals within victim). TS p-values use paired sign-flip tests; binary metrics use exact McNemar tests. Holm correction is applied across the two strategy contrasts within each dataset and metric.",
        "",
    ]
    for dataset in ("advbench", "gptfuzz"):
        lines.extend([
            f"## {'AdvBench' if dataset == 'advbench' else 'GPTFuzz'}",
            "",
            "| Contrast | n pairs | victims | ΔTS [95% CI] | Holm p | ΔActionable [95% CI] | Holm p | ΔPolicy-risk [95% CI] | Holm p |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in rows:
            if row["dataset"] != dataset:
                continue
            lines.append(
                f"| {row['comparison_display']} | {row['n_pairs']} | {row['victims']} | "
                f"{signed(row['ts_delta'])} [{signed(row['ts_ci_low'])}, {signed(row['ts_ci_high'])}] | {format_p(row['ts_p_holm'])} | "
                f"{signed(row['actionable_delta'])} [{signed(row['actionable_ci_low'])}, {signed(row['actionable_ci_high'])}] | {format_p(row['actionable_p_holm'])} | "
                f"{signed(row['policy_delta'])} [{signed(row['policy_ci_low'])}, {signed(row['policy_ci_high'])}] | {format_p(row['policy_p_holm'])} |"
            )
        lines.append("")
    return "\n".join(lines)


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
        help="Optional disposable Markdown preview; CSV is the retained statistical result.",
    )
    parser.add_argument("--iterations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260620)
    args = parser.parse_args()
    if args.iterations < 1000:
        raise ValueError("--iterations must be at least 1000")
    outputs = [args.csv]
    if args.markdown is not None:
        outputs.append(args.markdown)
    for path in outputs:
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    rows = analyze(args)
    with args.csv.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if args.markdown is not None:
        args.markdown.write_text(report(rows, args.iterations), encoding="utf-8")
    print(f"Wrote paired statistics for {len(rows)} dataset/strategy comparisons")


if __name__ == "__main__":
    main()
