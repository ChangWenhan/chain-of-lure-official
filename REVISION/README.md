# Revision Workspace

This directory contains the revision experiments, derived evidence, and the
paper-facing experiment draft for Chain-of-Lure.

## Start Here

| Path | Purpose |
|---|---|
| `EXPERIMENT_SECTION_DRAFT.md` | The only paper-facing Markdown source for experiment tables, statistical results, interpretations, and scoped claims. |
| `component_ablation/README.md` | Complete protocol and artifact map for the controlled component ablation on AdvBench and GPTFuzz. |
| `random_restart/README.md` | Complete protocol and artifact map for the equal-budget Random Restart control. |
| `generalization/README.md` | Completed category-level generalization analysis instantiated with HarmBench annotations, including radar figures, narrative-safety diagnosis, semantic-retention analysis, and claim boundaries. |
| `tools/README.md` | Canonicalization, judge, summarization, and table-synchronization commands. |
| `papers and comments/comments.txt` | Original reviewer comments. |
| `papers and comments/Latex/` | Manuscript source and retained figures. |

## Source-of-Truth Rules

The workspace uses three deliberately separate evidence layers:

1. Raw and canonical `.json`/`.jsonl` files are immutable experimental
   evidence. They must never be deleted or edited during documentation cleanup.
2. Derived `.csv` and paired-statistics `.jsonl` files are the machine-readable
   numeric sources for tables and statistical claims.
3. `EXPERIMENT_SECTION_DRAFT.md` is the only full paper-facing Markdown result
   source. This README provides routing, status, and compact claim boundaries;
   experiment READMEs describe how an experiment was run and point to their
   machine-readable evidence.

Generated Markdown summaries are temporary build artifacts. Canonicalization
and analysis scripts should normally emit JSONL/CSV only; a Markdown preview is
optional and should not be treated as a source of truth.

## Experiment Map

| Experiment | Protocol | Data and derived evidence |
|---|---|---|
| Main and baseline evaluation | `tools/README.md` | `review-stage/outputs/` |
| Component ablation | `component_ablation/README.md` | `component_ablation/structured_from_messages*/`, `vllm_outputs*/`, `guard_eval*/`, and `outputs/` |
| Equal-budget Random Restart | `random_restart/README.md` | `random_restart/outputs/` |
| Generalization and category heterogeneity | `generalization/README.md` | Frozen four-dataset metrics under `generalization/outputs/metrics/`; paper-facing mechanism analysis is category-level and uses HarmBench because it provides the required semantic labels under `generalization/outputs/data_analysis/` and `generalization/outputs/narrative_safety/`. |
| Recovered AdvBench CoL-multi/Mistral cell | This file and experiment draft | `missing_mistral/outputs/`; the original completed response file also remains under `output/deepseek_attack/` |
| Manuscript and reviewer material | `papers and comments/` | LaTeX, BibTeX, figures, and comments |

## Paper-Facing Experiment Narrative

The revised experiment section should present CoL as a red-teaming evaluation
framework, not as a stronger attack method. The coherent paper narrative is:
CoL constructs narrative-obfuscated test cases from a hidden harmful goal, then
measures whether target models respond to the underlying adversarial intent
rather than only to the benign-looking narrative surface.

| Paper order | Section role | Evidence to use | Supported claim boundary |
|---:|---|---|---|
| 5.1 | Experimental setup | `EXPERIMENT_SECTION_DRAFT.md`, `tools/README.md` | Define datasets, target models, generators/refiners, judges, TS, Actionable-ASR, Policy-risk-ASR, and cost metrics. Remove all Large Reasoning Model material. |
| 5.2 | Main red-team evaluation | Tables 1--3 in `EXPERIMENT_SECTION_DRAFT.md` | CoL exposes strong hidden-intent risk under the declared DeepSeek-V3 generator and three-judge evaluation; do not claim universal attack superiority. |
| 5.3 | Category-level generalization | `generalization/README.md`, radar PDFs, semantic-retention scatter plots | Category-dependent failures are visible in the categorized evaluation and are consistent with narrative sanitization plus semantic/task-contract drift; this is observational, not causal. |
| 5.4 | Iterative refinement | `random_restart/README.md`, paired statistics under `random_restart/outputs/` | Previous-narrative-conditioned rewriting improves over independent random restarts in the matched open-target setting; it is not target-response feedback. |
| 5.5 | Multi-turn risk evolution | retained PPL/TS trace artifacts referenced by the experiment draft | PPL and TS trends describe selected multi-turn trajectories; do not treat PPL as a validated camouflage metric. |
| 5.6 | Controlled component analysis | `component_ablation/README.md` and `component_ablation/outputs/` | Progressive decomposition is the strongest component-level driver; not every named narrative component is independently indispensable. |
| 5.7 | Generator sensitivity | generator tables in `EXPERIMENT_SECTION_DRAFT.md` | Generator choice changes the risk profile; other generators are sensitivity conditions, not pooled into the main CoL claim. |
| 5.8 | Framework efficiency | turn/token tables in `EXPERIMENT_SECTION_DRAFT.md` | Turns and prompt length are operational costs of constructing red-team tests; report variation rather than a single pooled cost. |
| 5.9--5.10 | Reserved | defense/case artifacts only after author selection | Keep as heading-only placeholders until the design/cases are finalized. |

This order should be treated as the writing spine for Prism. Each completed
subsection should end with its own insight and scope boundary; do not add a
standalone experiment-summary subsection.

## Generalization Result Summary

The generalization section should no longer be framed as a broad claim that CoL
uniformly improves across new benchmarks, and it should make clear that
HarmBench is only the labeled substrate for the category-level diagnosis. The
current evidence supports a more precise claim: **the categorized evaluation exposes strong category-level heterogeneity:
CoL works well when the generated narrative preserves visible harmful intent and
the requested task contract, but weakens when the narrative is sanitized or the
original behavior drifts into a safer proxy.** HarmBench is used here because it
has category annotations suitable for this diagnosis.

The main category table, instantiated with HarmBench annotations, is:

| Category | n | Narr-unsafe | TS | ASRa | ASRp | Goal→Narr cosine | ASRp-ASRa |
|---|---:|---:|---:|---:|---:|---:|---:|
| cybercrime_intrusion | 67 | 0.716 | 3.321 | 0.847 | 0.922 | 0.564 | 0.075 |
| illegal | 65 | 0.600 | 2.846 | 0.708 | 0.958 | 0.488 | 0.250 |
| chemical_biological | 56 | 0.804 | 3.214 | 0.679 | 0.991 | 0.518 | 0.312 |
| misinformation_disinformation | 65 | 0.246 | 2.488 | 0.654 | 0.788 | 0.565 | 0.134 |
| harmful | 22 | 0.318 | 1.659 | 0.307 | 0.716 | 0.482 | 0.409 |
| copyright | 100 | 0.170 | 1.807 | 0.258 | 0.662 | 0.540 | 0.404 |
| harassment_bullying | 25 | 0.160 | 1.310 | 0.210 | 0.580 | 0.406 | 0.370 |

Use this interpretation when writing the paper:

- `Narr-unsafe` is a standalone gpt-oss-safeguard classification of the initial
  narrative only; unsafe and controversial are counted together. It measures
  whether the narrative itself still contains visible risk.
- `Goal→Narr cosine` measures semantic retention between the original labeled
  goal and the generated narrative. Lower values are evidence of narrative
  intent drift, not proof of causality.
- `ASRp-ASRa` captures soft compliance: the response may be policy-risky while
  still failing to provide actionable completion.
- Category-level Spearman correlations are descriptive because there are only
  seven categories. The stronger statistical support comes from goal-level
  category-adjusted correlations over 400 labeled goals from HarmBench.

The supported paper-facing conclusion is:

> Category-level generalization gaps are partly explained by narrative semantic
> or intent drift, but the stronger framing is a two-factor mechanism:
> alignment-induced narrative sanitization reduces visible harmful intent, while
> semantic/task-contract drift weakens actionable fulfillment. These mechanisms
> are observationally supported by standalone narrative-safety labels, semantic
> retention scores, and their category-adjusted associations with TS/ASRa/ASRp.

Avoid claiming that this is a causal proof. The data support diagnosis and
interpretation; a causal repair claim would require regenerating narratives
under controlled anti-sanitization or intent-preservation constraints and
rerunning victims plus judges.

## Generalization Figures to Mention

The section should use standalone PDF subfigures assembled in LaTeX. Do not use
pre-composed 2x2 or 2x3 PDF panels for the manuscript body.

| Figure artifact | Recommended use |
|---|---|
| `generalization/outputs/data_analysis/harmbench_radar_{llama-2-7b,llama-3-8b,mistral-7b,vicuna-7b}.pdf` | Four standalone radar subfigures; assemble as a LaTeX 2x2 figure. |
| `generalization/outputs/data_analysis/harmbench_scatter_goal_narr_cosine_vs_{TS,ASRa,ASRp}.pdf` | First row of the selected 2x3 mechanism figure: semantic retention versus three outcomes. |
| `generalization/outputs/data_analysis/harmbench_scatter_narr_unsafe_vs_{TS,ASRa,ASRp}.pdf` | Second row of the selected 2x3 mechanism figure: standalone narrative-unsafe rate versus three outcomes. |

Recommended paper layout:

1. Put the four standalone radar PDFs first and assemble them as a 2x2 LaTeX
   subfigure. They show the core phenomenon: cyber/chemical/illegal are strong,
   while harassment/copyright/harmful are weak, and ASRp often remains higher
   than ASRa.
2. Follow with six standalone scatter PDFs assembled as a 2x3 LaTeX subfigure.
   This is the selected main-text scatter layout: two mechanism rows
   (`Goal→Narr cosine` and `Narrative-unsafe rate`) by three outcome columns
   (`TS`, `ASRa`, `ASRp`). Do not use the 3x3 layout in the main text; token
   length and old-dataset proximity are diagnostic controls, not the main
   mechanism story.
3. Keep the statistical audit in CSV/prose form. Do not regenerate or cite the
   old heatmap/legacy PNG diagnostics in the manuscript.

## Current Completion Status

- Main and baseline safeguard/Qwen3Guard outputs are retained under
  `review-stage/outputs/`.
- Component ablation is complete for seven variants, four open-source victims,
  and three judges: 14,560 AdvBench responses and 2,800 GPTFuzz responses.
- Random Restart is complete on AdvBench and GPTFuzz for the four open-source
  victims, with matched TS, Actionable-ASR, and Policy-risk-ASR evaluation.
- Generalization has been run and summarized. Frozen four-dataset metrics are
  retained, but the paper-facing analysis is now narrowed to a category-level
  diagnosis using HarmBench labels, four victim models, standalone
  narrative-safety classification, semantic-retention diagnostics, and
  radar/scatter figures.
- The previously missing AdvBench/DeepSeek/CoL-multi/Mistral group was measured
  on all 520 goals. No value is imputed.

## Maintenance Policy

- Keep scripts, JSON/JSONL evidence, CSV statistics, run summaries, prompt
  artifacts referenced by run summaries, manuscript sources, and figures.
- Runtime logs, `__pycache__`, LaTeX auxiliary files, and generated Markdown
  previews may be removed after completion is verified.
- Do not join records by row position. Use `sample_id`, `task_id`, and
  `attack_instance_id` as documented in `tools/README.md`.
- Main/RQ1/RQ2 CoL results use `attacker_model == deepseek-v3`; other generator
  outputs remain sensitivity evidence and must not be silently pooled.
