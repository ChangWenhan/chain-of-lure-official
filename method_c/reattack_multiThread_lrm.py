#!/usr/bin/env python3
"""History-conditioned multi-turn CoL runner with Large Reasoning Model support.

Extends ``reattack_multiThread.py`` to capture the victim model's reasoning
process (``reasoning_content``) alongside the final output.  Compatible with
any OpenAI-API-compatible endpoint that returns reasoning tokens (DeepSeek-R1,
Qwen3 with ``enable_thinking``, vLLM reasoning backends, etc.).

Key differences from the base runner:

* ``call_model()`` returns a dict with ``content`` and ``reasoning`` keys
  instead of a plain string.
* Refusal detection still runs against ``content`` only (reasoning is internal
  monologue, not the surface response).
* Every attempt record and the final output include a ``reasoning`` field.
* The rewriter path is unchanged (plain text); only victim calls capture
  reasoning.

Usage (same CLI as the base runner plus LRM-specific flags)::

    python method_c/reattack_multiThread_lrm.py \\
        --input stories.json \\
        --output results.json \\
        --checkpoint checkpoint.jsonl \\
        --victim-label mistral-7b \\
        --victim-model qwen3-8b \\
        --victim-enable-thinking \\
        --workers 8
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from openai import OpenAI
from tqdm import tqdm

from utils import rewrite_prompt_template, rewrite_system_prompt, test_prefixes

LOGGER = logging.getLogger("col-multi-lrm")


# ---------------------------------------------------------------------------
# I/O helpers (identical to base runner)
# ---------------------------------------------------------------------------

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


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def merge_extra_body(
    extra_body_json: str | None,
    enable_thinking: bool,
) -> dict[str, Any] | None:
    extra_body: dict[str, Any] = {}
    if extra_body_json:
        parsed = json.loads(extra_body_json)
        if not isinstance(parsed, dict):
            raise TypeError("--victim-extra-body-json must decode to a JSON object")
        extra_body.update(parsed)
    if enable_thinking:
        chat_template_kwargs = dict(extra_body.get("chat_template_kwargs") or {})
        chat_template_kwargs["enable_thinking"] = True
        extra_body["chat_template_kwargs"] = chat_template_kwargs
    return extra_body or None


# ---------------------------------------------------------------------------
# Model calling (LRM-aware)
# ---------------------------------------------------------------------------

def call_model(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    call_type: str,
    extra_body: dict[str, Any] | None = None,
    qwen3_fallback: bool = False,
    stream: bool = False,
    reasoning_effort: str | None = None,
    max_retries: int = 3,
) -> dict[str, str | None]:
    """Call *model* and return a dict with ``content`` and ``reasoning``.

    ``reasoning`` is ``None`` when the model / provider does not return
    reasoning tokens.  ``content`` is ``None`` on API failure after all
    retries are exhausted.
    """
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            kwargs: dict[str, Any] = dict(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                stream=stream,
            )
            if extra_body:
                kwargs["extra_body"] = extra_body
            if reasoning_effort:
                kwargs["reasoning_effort"] = reasoning_effort
            response = client.chat.completions.create(**kwargs)
            if stream:
                content_parts: list[str] = []
                reasoning_parts: list[str] = []
                for chunk in response:
                    if not getattr(chunk, "choices", None):
                        continue
                    delta = chunk.choices[0].delta
                    content_piece = getattr(delta, "content", None)
                    if content_piece:
                        content_parts.append(content_piece)
                    reasoning_piece = _extract_reasoning(delta, qwen3_fallback=False)
                    if reasoning_piece:
                        reasoning_parts.append(reasoning_piece)
                content = "".join(content_parts) or None
                reasoning = "".join(reasoning_parts) or None
                if not reasoning and qwen3_fallback and content and " response" in content:
                    reasoning, _, answer = content.partition(" response")
                    reasoning = reasoning.strip() or None
                    content = answer.strip() if answer.strip() else content
                return {"content": content, "reasoning": reasoning}

            message = response.choices[0].message
            content = message.content
            reasoning = _extract_reasoning(message, qwen3_fallback=qwen3_fallback)
            # If reasoning was extracted via Qwen3 fallback ( response split),
            # strip it from content so refusal checks only see the answer.
            if reasoning and content and qwen3_fallback and " response" in content:
                _, _, answer = content.partition(" response")
                content = answer.strip() if answer.strip() else content
            return {"content": content, "reasoning": reasoning}
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                delay = 2 ** attempt
                LOGGER.warning(
                    "%s call to %s failed (attempt %d/%d), retrying in %ds: %s",
                    call_type, model, attempt, max_retries, delay, exc,
                )
                time.sleep(delay)
            else:
                LOGGER.error(
                    "%s call to %s failed after %d attempts: %s",
                    call_type, model, max_retries, exc,
                )
    return {"content": None, "reasoning": None}


def _extract_reasoning(
    message: Any, qwen3_fallback: bool = False,
) -> str | None:
    """Best-effort extraction of reasoning tokens from a chat message."""
    # Direct attribute (OpenAI SDK ≥ 1.x with reasoning models, e.g. DeepSeek)
    reasoning = getattr(message, "reasoning_content", None)
    if reasoning:
        return reasoning
    # Fallback: some providers stash it in model_extra
    extra = getattr(message, "model_extra", None) or {}
    reasoning = extra.get("reasoning_content")
    if reasoning:
        return reasoning
    # Qwen3 fallback (only when --victim-enable-thinking is set):
    # vLLM's Qwen3 reasoning parser requires  thinking in the model output,
    # but the chat template adds it to the prompt instead.  When the parser
    # fails, the entire output (thinking +  response + answer) lands in
    # content.  Split on the  response token manually.
    if qwen3_fallback:
        content = message.content
        if content and " response" in content:
            reasoning, _, _ = content.partition(" response")
            return reasoning.strip() if reasoning.strip() else None
    return None


def call_model_legacy(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    call_type: str,
) -> str | None:
    """Backward-compatible plain-text call (used by the rewriter path)."""
    result = call_model(
        client,
        model,
        messages,
        max_tokens,
        call_type,
        qwen3_fallback=False,
        stream=False,
        reasoning_effort=None,
    )
    return result["content"]


# ---------------------------------------------------------------------------
# Refusal detection
# ---------------------------------------------------------------------------

def check_success(response_content: str | None) -> tuple[bool, str]:
    """Check *content* (not reasoning) for refusal prefixes."""
    if not response_content:
        return False, "No response content received from LLM to check."
    lowered = response_content.lower()
    for phrase in test_prefixes:
        if phrase.lower() in lowered:
            return False, f"Detected refusal phrase: '{phrase}'"
    return True, ""


# ---------------------------------------------------------------------------
# Per-item attack logic
# ---------------------------------------------------------------------------

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
            "reasoning": None,
            "failure_reason": "No initial story provided in item.",
            "attack_successful_flag": False,
            "generation_attempts": 0,
            "attempts": attempts,
            "victim_model": args.victim_label,
            "attacker_model": args.attacker_model,
            "helper_model": args.helper_model,
        }

    response_content: str | None = None
    response_reasoning: str | None = None
    failure_reason = ""
    successful = False
    generation_attempts = 0

    victim_extra_body = merge_extra_body(
        args.victim_extra_body_json,
        args.victim_enable_thinking,
    )

    while generation_attempts < args.max_attempts:
        generation_attempts += 1

        # --- Rewrite (unchanged from base runner) --------------------------
        if generation_attempts > 1:
            rewrite_prompt = rewrite_prompt_template.format(
                message=goal, story=current_story
            )
            use_primary = generation_attempts < args.switch_threshold
            rewrite_client = attacker_client if use_primary else helper_client
            rewrite_model = args.attacker_model if use_primary else args.helper_model
            rewritten = call_model_legacy(
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
                    "reasoning": None,
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

        # --- Victim call (LRM-aware) ---------------------------------------
        victim_result = call_model(
            victim_client,
            args.victim_model,
            [{"role": "user", "content": current_story}],
            args.victim_max_tokens,
            "Victim",
            extra_body=victim_extra_body,
            qwen3_fallback=args.victim_enable_thinking,
            stream=args.victim_stream,
            reasoning_effort=args.victim_reasoning_effort,
        )
        response_content = victim_result["content"]
        response_reasoning = victim_result["reasoning"]
        successful, failure_reason = check_success(response_content)

        attempts.append({
            "attempt_number": generation_attempts,
            "story": current_story,
            "response": response_content,
            "reasoning": response_reasoning,
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
        "response": response_content,
        "reasoning": response_reasoning,
        "failure_reason": failure_reason,
        "attack_successful_flag": successful,
        "generation_attempts": generation_attempts,
        "attempts": attempts,
        "victim_model": args.victim_label,
        "attacker_model": args.attacker_model,
        "helper_model": args.helper_model,
    }


# ---------------------------------------------------------------------------
# Checkpoint / output
# ---------------------------------------------------------------------------

def load_completed(checkpoint: Path) -> dict[int, dict[str, Any]]:
    completed: dict[int, dict[str, Any]] = {}
    if checkpoint.exists():
        for row in read_jsonl(checkpoint):
            completed[int(row["item_index"])] = row
    return completed


def write_final(path: Path, rows: dict[int, dict[str, Any]], expected: int) -> None:
    missing = sorted(set(range(expected)) - set(rows))
    if missing:
        raise RuntimeError(
            f"Cannot materialize incomplete output; missing indices: {missing[:20]}"
        )
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output_lrm"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CoL-multi runner with LRM reasoning capture."
    )
    # Core I/O
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument(
        "--run-name",
        default=None,
        help="Short name for this run (e.g. 'deepseek-r1-advbench'). "
        "When set, --output and --checkpoint are auto-derived under output_lrm/.",
    )
    # Victim
    parser.add_argument("--victim-model", default=os.getenv("VICTIM_MODEL", "victim"))
    parser.add_argument("--victim-label", default=os.getenv("VICTIM_LABEL"))
    parser.add_argument(
        "--victim-base-url",
        default=os.getenv("VICTIM_BASE_URL", "http://127.0.0.1:8002/v1"),
    )
    parser.add_argument(
        "--victim-api-key-env",
        default=os.getenv("VICTIM_API_KEY_ENV", "VICTIM_API_KEY"),
    )
    parser.add_argument(
        "--victim-enable-thinking",
        action="store_true",
        default=env_flag("VICTIM_ENABLE_THINKING"),
        help="Pass enable_thinking=True via extra_body (vLLM / Qwen3 thinking mode).",
    )
    parser.add_argument(
        "--victim-stream",
        action="store_true",
        default=env_flag("VICTIM_STREAM"),
        help="Use streaming Chat Completions for victim calls; useful when reasoning_content is only emitted in deltas.",
    )
    parser.add_argument(
        "--victim-extra-body-json",
        default=os.getenv("VICTIM_EXTRA_BODY_JSON", ""),
        help="JSON object merged into victim chat.completions.create(extra_body=...).",
    )
    parser.add_argument(
        "--victim-reasoning-effort",
        choices=["low", "medium", "high"],
        default=os.getenv("VICTIM_REASONING_EFFORT", ""),
        help="Pass reasoning_effort to the victim API when the provider supports it.",
    )
    # Attacker / helper
    parser.add_argument("--attacker-model", default="deepseek-v3-2-251201")
    parser.add_argument("--helper-model", default="deepseek-v3-2-251201")
    parser.add_argument(
        "--attacker-base-url",
        default="https://ark.cn-beijing.volces.com/api/v3",
    )
    parser.add_argument("--attacker-api-key-env", default="HELPER_API_KEY")
    # Tuning
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    if not args.victim_label:
        args.victim_label = args.victim_model

    # Resolve --run-name into --output and --checkpoint
    if args.run_name:
        if args.output or args.checkpoint:
            raise ValueError("--run-name is mutually exclusive with --output/--checkpoint")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        args.output = OUTPUT_DIR / f"{args.run_name}.json"
        args.checkpoint = OUTPUT_DIR / f"{args.run_name}.checkpoint.jsonl"

    if not args.output or not args.checkpoint:
        raise ValueError("either --run-name or both --output and --checkpoint are required")

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
    attacker_client = make_client(
        attacker_key, args.attacker_base_url, args.request_timeout
    )
    helper_client = make_client(
        attacker_key, args.attacker_base_url, args.request_timeout
    )

    mode = "a" if args.resume else "x"
    with args.checkpoint.open(mode, encoding="utf-8") as checkpoint, ThreadPoolExecutor(
        max_workers=args.workers,
        thread_name_prefix="CoL-LRM",
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
        for future in tqdm(as_completed(futures), total=len(futures), desc="CoL-multi-LRM"):
            index = futures[future]
            try:
                row = future.result()
            except Exception as exc:
                LOGGER.exception("item %d failed", index)
                row = {
                    **copy.deepcopy(source_rows[index]),
                    "item_index": index,
                    "response": None,
                    "reasoning": None,
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
        raise RuntimeError(
            f"Completed rows without a victim response: {invalid[:20]}"
        )
    if args.limit:
        print(f"Smoke run complete: {len(completed)}/{expected} checkpoint rows")
        return 0

    write_final(args.output, completed, expected)
    attempts = [
        int(completed[index]["generation_attempts"]) for index in range(expected)
    ]
    successes = sum(
        bool(completed[index]["attack_successful_flag"]) for index in range(expected)
    )
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
