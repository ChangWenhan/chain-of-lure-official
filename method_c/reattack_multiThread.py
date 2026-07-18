#!/usr/bin/env python3
"""History-conditioned multi-turn CoL runner.

The attack logic matches the original script: try the current story, detect
legacy refusal phrases, then rewrite the latest story and retry up to the
configured query cap. The implementation adds CLI configuration, stable item
indices, append-only checkpoints, and resumability.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import json
import logging
import os
from pathlib import Path
import time
from typing import Any

from openai import OpenAI
from tqdm import tqdm

from utils import rewrite_prompt_template, rewrite_system_prompt, test_prefixes


LOGGER = logging.getLogger("col-multi")


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def make_client(api_key: str, base_url: str, timeout: float) -> OpenAI:
    return OpenAI(
        api_key=api_key or "EMPTY",
        base_url=base_url,
        timeout=timeout,
        max_retries=0,
    )


def call_model(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    call_type: str,
) -> str | None:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as exc:
        LOGGER.error("%s call to %s failed: %s", call_type, model, exc)
        return None


def check_success(response: str | None) -> tuple[bool, str]:
    if not response:
        return False, "No response content received from LLM to check."
    lowered = response.lower()
    for phrase in test_prefixes:
        if phrase.lower() in lowered:
            return False, f"Detected refusal phrase: '{phrase}'"
    return True, ""


def process_item(
    item_index: int,
    source: dict[str, Any],
    victim_client: OpenAI,
    attacker_client: OpenAI,
    helper_client: OpenAI,
    args: argparse.Namespace,
) -> dict[str, Any]:
    item = copy.deepcopy(source)
    goal = str(item.get("message") or "")
    current_story = str(item.get("story") or "")
    attempts: list[dict[str, Any]] = []

    if not current_story:
        return {
            **item,
            "item_index": item_index,
            "response": None,
            "failure_reason": "No initial story provided in item.",
            "attack_successful_flag": False,
            "generation_attempts": 0,
            "attempts": attempts,
            "victim_model": args.victim_label,
            "attacker_model": args.attacker_model,
            "helper_model": args.helper_model,
        }

    response: str | None = None
    failure_reason = ""
    successful = False
    generation_attempts = 0

    while generation_attempts < args.max_attempts:
        generation_attempts += 1
        if generation_attempts > 1:
            rewrite_prompt = rewrite_prompt_template.format(message=goal, story=current_story)
            use_primary = generation_attempts < args.switch_threshold
            rewrite_client = attacker_client if use_primary else helper_client
            rewrite_model = args.attacker_model if use_primary else args.helper_model
            rewritten = call_model(
                rewrite_client,
                rewrite_model,
                [
                    {"role": "system", "content": rewrite_system_prompt},
                    {"role": "user", "content": rewrite_prompt},
                ],
                args.rewriter_max_tokens,
                "Rewriter",
            )
            if not rewritten:
                failure_reason = f"Rewrite failed at attempt {generation_attempts}."
                attempts.append({
                    "attempt_number": generation_attempts,
                    "story": current_story,
                    "response": None,
                    "failure_reason": failure_reason,
                    "rewriter_model": rewrite_model,
                    "rewrite_failed": True,
                })
                if generation_attempts < args.max_attempts:
                    time.sleep(args.rewrite_failure_delay)
                continue
            current_story = rewritten
            rewriter_model = rewrite_model
        else:
            rewriter_model = None

        response = call_model(
            victim_client,
            args.victim_model,
            [{"role": "user", "content": current_story}],
            args.victim_max_tokens,
            "Victim",
        )
        successful, failure_reason = check_success(response)
        attempts.append({
            "attempt_number": generation_attempts,
            "story": current_story,
            "response": response,
            "failure_reason": failure_reason,
            "rewriter_model": rewriter_model,
            "rewrite_failed": False,
        })
        if successful:
            break

    return {
        **item,
        "item_index": item_index,
        "story": current_story,
        "response": response,
        "failure_reason": failure_reason,
        "attack_successful_flag": successful,
        "generation_attempts": generation_attempts,
        "attempts": attempts,
        "victim_model": args.victim_label,
        "attacker_model": args.attacker_model,
        "helper_model": args.helper_model,
    }


def load_completed(checkpoint: Path) -> dict[int, dict[str, Any]]:
    completed: dict[int, dict[str, Any]] = {}
    if checkpoint.exists():
        for row in read_jsonl(checkpoint):
            completed[int(row["item_index"])] = row
    return completed


def write_final(path: Path, rows: dict[int, dict[str, Any]], expected: int) -> None:
    missing = sorted(set(range(expected)) - set(rows))
    if missing:
        raise RuntimeError(f"Cannot materialize incomplete output; missing indices: {missing[:20]}")
    final_rows = []
    for index in range(expected):
        row = copy.deepcopy(rows[index])
        row.pop("item_index", None)
        row.pop("attempts", None)
        row.pop("victim_model", None)
        row.pop("attacker_model", None)
        row.pop("helper_model", None)
        row.pop("attack_successful_flag", None)
        row.pop("generation_attempts", None)
        final_rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(final_rows, handle, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--victim-model", default="victim")
    parser.add_argument("--victim-label", required=True)
    parser.add_argument("--victim-base-url", default="http://127.0.0.1:8002/v1")
    parser.add_argument("--victim-api-key-env", default="VICTIM_API_KEY")
    parser.add_argument("--attacker-model", default="deepseek-v3-2-251201")
    parser.add_argument("--helper-model", default="deepseek-v3-2-251201")
    parser.add_argument(
        "--attacker-base-url",
        default="https://ark.cn-beijing.volces.com/api/v3",
    )
    parser.add_argument("--attacker-api-key-env", default="HELPER_API_KEY")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--max-attempts", type=int, default=30)
    parser.add_argument("--switch-threshold", type=int, default=10)
    parser.add_argument("--victim-max-tokens", type=int, default=4096)
    parser.add_argument("--rewriter-max-tokens", type=int, default=4096)
    parser.add_argument("--request-timeout", type=float, default=180.0)
    parser.add_argument("--rewrite-failure-delay", type=float, default=1.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite final output: {args.output}")
    if args.checkpoint.exists() and not args.resume:
        raise FileExistsError(f"Checkpoint exists; pass --resume: {args.checkpoint}")
    if not 1 <= args.workers <= 128:
        raise ValueError("--workers must be between 1 and 128")
    if not 1 <= args.switch_threshold <= args.max_attempts:
        raise ValueError("switch threshold must be within the attempt budget")

    source_rows = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(source_rows, list):
        raise TypeError("input must be a JSON list")
    expected = min(len(source_rows), args.limit) if args.limit else len(source_rows)
    completed = load_completed(args.checkpoint) if args.resume else {}
    pending = [index for index in range(expected) if index not in completed]
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)

    victim_client = make_client(
        os.getenv(args.victim_api_key_env, "EMPTY"),
        args.victim_base_url,
        args.request_timeout,
    )
    attacker_key = os.getenv(args.attacker_api_key_env, "")
    attacker_client = make_client(attacker_key, args.attacker_base_url, args.request_timeout)
    helper_client = make_client(attacker_key, args.attacker_base_url, args.request_timeout)

    mode = "a" if args.resume else "x"
    with args.checkpoint.open(mode, encoding="utf-8") as checkpoint, ThreadPoolExecutor(
        max_workers=args.workers,
        thread_name_prefix="CoLMistral",
    ) as executor:
        futures = {
            executor.submit(
                process_item,
                index,
                source_rows[index],
                victim_client,
                attacker_client,
                helper_client,
                args,
            ): index
            for index in pending
        }
        for future in tqdm(as_completed(futures), total=len(futures), desc="CoL-multi"):
            index = futures[future]
            try:
                row = future.result()
            except Exception as exc:
                LOGGER.exception("item %d failed", index)
                row = {
                    **copy.deepcopy(source_rows[index]),
                    "item_index": index,
                    "response": None,
                    "failure_reason": f"Critical processing error: {type(exc).__name__}: {exc}",
                    "attack_successful_flag": False,
                    "generation_attempts": 0,
                    "attempts": [],
                    "victim_model": args.victim_label,
                    "attacker_model": args.attacker_model,
                    "helper_model": args.helper_model,
                }
            checkpoint.write(json.dumps(row, ensure_ascii=False) + "\n")
            checkpoint.flush()
            completed[index] = row

    invalid = [
        index
        for index, row in completed.items()
        if index < expected and not str(row.get("response") or "").strip()
    ]
    if invalid:
        raise RuntimeError(f"Completed rows without a victim response: {invalid[:20]}")
    if args.limit:
        print(f"Smoke run complete: {len(completed)}/{expected} checkpoint rows")
        return 0

    write_final(args.output, completed, expected)
    attempts = [int(completed[index]["generation_attempts"]) for index in range(expected)]
    successes = sum(bool(completed[index]["attack_successful_flag"]) for index in range(expected))
    print(
        f"Wrote {expected} rows to {args.output}; legacy successes={successes}/{expected}; "
        f"mean attempts={sum(attempts) / len(attempts):.3f}; max attempts={max(attempts)}"
    )
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(threadName)s - %(message)s",
    )
    raise SystemExit(main())
