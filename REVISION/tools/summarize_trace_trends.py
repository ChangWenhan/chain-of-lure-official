#!/usr/bin/env python3
"""Summarize the retained PPL and TS trends from multi-turn trace files."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from statistics import mean

import numpy as np


def read_rows(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not row.get("summary"):
            yield row


def dataset_from_name(name: str) -> str:
    if name.startswith("advbench_") or name.startswith("eval_advbench_"):
        return "AdvBench"
    if name.startswith("gptfuzz_") or name.startswith("eval_gptfuzz_"):
        return "GPTFuzz"
    raise ValueError(f"Cannot infer dataset from {name}")


def victim_from_name(name: str) -> str:
    stem = name.removeprefix("eval_")
    stem = stem.removeprefix("advbench_trace_attack_").removeprefix("gptfuzz_trace_attack_")
    return stem.removesuffix(".jsonl")


def load_metric(paths: list[Path], field: str) -> dict[tuple[str, str, str, int], float]:
    result = {}
    for path in paths:
        dataset = dataset_from_name(path.name)
        victim = victim_from_name(path.name)
        for row in read_rows(path):
            iteration = row.get("iteration_num")
            value = row.get(field)
            goal = str(row.get("goal") or "")
            if not isinstance(iteration, int) or not isinstance(value, (int, float)):
                continue
            if not goal or not math.isfinite(float(value)):
                continue
            result[(dataset, victim, goal, iteration)] = float(value)
    return result


def cluster_ci(
    deltas: dict[str, list[float]], *, iterations: int, seed: int
) -> tuple[float, float, float]:
    goals = sorted(deltas)
    observed = mean(value for values in deltas.values() for value in values)
    rng = np.random.default_rng(seed)
    draws = np.empty(iterations, dtype=float)
    for index in range(iterations):
        selected = rng.integers(0, len(goals), size=len(goals))
        values = [value for goal_index in selected for value in deltas[goals[goal_index]]]
        draws[index] = np.mean(values)
    low, high = np.quantile(draws, [0.025, 0.975])
    return observed, float(low), float(high)


def trend_rows(metric: dict[tuple[str, str, str, int], float]):
    grouped = defaultdict(list)
    for (dataset, _victim, _goal, iteration), value in metric.items():
        grouped[(dataset, iteration)].append(value)
        grouped[("Combined", iteration)].append(value)
    return grouped


def paired_first_second(metric: dict[tuple[str, str, str, int], float], dataset: str):
    by_unit = defaultdict(dict)
    for (ds, victim, goal, iteration), value in metric.items():
        if dataset != "Combined" and ds != dataset:
            continue
        if iteration in (1, 2):
            by_unit[(ds, victim, goal)][iteration] = value
    paired = {key: values for key, values in by_unit.items() if 1 in values and 2 in values}
    clusters = defaultdict(list)
    for (ds, _victim, goal), values in paired.items():
        clusters[f"{ds}|{goal}"].append(values[2] - values[1])
    return paired, clusters


def fmt_ci(values: tuple[float, float, float]) -> str:
    return f"{values[0]:+.3f} [{values[1]:+.3f}, {values[2]:+.3f}]"


def build_report(ppl, ts, iterations: int, seed: int) -> str:
    ppl_trend = trend_rows(ppl)
    ts_trend = trend_rows(ts)
    lines = [
        "# Trace Analysis: PPL and TS Trends",
        "",
        "This is the only retained trace analysis. Trace files contain only trajectories that eventually succeeded after more than one interaction, so the results are conditional process diagnostics rather than population-level attack-performance estimates.",
        "",
        "## Iteration Trends",
        "",
        "| Dataset | Iteration | PPL mean | PPL n | TS mean | TS n |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for dataset in ("AdvBench", "GPTFuzz", "Combined"):
        iterations_present = sorted({it for ds, it in set(ppl_trend) | set(ts_trend) if ds == dataset})
        for iteration in iterations_present:
            pvals = ppl_trend.get((dataset, iteration), [])
            tvals = ts_trend.get((dataset, iteration), [])
            lines.append(
                f"| {dataset} | {iteration} | "
                f"{mean(pvals):.3f} | {len(pvals)} | {mean(tvals):.3f} | {len(tvals)} |"
            )

    lines.extend([
        "",
        "## Paired First-to-Second Iteration Change",
        "",
        f"Confidence intervals use {iterations:,} bootstrap draws clustered by goal; all victim trajectories for a sampled goal move together.",
        "",
        "| Dataset | Paired trajectories | Goal clusters | ΔPPL [95% CI] | ΔTS [95% CI] |",
        "|---|---:|---:|---:|---:|",
    ])
    for offset, dataset in enumerate(("AdvBench", "GPTFuzz", "Combined")):
        ppl_pairs, ppl_clusters = paired_first_second(ppl, dataset)
        ts_pairs, ts_clusters = paired_first_second(ts, dataset)
        common = set(ppl_pairs) & set(ts_pairs)
        if len(common) != len(ppl_pairs) or len(common) != len(ts_pairs):
            raise RuntimeError(f"{dataset}: PPL/TS paired-unit mismatch")
        lines.append(
            f"| {dataset} | {len(common)} | {len(ppl_clusters)} | "
            f"{fmt_ci(cluster_ci(ppl_clusters, iterations=iterations, seed=seed + offset))} | "
            f"{fmt_ci(cluster_ci(ts_clusters, iterations=iterations, seed=seed + 100 + offset))} |"
        )

    lines.extend([
        "",
        "## Reading",
        "",
        "1. The first-to-second interaction is the only well-supported trend segment: it has hundreds of paired trajectories, whereas iteration 3 has only 50 records and later iterations rapidly fall to single digits.",
        "2. PPL and TS both rise from the first to the second interaction in the combined trace. This describes how the retained successful multi-turn trajectories evolve; it does not show that higher PPL causes higher harmfulness or that later rounds always improve results.",
        "3. Iterations 3 onward should remain visible only with their sample counts. Their non-monotonic means are too sparse and selection-conditioned for inferential claims.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-dir", type=Path, default=Path("output_trace"))
    parser.add_argument("--output", type=Path, default=Path("REVISION/review-stage/outputs/trace_ppl_ts_trends.md"))
    parser.add_argument("--iterations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260620)
    args = parser.parse_args()
    if args.iterations < 1000:
        raise ValueError("--iterations must be at least 1000")
    ppl_paths = sorted(args.trace_dir.glob("*trace_attack*.jsonl"))
    ts_paths = sorted((args.trace_dir / "paint").glob("eval_*trace_attack*.jsonl"))
    if len(ppl_paths) != 14 or len(ts_paths) != 14:
        raise RuntimeError(f"Expected 14 PPL and 14 TS files, got {len(ppl_paths)} and {len(ts_paths)}")
    ppl = load_metric(ppl_paths, "ppl")
    ts = load_metric(ts_paths, "judge_score")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_report(ppl, ts, args.iterations, args.seed), encoding="utf-8")
    print(f"Wrote {args.output} from {len(ppl)} PPL and {len(ts)} TS records")


if __name__ == "__main__":
    main()
