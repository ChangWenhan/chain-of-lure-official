# Chain-of-Lure (CoL)

A red-teaming evaluation framework that constructs **narrative-obfuscated test cases from a hidden harmful goal**, then measures whether target models respond to the underlying adversarial intent rather than only to the benign-looking narrative surface.

CoL wraps a harmful goal into a plausible narrative scenario (the "lure"), sends the narrative to the target model, and — if the model refuses — iteratively rewrites the narrative conditioned on the previous one, up to a configurable attempt budget. Effectiveness is measured by a three-judge system rather than a single keyword check.

## Attack pipeline

1. **Story generation** (`attack_story/`) — Templates wrap harmful goals into narrative scenarios; `story_maker_multi_threding.py` generates stories from goals.
2. **Attack execution** (`method_c/`) — The narrative is sent to the victim model. A refusal check (`method_c/utils.py` → `test_prefixes`) detects rejection. On refusal, the helper model rewrites the story and retries, up to `--max-attempts`.
3. **Evaluation** (`evaluation/`) — Responses are judged by three dimensions:
   - **TS (Threat Score)** — `LLM_judge_statistic_optimization.py`, scored 1–5.
   - **Actionable-ASR** — `openai/gpt-oss-safeguard-20b` via vLLM (lower bound).
   - **Policy-risk-ASR** — `Qwen3Guard-Gen-8B` via vLLM (upper bound; "Controversial" counts as a violation).

## Attack methods (generations)

- **`method_a/`** — CoL-single: one-shot narrative generation + attack (`dry_attack.py`).
- **`method_b/`** — M2M (model-to-model) multi-turn attack variants.
- **`method_c/`** — **CoL-multi** (primary method): history-conditioned multi-turn attack where each rewrite is conditioned on the previous narrative.
  - `reattack_multiThread.py` — main CoL-multi runner, parameterized and resumable.
  - `random_restart_multiThread.py` — equal-budget independent Random Restart baseline (each attempt generates a fresh narrative from the original goal with no history).

## Quick start

All scripts run directly with `python` from the repository root — there is no build system or virtual environment manager.

```bash
git clone https://github.com/ChangWenhan/chain-of-lure-official.git
cd chain-of-lure-official
cp .env.example .env   # then fill in your API keys
```

Run the main CoL-multi attack:

```bash
python method_c/reattack_multiThread.py --help
```

Run the Random Restart baseline:

```bash
python method_c/random_restart_multiThread.py --help
```

## Configuration

Credentials live in `.env` (gitignored; see `.env.example`). Four separate API keys are used:

- `ATTACKER_*` — story generator (default: deepseek-v3 via DashScope)
- `HELPER_*` — story refiner/rewriter (default: deepseek-v3 via DashScope)
- `VICTIM_*` — target model under test (default: qwen-turbo via DashScope)
- `JUDGE_*` — harmfulness scoring (OpenAI API)

Victim models typically run via local vLLM on `http://127.0.0.1:8002/v1`.

## Data

- `data/harmful_behaviors.csv` — AdvBench (520 goals)
- `data/gptfuzz.csv` — GPTFuzz dataset
- `data/harmbench/` — HarmBench with category annotations for generalization analysis
- `data/strongreject/` — StrongREJECT evaluation data

## Baselines

Baseline / reference red-team methods live in `compare_methods/`: GCG, AutoDAN, DAN, DarkCite, DRA, MAC, TAP, AmpleGCG-plus.

## Repository layout

```
attack_story/      narrative templates and story generation
method_a/          CoL-single (one-shot)
method_b/          M2M multi-turn variants
method_c/          CoL-multi (primary) + Random Restart baseline
evaluation/        three-judge evaluation pipeline
compare_methods/   baseline red-team methods
defense/           defense-side evaluation
ablation_experiment/
tools/
data/              AdvBench, GPTFuzz, HarmBench, StrongREJECT
REVISION/          revision-stage tooling and experiment scripts
```

## Identity conventions

Never join records by row position. Use `sample_id`, `task_id`, and `attack_instance_id` for all joins. Main CoL results use `attacker_model == deepseek-v3`; other generator outputs are sensitivity evidence and must not be pooled.

## Note

This repository contains source code and small reference datasets only. Raw experimental outputs, large result corpora, paper drafts, and reviewer comments are intentionally not included.
