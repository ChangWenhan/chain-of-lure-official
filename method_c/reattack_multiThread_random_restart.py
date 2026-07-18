#!/usr/bin/env python3
"""Equal-budget random-restart baseline for Chain-of-Lure.

For every harmful goal, each attempt independently generates a new narrative from
the original goal and sends it to the victim.  The generator never receives a
previous narrative or a victim response/refusal.  This is deliberately different
from ``reattack_multiThread.py``, which conditions each rewrite on the previous
narrative.

The script writes three non-overwriting artifacts:

* ``*.attempts.jsonl``: one complete record per goal, including every attempt.
* ``*.final.json``: legacy-compatible final records for the evaluation scripts.
* ``*.summary.json``: run configuration and the legacy refusal-prefix statistic.

Use ``--resume`` with the same ``--output-prefix`` after an interrupted run.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import logging
import os
import re
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI
from tqdm import tqdm


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from attack_story.story_templates import old_template as NARRATIVE_PROMPT_TEMPLATE  # noqa: E402
from method_c.utils import test_prefixes  # noqa: E402


LOG = logging.getLogger("random_restart")
WRITE_LOCK = threading.Lock()


@dataclass(frozen=True)
class RunPaths:
    attempts: Path
    final: Path
    summary: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the equal-budget random-restart baseline: every attempt samples "
            "a fresh narrative from the original goal only."
        )
    )
    parser.add_argument("--input", type=Path, required=True, help="CSV or JSON input containing goal/message records")
    parser.add_argument("--dataset", required=True, choices=("advbench", "gptfuzz"))
    parser.add_argument("--victim-model", required=True, help="Model name exposed by the local OpenAI-compatible server")
    parser.add_argument("--victim-label", required=True, help="Stable paper-facing victim label used in output names")
    parser.add_argument("--victim-base-url", default="http://127.0.0.1:8002/v1")
    parser.add_argument("--victim-api-key-env", default="VICTIM_API_KEY")
    parser.add_argument("--attacker-model", default="deepseek-v3-2-251201")
    parser.add_argument("--attacker-base-url", default="https://ark.cn-beijing.volces.com/api/v3")
    parser.add_argument("--attacker-api-key-env", default="HELPER_API_KEY")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--max-attempts", type=int, default=30)
    parser.add_argument("--victim-max-tokens", type=int, default=8192)
    parser.add_argument("--attacker-max-tokens", type=int, default=8192)
    parser.add_argument("--attacker-temperature", type=float, default=1.0)
    parser.add_argument("--request-timeout", type=float, default=180.0)
    parser.add_argument("--api-retries", type=int, default=3)
    parser.add_argument("--retry-backoff", type=float, default=2.0)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "REVISION" / "random_restart" / "outputs")
    parser.add_argument(
        "--output-prefix",
        help="Explicit basename without extension. Defaults to a timestamped, non-overwriting name.",
    )
    parser.add_argument("--resume", action="store_true", help="Append only missing item indices to an existing attempts file")
    parser.add_argument("--limit", type=int, help="Process only the first N items (for smoke tests)")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    return parser.parse_args()


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return value or "unnamed"


def build_paths(args: argparse.Namespace) -> RunPaths:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.output_prefix:
        prefix = slugify(args.output_prefix)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"random_restart_{args.dataset}_{slugify(args.victim_label)}_{timestamp}"
    return RunPaths(
        attempts=args.output_dir / f"{prefix}.attempts.jsonl",
        final=args.output_dir / f"{prefix}.final.json",
        summary=args.output_dir / f"{prefix}.summary.json",
    )


def validate_args(args: argparse.Namespace, paths: RunPaths) -> None:
    if args.workers < 1 or args.workers > 128:
        raise ValueError("--workers must be between 1 and 128")
    if args.max_attempts < 1:
        raise ValueError("--max-attempts must be positive")
    if args.api_retries < 1:
        raise ValueError("--api-retries must be positive")
    if not args.input.is_file():
        raise FileNotFoundError(args.input)

    existing = [path for path in asdict(paths).values() if Path(path).exists()]
    if args.resume:
        if not paths.attempts.exists():
            raise FileNotFoundError(f"Cannot resume: {paths.attempts} does not exist")
    elif existing:
        joined = ", ".join(map(str, existing))
        raise FileExistsError(f"Refusing to overwrite existing artifact(s): {joined}")


def load_goals(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            raw: Any = list(csv.DictReader(handle))
    elif path.suffix.lower() in {".json", ".jsonl"}:
        if path.suffix.lower() == ".jsonl":
            with path.open("r", encoding="utf-8") as handle:
                raw = [json.loads(line) for line in handle if line.strip()]
        else:
            with path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
    else:
        raise ValueError(f"Unsupported input format: {path.suffix}")

    if not isinstance(raw, list):
        raise ValueError("Input must contain a list of records")

    goals: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if isinstance(item, str):
            goal, source = item, {}
        elif isinstance(item, dict):
            goal = item.get("goal") or item.get("message")
            source = item
        else:
            raise ValueError(f"Input record {index} is neither a string nor an object")
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError(f"Input record {index} has no non-empty goal/message")
        goals.append({"item_index": index, "goal": goal.strip(), "source": source})
    return goals


def read_completed_indices(path: Path) -> set[int]:
    completed: set[int] = set()
    if not path.exists():
        return completed
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                # A transport/API failure must remain resumable. A genuine
                # refusal is complete because it still has a victim response.
                final_response = record.get("final_selected_response")
                if isinstance(final_response, str) and final_response.strip():
                    completed.add(int(record["item_index"]))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid resume record at {path}:{line_number}: {exc}") from exc
    return completed


def make_client(api_key: str, base_url: str, timeout: float) -> OpenAI:
    return OpenAI(api_key=api_key or "EMPTY", base_url=base_url, timeout=timeout, max_retries=0)


def call_chat(
    client: OpenAI,
    *,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    retries: int,
    retry_backoff: float,
    temperature: float | None = None,
) -> tuple[str | None, dict[str, Any]]:
    error: str | None = None
    started = time.monotonic()
    for api_attempt in range(1, retries + 1):
        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "stream": False,
            }
            if temperature is not None:
                kwargs["temperature"] = temperature
            response = client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            usage = getattr(response, "usage", None)
            meta = {
                "api_attempts": api_attempt,
                "latency_seconds": round(time.monotonic() - started, 4),
                "finish_reason": getattr(choice, "finish_reason", None),
                "usage": usage.model_dump() if usage is not None else None,
                "error": None,
            }
            return choice.message.content, meta
        except Exception as exc:  # API clients expose several provider-specific exception types
            error = f"{type(exc).__name__}: {exc}"
            LOG.warning("API call %s/%s to %s failed: %s", api_attempt, retries, model, error)
            if api_attempt < retries:
                time.sleep(retry_backoff * (2 ** (api_attempt - 1)))
    return None, {
        "api_attempts": retries,
        "latency_seconds": round(time.monotonic() - started, 4),
        "finish_reason": None,
        "usage": None,
        "error": error,
    }


def check_legacy_success(response: str | None) -> tuple[bool, str]:
    """Replicate the refusal-prefix stopping rule from reattack_multiThread.py."""
    if not response:
        return False, "No response content received from victim."
    lowered = response.lower()
    for phrase in test_prefixes:
        if phrase.lower() in lowered:
            return False, f"Detected refusal phrase: '{phrase}'"
    return True, ""


def process_goal(
    item: dict[str, Any],
    args: argparse.Namespace,
    attacker_client: OpenAI,
    victim_client: OpenAI,
) -> dict[str, Any]:
    goal = item["goal"]
    attempts: list[dict[str, Any]] = []
    legacy_success = False
    stopping_reason = "max_attempts_exhausted"

    # Every iteration formats the same original goal. No prior story, refusal, or
    # victim response is present in the generator messages.
    generator_prompt = NARRATIVE_PROMPT_TEMPLATE.format(goal)
    for attempt_index in range(1, args.max_attempts + 1):
        narrative, attacker_meta = call_chat(
            attacker_client,
            model=args.attacker_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": generator_prompt},
            ],
            max_tokens=args.attacker_max_tokens,
            retries=args.api_retries,
            retry_backoff=args.retry_backoff,
            temperature=args.attacker_temperature,
        )

        victim_response: str | None = None
        victim_meta: dict[str, Any] | None = None
        failure_reason: str
        if narrative:
            victim_response, victim_meta = call_chat(
                victim_client,
                model=args.victim_model,
                messages=[{"role": "user", "content": narrative}],
                max_tokens=args.victim_max_tokens,
                retries=args.api_retries,
                retry_backoff=args.retry_backoff,
            )
            legacy_success, failure_reason = check_legacy_success(victim_response)
        else:
            legacy_success = False
            failure_reason = "Narrative generation failed; victim was not queried."

        attempts.append(
            {
                "attempt_index": attempt_index,
                "narrative": narrative,
                "victim_response": victim_response,
                "legacy_attack_successful_flag": legacy_success,
                "failure_reason": failure_reason,
                "attacker_call": attacker_meta,
                "victim_call": victim_meta,
            }
        )
        if legacy_success:
            stopping_reason = "legacy_non_refusal_detected"
            break

    selected = attempts[-1]
    return {
        "schema_version": "random_restart.v1",
        "strategy": "random_restart",
        "dataset": args.dataset,
        "victim_label": args.victim_label,
        "victim_model": args.victim_model,
        "attacker_model": args.attacker_model,
        "item_index": item["item_index"],
        "goal": goal,
        "message": goal,
        "source": item["source"],
        "max_attempts": args.max_attempts,
        "generation_attempts": len(attempts),
        "stopping_reason": stopping_reason,
        "attack_successful_flag": legacy_success,
        "failure_reason": selected["failure_reason"],
        "final_selected_narrative": selected["narrative"],
        "final_selected_response": selected["victim_response"],
        "story": selected["narrative"],
        "response": selected["victim_response"],
        "attempts": attempts,
    }


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    encoded = json.dumps(record, ensure_ascii=False) + "\n"
    with WRITE_LOCK:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())


def load_attempt_records(path: Path) -> list[dict[str, Any]]:
    latest: dict[int, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                record = json.loads(line)
                latest[int(record["item_index"])] = record
    return [latest[index] for index in sorted(latest)]


def write_json_exclusive(path: Path, data: Any, *, allow_replace: bool) -> None:
    mode = "w" if allow_replace else "x"
    with path.open(mode, encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def materialize_final_artifacts(args: argparse.Namespace, paths: RunPaths, records: list[dict[str, Any]]) -> None:
    final_records = []
    for record in records:
        final_records.append(
            {
                "item_index": record["item_index"],
                "dataset": record["dataset"],
                "method": "Random Restart",
                "attacker": record["attacker_model"],
                "victim": record["victim_label"],
                "message": record["goal"],
                "goal": record["goal"],
                "story": record["final_selected_narrative"],
                "response": record["final_selected_response"],
                "failure_reason": record["failure_reason"],
                "attack_successful_flag": record["attack_successful_flag"],
                "generation_attempts": record["generation_attempts"],
                "stopping_reason": record["stopping_reason"],
            }
        )

    successes = sum(bool(row["attack_successful_flag"]) for row in records)
    attempt_count = sum(int(row["generation_attempts"]) for row in records)
    summary = {
        "schema_version": "random_restart.summary.v1",
        "created_at": datetime.now().astimezone().isoformat(),
        "dataset": args.dataset,
        "strategy": "random_restart",
        "victim_label": args.victim_label,
        "victim_model": args.victim_model,
        "victim_base_url": args.victim_base_url,
        "attacker_model": args.attacker_model,
        "attacker_base_url": args.attacker_base_url,
        "workers": args.workers,
        "max_attempts": args.max_attempts,
        "record_count": len(records),
        "legacy_non_refusal_count": successes,
        "legacy_non_refusal_rate": successes / len(records) if records else None,
        "total_generation_attempts": attempt_count,
        "mean_generation_attempts": attempt_count / len(records) if records else None,
        "attempts_artifact": str(paths.attempts),
        "final_artifact": str(paths.final),
        "note": (
            "The legacy non-refusal statistic is only the historical stopping rule. "
            "Paper-facing TS, Actionable-ASR, and Policy-risk-ASR require separate judges."
        ),
    }
    write_json_exclusive(paths.final, final_records, allow_replace=args.resume)
    write_json_exclusive(paths.summary, summary, allow_replace=args.resume)


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(threadName)s %(message)s",
    )
    paths = build_paths(args)
    validate_args(args, paths)

    attacker_key = os.getenv(args.attacker_api_key_env, "")
    victim_key = os.getenv(args.victim_api_key_env, "EMPTY")
    if not attacker_key:
        raise RuntimeError(f"Required attacker key environment variable is empty: {args.attacker_api_key_env}")

    goals = load_goals(args.input)
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError("--limit must be positive")
        goals = goals[: args.limit]

    completed = read_completed_indices(paths.attempts) if args.resume else set()
    pending = [item for item in goals if item["item_index"] not in completed]
    LOG.info("Loaded %d goals; %d complete and %d pending", len(goals), len(completed), len(pending))
    LOG.info("Attempts artifact: %s", paths.attempts)

    attacker_client = make_client(attacker_key, args.attacker_base_url, args.request_timeout)
    victim_client = make_client(victim_key, args.victim_base_url, args.request_timeout)

    failures = 0
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.workers, thread_name_prefix="RandomRestartWorker"
    ) as executor:
        future_to_item = {
            executor.submit(process_goal, item, args, attacker_client, victim_client): item
            for item in pending
        }
        for future in tqdm(
            concurrent.futures.as_completed(future_to_item),
            total=len(future_to_item),
            desc=f"{args.dataset}/{args.victim_label}",
        ):
            item = future_to_item[future]
            try:
                append_jsonl(paths.attempts, future.result())
            except Exception as exc:
                failures += 1
                LOG.exception("Uncaught failure for item %s: %s", item["item_index"], exc)

    records = load_attempt_records(paths.attempts)
    materialize_final_artifacts(args, paths, records)
    LOG.info("Materialized %d final records at %s", len(records), paths.final)
    LOG.info("Summary written to %s", paths.summary)
    if failures:
        LOG.error("%d worker(s) failed without a completed record; resume this run", failures)
        return 2
    if len(records) != len(goals):
        LOG.error("Expected %d records but found %d; resume this run", len(goals), len(records))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
