#!/usr/bin/env python3
"""Run the Qwen3Guard-Gen-8B judge for selected revised-paper corpora.

Convenience wrapper mirroring run_safeguard_all_corpora.py but writing to
qwen3guard_*.jsonl files. Defaults to P0 scope: main_col + baselines.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "REVISION" / "tools" / "run_qwen3guard_judge.py"
OUT = ROOT / "REVISION" / "review-stage" / "outputs"


CORPORA = [
    ("main_col", "canonical_outputs.jsonl", "qwen3guard_main_col.jsonl"),
    ("baselines", "canonical_baselines.jsonl", "qwen3guard_baselines.jsonl"),
    ("defense", "canonical_defense.jsonl", "qwen3guard_defense.jsonl"),
    ("trace", "canonical_trace.jsonl", "qwen3guard_trace.jsonl"),
]
DEFAULT_CORPORA = ["main_col", "baselines"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Optional per-corpus limit for dry runs.")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--max-response-chars", type=int, default=18000)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--corpus",
        nargs="*",
        default=DEFAULT_CORPORA,
        help="Subset of corpora to run: main_col baselines defense trace, or all. Defaults to P0: main_col baselines.",
    )
    args = parser.parse_args()

    wanted = set(args.corpus)
    if "all" in wanted:
        wanted = {name for name, _input, _output in CORPORA}
    for name, input_name, output_name in CORPORA:
        if name not in wanted:
            continue
        cmd = [
            sys.executable,
            str(TOOL),
            "--input",
            str(OUT / input_name),
            "--output",
            str(OUT / output_name),
            "--max-retries",
            str(args.max_retries),
            "--workers",
            str(args.workers),
            "--max-tokens",
            str(args.max_tokens),
            "--max-response-chars",
            str(args.max_response_chars),
        ]
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        if args.base_url:
            cmd.extend(["--base-url", args.base_url])
        if args.api_key:
            cmd.extend(["--api-key", args.api_key])
        if args.model:
            cmd.extend(["--model", args.model])
        print(f"Running Qwen3Guard judge for corpus={name}")
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
