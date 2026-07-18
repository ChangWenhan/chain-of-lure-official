#!/usr/bin/env python3
"""Run the full revision guard-judge pipeline on one local GPU.

This coordinator is intentionally conservative:
- it reuses resume-safe judge scripts;
- it never edits raw experiment outputs;
- it runs only one vLLM guard server at a time on port 8000;
- it validates latest ok sample_id coverage before moving to the next guard.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "REVISION" / "review-stage" / "outputs"
LOG = ROOT / "REVISION" / "review-stage" / "logs"
API_URL = "http://127.0.0.1:8000/v1/models"

PROXY_VARS = [
    "ALL_PROXY",
    "all_proxy",
    "HTTP_PROXY",
    "http_proxy",
    "HTTPS_PROXY",
    "https_proxy",
]

SAFEGUARD_TARGETS = {
    OUT / "safeguard_main_col.jsonl": 43346,
    OUT / "safeguard_baselines.jsonl": 20675,
}
QWEN_TARGETS = {
    OUT / "qwen3guard_main_col.jsonl": 43346,
    OUT / "qwen3guard_baselines.jsonl": 20675,
}


def clean_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in PROXY_VARS:
        env.pop(key, None)
    env["NO_PROXY"] = "localhost,127.0.0.1,::1"
    env["no_proxy"] = "localhost,127.0.0.1,::1"
    return env


def run(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        env=clean_env(),
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def screen_ls() -> str:
    result = run(["screen", "-ls"], check=False)
    return result.stdout or ""


def screen_running(name: str) -> bool:
    return f".{name}" in screen_ls()


def start_screen(name: str, command: str) -> None:
    LOG.mkdir(parents=True, exist_ok=True)
    wrapped = f"cd {shlex.quote(str(ROOT))} && {command}"
    run(["screen", "-dmS", name, "bash", "-lc", wrapped])
    print(f"[pipeline] started screen {name}", flush=True)


def stop_screen(name: str) -> None:
    if screen_running(name):
        run(["screen", "-S", name, "-X", "quit"], check=False)
        print(f"[pipeline] stopped screen {name}", flush=True)
        time.sleep(15)


def latest_counts(path: Path) -> tuple[int, int, int, dict[str, int]]:
    if not path.exists():
        return 0, 0, 0, {}
    rows = 0
    json_errors = 0
    latest: dict[str, str | None] = {}
    status_counts: dict[str, int] = {}
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                json_errors += 1
                continue
            sample_id = row.get("sample_id")
            status = row.get("parse_status")
            if sample_id:
                latest[str(sample_id)] = status
            status_counts[str(status)] = status_counts.get(str(status), 0) + 1
    ok = sum(1 for status in latest.values() if status == "ok")
    return rows, ok, json_errors, status_counts


def targets_complete(targets: dict[Path, int]) -> bool:
    complete = True
    for path, expected in targets.items():
        rows, ok, json_errors, status_counts = latest_counts(path)
        print(
            f"[pipeline] {path.name}: rows={rows}, latest_ok={ok}/{expected}, "
            f"json_errors={json_errors}, statuses={status_counts}",
            flush=True,
        )
        if ok != expected or json_errors:
            complete = False
    return complete


def model_ids() -> list[str]:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(API_URL, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return []
    return [str(item.get("id")) for item in payload.get("data", [])]


def wait_api(served_model_name: str, timeout_s: int = 900) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        ids = model_ids()
        if served_model_name in ids:
            print(f"[pipeline] API ready for {served_model_name}", flush=True)
            return
        if ids:
            raise RuntimeError(f"port 8000 serves {ids}, expected {served_model_name}")
        time.sleep(10)
    raise TimeoutError(f"API did not become ready for {served_model_name}")


def ensure_server(name: str, served_model_name: str, command: str) -> None:
    ids = model_ids()
    if served_model_name in ids:
        return
    if ids:
        raise RuntimeError(f"port 8000 serves {ids}, expected {served_model_name}")
    if not screen_running(name):
        start_screen(name, command)
    wait_api(served_model_name)


def ensure_judge(name: str, command: str, targets: dict[Path, int]) -> None:
    if targets_complete(targets):
        return
    if not screen_running(name):
        start_screen(name, command)


def wait_judge(
    label: str,
    targets: dict[Path, int],
    judge_screen: str,
    judge_command: str,
    server_screen: str,
    served_model_name: str,
    server_command: str,
) -> None:
    while True:
        if targets_complete(targets):
            print(f"[pipeline] {label} coverage complete", flush=True)
            return
        if not screen_running(judge_screen):
            print(f"[pipeline] {label} judge is not running; resuming", flush=True)
            ensure_server(server_screen, served_model_name, server_command)
            start_screen(judge_screen, judge_command)
        time.sleep(300)


def main() -> None:
    LOG.mkdir(parents=True, exist_ok=True)

    safeguard_server = (
        "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True "
        "conda run -n agents python -m vllm.entrypoints.openai.api_server "
        "--model /mnt/disk/cwh/LLMs/gpt-oss-safeguard-20b "
        "--served-model-name gpt-oss-safeguard-20b "
        "--host 127.0.0.1 --port 8000 --trust-remote-code --dtype auto "
        "--max-model-len 8192 --gpu-memory-utilization 0.75 "
        "--max-num-seqs 8 --max-num-batched-tokens 1024 "
        "> REVISION/review-stage/logs/vllm_safeguard_20260624.log 2>&1"
    )
    safeguard_judge = (
        "env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy "
        "-u HTTPS_PROXY -u https_proxy "
        "python REVISION/tools/run_safeguard_all_corpora.py "
        "--corpus main_col baselines "
        "--base-url http://127.0.0.1:8000/v1 --api-key EMPTY "
        "--model gpt-oss-safeguard-20b --workers 8 --max-tokens 1536 "
        "--max-response-chars 3000 "
        "> REVISION/review-stage/logs/judge_safeguard_main_baselines_20260624.log 2>&1"
    )

    qwen_server = (
        "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True "
        "conda run -n agents python -m vllm.entrypoints.openai.api_server "
        "--model /mnt/disk/cwh/LLMs/Qwen3Guard-Gen-8B "
        "--served-model-name Qwen3Guard-Gen-8B "
        "--host 127.0.0.1 --port 8000 --trust-remote-code --dtype auto "
        "--max-model-len 8192 --gpu-memory-utilization 0.85 --max-num-seqs 16 "
        "> REVISION/review-stage/logs/vllm_qwen3guard_20260624.log 2>&1"
    )
    qwen_judge = (
        "env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy "
        "-u HTTPS_PROXY -u https_proxy "
        "python REVISION/tools/run_qwen3guard_all_corpora.py "
        "--corpus main_col baselines "
        "--base-url http://127.0.0.1:8000/v1 --api-key EMPTY "
        "--model Qwen3Guard-Gen-8B --workers 12 --max-tokens 128 "
        "--max-response-chars 3000 "
        "> REVISION/review-stage/logs/judge_qwen3guard_main_baselines_20260624.log 2>&1"
    )

    ensure_server(
        "rev_guard_safeguard_20260624",
        "gpt-oss-safeguard-20b",
        safeguard_server,
    )
    ensure_judge("rev_judge_safeguard_20260624", safeguard_judge, SAFEGUARD_TARGETS)
    wait_judge(
        "safeguard",
        SAFEGUARD_TARGETS,
        "rev_judge_safeguard_20260624",
        safeguard_judge,
        "rev_guard_safeguard_20260624",
        "gpt-oss-safeguard-20b",
        safeguard_server,
    )
    stop_screen("rev_guard_safeguard_20260624")

    ensure_server("rev_guard_qwen3guard_20260624", "Qwen3Guard-Gen-8B", qwen_server)
    ensure_judge("rev_judge_qwen3guard_20260624", qwen_judge, QWEN_TARGETS)
    wait_judge(
        "qwen3guard",
        QWEN_TARGETS,
        "rev_judge_qwen3guard_20260624",
        qwen_judge,
        "rev_guard_qwen3guard_20260624",
        "Qwen3Guard-Gen-8B",
        qwen_server,
    )
    stop_screen("rev_guard_qwen3guard_20260624")

    print("[pipeline] generating revision markdown tables", flush=True)
    run(["python", "REVISION/tools/generate_revision_md_tables.py"])
    print("[pipeline] syncing generated tables into experiment draft", flush=True)
    run(["python", "REVISION/tools/sync_generated_tables_to_experiment_draft.py"])
    if not targets_complete(SAFEGUARD_TARGETS) or not targets_complete(QWEN_TARGETS):
        raise RuntimeError("coverage check failed after table generation")
    print("[pipeline] all guard outputs complete and generated tables refreshed", flush=True)


if __name__ == "__main__":
    main()
