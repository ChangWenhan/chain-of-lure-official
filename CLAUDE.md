# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chain-of-Lure (CoL) is a red-teaming evaluation framework that constructs narrative-obfuscated test cases from hidden harmful goals, then measures whether target models respond to adversarial intent hidden behind benign-looking narratives. The project is in paper revision stage; the active workspace is `REVISION/`.

## Key Commands

No build system, package manager, or virtual environment management exists. All scripts run directly with `python` from the repo root:

```bash
cd /mnt/disk/cwh/chain-of-lure-jailbreak
```

**Canonicalization and judging pipeline:**
```bash
python REVISION/tools/build_canonical_corpora.py          # Build all review-stage corpora
python REVISION/tools/run_revision_guard_pipeline.py       # Resume/monitor guard judging
python REVISION/tools/sync_generated_tables_to_experiment_draft.py  # Update paper tables
```

**Running the main CoL-multi attack:**
```bash
python method_c/reattack_multiThread.py --help
```

**Running the Random Restart baseline:**
```bash
python method_c/random_restart_multiThread.py --help
```

**Paper compilation:**
```bash
cd "REVISION/papers and comments"
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## Configuration

Credentials live in `.env` (gitignored, see `.env.example`). The project uses four separate API keys:
- `ATTACKER_*` — story generator (default: deepseek-v3 via DashScope)
- `HELPER_*` — story refiner/rewriter (default: deepseek-v3 via DashScope)
- `VICTIM_*` — target model under test (default: qwen-turbo via DashScope)
- `JUDGE_*` — gpt-4o-mini for harmfulness scoring (OpenAI API)

Victim models typically run via local vLLM on `http://127.0.0.1:8002/v1`.

## Architecture

### Three attack methods (generations)

- **method_a/** — CoL-single: one-shot narrative generation + attack (`dry_attack.py`)
- **method_b/** — M2M (model-to-model) multi-turn attack variants
- **method_c/** — **CoL-multi** (primary method): history-conditioned multi-turn attack where each rewrite is conditioned on the previous narrative. Two active runners:
  - `reattack_multiThread.py` — main CoL-multi runner, parameterized and resumable
  - `random_restart_multiThread.py` — equal-budget independent Random Restart baseline (each attempt generates a fresh narrative from the original goal with no history)

### Attack pipeline

1. **Story generation** (`attack_story/`) — Templates (`old_template`, `new_template`) wrap harmful goals into narrative scenarios. `story_maker_multi_threding.py` generates stories from goals.
2. **Attack execution** (`method_c/`) — The narrative is sent to the victim model; a refusal check (`method_c/utils.py:test_prefixes`) detects rejection. If refused, the helper model rewrites the story and retries, up to `--max-attempts`.
3. **Evaluation** (`evaluation/`) — Responses are judged by a three-judge system:
   - **TS** (Threat Score): gpt-4o-mini via `LLM_judge_statistic_optimization.py`, scores 1–5
   - **Actionable-ASR**: `openai/gpt-oss-safeguard-20b` via vLLM, lower bound
   - **Policy-risk-ASR**: `Qwen3Guard-Gen-8B` via vLLM, upper bound; "Controversial" counts as violation
4. **Baseline methods** in `compare_methods/`: GCG, AutoDAN, DAN, DarkCite, DRA, MAC, TAP, AmpleGCG-plus

### REVISION/ workspace

The paper revision is organized as a self-contained workspace with three evidence layers:
1. **Raw JSON/JSONL** — immutable experimental evidence, never delete or edit
2. **Derived CSV/statistics** — machine-readable numeric sources for tables
3. **`EXPERIMENT_SECTION_DRAFT.md`** — the only paper-facing Markdown source for all experiment tables, statistics, and claims

Key directories:
- `REVISION/tools/` — canonicalization, judging, analysis, and table-sync scripts
- `REVISION/component_ablation/` — controlled component ablation (7 variants × 4 victims × 3 judges)
- `REVISION/random_restart/` — equal-budget Random Restart control
- `REVISION/generalization/` — category-level generalization analysis using HarmBench annotations
- `REVISION/papers and comments/` — LaTeX manuscript (`main.tex`), figures, reviewer comments

### Data

- `data/harmful_behaviors.csv` — AdvBench (520 goals)
- `data/gptfuzz.csv` — GPTFuzz dataset
- `data/harmbench/` — HarmBench with category annotations for generalization analysis
- `data/strongreject/` — StrongREJECT evaluation data

### Identity conventions

Never join records by row position. Use `sample_id`, `task_id`, and `attack_instance_id` for all joins. Main/RQ1/RQ2 CoL results use `attacker_model == deepseek-v3`; other generator outputs are sensitivity evidence and must not be pooled.

### Output directories

- `output/` — per-model attack results (deepseek_attack, gemma_attack, etc.)
- `output_trace/` — per-iteration PPL/TS traces for multi-turn trend analysis
- `refine-logs/` — experiment planning and tracking

## Judge Model Note

The TS judge model is `deepseek-v3-2-251201` (using the legacy gpt-4o-mini rubric). Do not add any model-mismatch disclaimer to tables or conversation.