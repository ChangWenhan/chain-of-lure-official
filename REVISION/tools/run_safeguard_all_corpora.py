#!/usr/bin/env python3
"""Run the safeguard judge for selected revised-paper corpora.

This is a convenience wrapper. It keeps outputs separated by corpus and defaults
to the P0 paper scope: main CoL results plus baselines. Defense and trace are
conditional analyses that should be requested explicitly.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "REVISION" / "tools" / "run_safeguard_judge.py"
OUT = ROOT / "REVISION" / "review-stage" / "outputs"


CORPORA = [
    ("main_col", "canonical_outputs.jsonl", "safeguard_main_col.jsonl"),
    ("baselines", "canonical_baselines.jsonl", "safeguard_baselines.jsonl"),
    ("defense", "canonical_defense.jsonl", "safeguard_defense.jsonl"),
    ("trace", "canonical_trace.jsonl", "safeguard_trace.jsonl"),
]
DEFAULT_CORPORA = ["main_col", "baselines"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Optional per-corpus limit for dry runs.")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-tokens", type=int, default=1536)
    parser.add_argument(
        "--reasoning-effort",
        choices=["low", "medium", "high"],
        default=None,
        help="Optional. Omit to use the provider/model default reasoning effort.",
    )
    parser.add_argument("--max-response-chars", type=int, default=3000)
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
        if args.reasoning_effort:
            cmd.extend(["--reasoning-effort", args.reasoning_effort])
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        if args.base_url:
            cmd.extend(["--base-url", args.base_url])
        if args.api_key:
            cmd.extend(["--api-key", args.api_key])
        if args.model:
            cmd.extend(["--model", args.model])
        print(f"Running safeguard judge for corpus={name}")
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
