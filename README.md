# Chain-of-Lure (CoL)

<p align="center">
  <em>Uncovering Hidden-Intent Vulnerabilities in Large Language Models via Narrative Red-Teaming</em>
</p>

<p align="center">
  <a href="https://github.com/ChangWenhan/chain-of-lure-official"><img alt="repo" src="https://img.shields.io/badge/repo-chain--of--lure-blue"></a>
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="python" src="https://img.shields.io/badge/python-3.8+-blue.svg">
  <img alt="status" src="https://img.shields.io/badge/status-paper--revision-orange">
</p>

---

> **TL;DR.** Most safety benchmarks hand a model a *directly* harmful request. Chain-of-Lure instead hides a harmful goal **inside a coherent narrative** — a scenario, assigned roles, guiding details, and staged questions — and asks a much harder question: can the model still recognize the harmful intent when it is **distributed across a story** rather than stated outright?

## What is Chain-of-Lure?

Chain-of-Lure (CoL) is a **black-box red-teaming evaluation framework** for testing *hidden-intent* safety. It does not try to be a stronger jailbreak. Instead, it measures whether target LLMs respond to the underlying adversarial intent of a prompt whose surface looks benign.

The name reflects two connected structures:

1. **A chain of questions** — context-specific questions embedded within a single narrative.
2. **A chain of revisions** — narrative rewrites performed across multiple rounds.

### How it works

**① Mission Transfer.** A generator LLM transforms an original harmful prompt $q_o$ into a structured **narrative lure chain** $L_0$, composed of:

- a scenario $s$,
- assigned roles $R$,
- guiding details $D$,
- context-specific questions $Q$.

The harmful request is never stated directly; its goal is expressed across the narrative and its questions. This tests whether the target recognizes harmful intent from the *complete context* rather than from explicit harmful wording.

**② Multi-round Narrative Rewriting.** If $L_0$ elicits an empty response or a keyword-matched refusal, a refiner LLM **revises the previous narrative** — updating scenario, roles, details, or question order — while keeping the original harmful goal $q_o$ as a fixed semantic reference. Each revised narrative is submitted as a **separate, independent black-box query** (no retained dialogue history, no target gradients, no exposed reasoning traces). This gives a more controlled alternative to independent random restart after every refusal.

**③ Multi-criterion Risk Evaluation.** Responses are judged along three complementary dimensions, using **separate judge models** rather than a single label:

| Dimension | Abbr. | Judge | Role |
|---|---|---|---|
| Targeted Harmfulness Score | $TS$ | GPT-4o-mini (1–5) | Semantic harmfulness w.r.t. original goal |
| Actionable ASR | ASR$_a$ | `gpt-oss-safeguard-20B` | Practical assistance (lower bound) |
| Policy-Risk ASR | ASR$_p$ | `Qwen3Guard-Gen-8B` | Unsafe **or** Controversial (upper bound) |

Reporting three criteria keeps distinct risk views visible: a response may violate policy (high ASR$_p$) without providing directly actionable assistance (lower ASR$_a$) — a distinction a single binary label would erase.

## Attack methods

CoL is provided in two generations, matching the paper's **CoL-single** and **CoL-multi**:

- **`method_b/` — CoL-single (single-turn).** A generator LLM produces one narrative lure chain per harmful goal and submits it once to the target. Entry point: `m2m_attack_multiThread.py`.
- **`method_c/` — CoL-multi (multi-turn, primary).** History-conditioned rewriting: when a narrative is refused, the refiner revises the *previous* narrative while keeping the original harmful goal as a fixed reference, and resubmits as an independent black-box query. Includes:
  - `reattack_multiThread.py` — main CoL-multi runner (parameterized, resumable).
  - `reattack_multiThread_random_restart.py` — equal-budget Random Restart baseline (each attempt generates a fresh narrative from the original goal, no history).
  - `reattack_multiThread_trace.py` — per-iteration PPL/TS trace collection.
  - `reattack_multiThread_lrm.py` — LRM-aware variant that captures victim reasoning.

## Repository contents

| Path | Purpose |
|---|---|
| `attack_story/` | Narrative templates & story generation (`story_maker_multi_threding.py`) |
| `method_b/` | **CoL-single** — single-turn narrative attack (`m2m_attack_multiThread.py`) |
| `method_c/` | **CoL-multi** (primary, multi-turn) + **Random Restart** baseline + trace & LRM variants |
| `evaluation/` | Three-judge evaluation pipeline (TS, Actionable-ASR, Policy-Risk-ASR) |
| `compare_methods/` | Baseline red-team methods: GCG, AutoDAN, DAN, DarkCite, DRA, MAC, TAP, AmpleGCG-plus |
| `defense/` | Defense-side evaluation |
| `data/` | AdvBench (520), GPTFuzz (100), HarmBench (+ category annotations), StrongREJECT |
| `REVISION/` | Revision-stage tooling and experiment scripts |

### Primary runners

```bash
python method_c/reattack_multiThread.py --help      # CoL-multi (history-conditioned rewriting)
python method_c/random_restart_multiThread.py --help # Random Restart (equal-budget baseline)
```

## Quick start

There is no build system or virtual environment manager — all scripts run directly with `python` from the repository root.

```bash
git clone https://github.com/ChangWenhan/chain-of-lure-official.git
cd chain-of-lure-official
cp .env.example .env   # then fill in your API keys
```

Run the main CoL-multi attack against a target:

```bash
python method_c/reattack_multiThread.py --help
```

## Configuration

Credentials live in `.env` (gitignored; see `.env.example`). Four separate API keys are used:

- `ATTACKER_*` — story generator (default: DeepSeek-V3 via DashScope)
- `HELPER_*` — story refiner/rewriter (default: DeepSeek-V3 via DashScope)
- `VICTIM_*` — target model under test (default: qwen-turbo via DashScope)
- `JUDGE_*` — harmfulness scoring (OpenAI API)

Victim models typically run via local **vLLM** on `http://127.0.0.1:8002/v1`.

## Datasets

| Dataset | Count | Use |
|---|---|---|
| `data/harmful_behaviors.csv` (AdvBench) | 520 | Main evaluation |
| `data/gptfuzz.csv` (GPTFuzz) | 100 | Main evaluation |
| `data/harmbench/` (HarmBench) | — | Data-level generalization + category analysis |
| `data/strongreject/` (StrongREJECT) | — | Additional evaluation |

## Experimental scope

- **7 target models** (open + closed): Vicuna-7B, Llama-3-8B, Llama-2-7B, Mistral-7B, GPT-3.5-Turbo, Doubao-1.5-pro, Qwen3-Turbo.
- **Main generator & refiner:** DeepSeek-V3-1226. Four alternative generators (Gemma-2-27B-it, Qwen2.5-Turbo, Gemma-3-1B, Qwen3-1.7B) are used only in the generator-sensitivity analysis and are **not pooled** with main results.
- **6 baselines:** AutoDAN, GCG, MAC (white-box); TAP, DRA, DarkCite (black-box). Multi-round methods are limited to 30 attempts per goal (including the initial submission).

## Identity conventions

Never join records by row position. Use `sample_id`, `task_id`, and `attack_instance_id` for all joins. Main CoL results use `attacker_model == deepseek-v3`; other generator outputs are sensitivity evidence and must not be pooled.

## Note

This repository contains source code and small reference datasets only. Raw experimental outputs, large result corpora, the paper manuscript, and reviewer comments are intentionally **not included**.

## Citation

If you find this work useful, please cite:

```bibtex
@article{chang2025chainoflure,
  title  = {Chain-of-Lure: Uncovering Hidden-Intent Vulnerabilities in Large Language Models via Narrative Red-Teaming},
  author = {Chang, Wenhan and Zhu, Tianqing and Zhao, Yu and Song, Shuangyong and Xiong, Ping and Zhou, Wanlei},
  note   = {IEEE Journal Manuscript (under review)}
}
```

## Acknowledgements

Wenhan Chang and Ping Xiong are with the School of Information Engineering, Zhongnan University of Economics and Law. Yu Zhao and Shuangyong Song are with TeleAI, Beijing. Tianqing Zhu and Wanlei Zhou are with the City University of Macau.
