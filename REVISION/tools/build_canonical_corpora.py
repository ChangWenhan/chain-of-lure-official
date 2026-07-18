#!/usr/bin/env python3
"""Build separate canonical corpora for all revised-paper result sets.

This script keeps the experiment collections separate. It does not run any
victim model, attacker model, or judge model. It only creates canonical inputs
for later safeguard judging.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "REVISION" / "tools" / "canonicalize_outputs.py"
OUT = ROOT / "REVISION" / "review-stage" / "outputs"


CORPORA = [
    {
        "name": "main_col",
        "include": ["output"],
        "output": "canonical_outputs.jsonl",
        "exclude": [],
    },
    {
        "name": "baselines",
        "include": ["compare_methods", "evaluation/TAP/test"],
        "output": "canonical_baselines.jsonl",
        "exclude": [],
    },
    {
        "name": "defense",
        "include": ["defense"],
        "output": "canonical_defense.jsonl",
        "exclude": [],
    },
    {
        "name": "trace",
        "include": ["output_trace"],
        "output": "canonical_trace.jsonl",
        # Exclude old TS-judge outputs and generated plotting artifacts. The raw
        # trace rows are enough for running the new safeguard judge.
        "exclude": ["output_trace/paint/"],
    },
]


def run_corpus(config: dict[str, object]) -> None:
    output = OUT / str(config["output"])
    cmd = [
        sys.executable,
        str(TOOL),
        "--root",
        str(ROOT),
        "--corpus",
        str(config["name"]),
        "--output",
        str(output),
        "--include",
        *config["include"],
    ]
    exclude = list(config.get("exclude", []))
    if exclude:
        cmd.extend(["--exclude-substring", *exclude])
    subprocess.run(cmd, check=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for config in CORPORA:
        run_corpus(config)


if __name__ == "__main__":
    main()
