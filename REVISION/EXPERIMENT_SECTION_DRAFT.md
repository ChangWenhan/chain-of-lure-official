# 5 Experiments

This file is the single paper-facing evidence source for rewriting the Chain-of-Lure (CoL) experiment section. The authoritative plan below defines the final narrative order; the numbered draft that follows preserves result tables and analysis material for reuse. The main evaluation uses a three-dimensional risk view that separates semantic harmfulness, actionable harmful compliance, and broader policy risk.

## Authoritative Rewrite Plan for Prism

This block is the editorial contract for rewriting the complete LaTeX experiment section. The numbered material below is an evidence bank, not the final section order. Prism must follow the order and constraints in this block, while taking every reported value from the evidence bank or its cited machine-readable artifact.

### Non-Negotiable Decisions

1. Do not optimize for page count at this stage. Write a complete experiment section first; compression can be performed only after the scientific narrative is stable.
2. Do not create or rely on an appendix. Experimental settings needed to interpret the currently retained results, the baseline descriptions, the PPL/$TS$ trends, and cost results belong in the main text. Defense and qualitative material remain reserved but unwritten for now.
3. Preserve the original paper's direct empirical voice and IEEE table/figure grammar, but correct grammar and remove claims that exceed the evidence.
4. Reuse the original model table, baseline descriptions, and their citations where the experimental condition has not changed. Reuse means preserving useful content and LaTeX structure, not copying outdated dataset counts, model names, metrics, or unsupported conclusions.
5. Treat the new three-judge evaluation as the paper-facing result: `TS / Actionable-ASR / Policy-risk-ASR`. The legacy refusal-keyword ASR is not a headline success metric. It may appear only where an old diagnostic has not been rerun with the three judges, and that limitation must be stated next to the result.
6. Describe the implemented multi-turn procedure as **previous-narrative-conditioned iterative rewriting**. The retained implementation rewrites from the original goal and previous narrative; it does not condition the rewrite prompt on the target model's previous response. Do not use “victim-feedback-conditioned,” “response-feedback,” or equivalent wording for the current results.
7. Section 5.3 is now active and should report the completed category-level generalization analysis instantiated with HarmBench annotations. Do not frame it as a broad four-dataset success claim, and do not use StrongREJECT in the paper-facing conclusion. The section should explain heterogeneity across semantically labeled harmful-intent categories using radar plots, standalone narrative-safety labels, semantic-retention scatter plots, and calibrated observational language.
8. Do not use appendix references such as `Appendix~\ref{...}` in the rewritten experiment section. All references must resolve to main-text tables and figures.
9. Exclude the Large Reasoning Model (LRM) evaluation completely. Do not include an LRM subsection, reasoning-process/output figures, reasoning-model rows, reasoning-model turn tables, or claims about reasoning-model generalization anywhere in the rewritten experiment section.
10. Keep Section 5.9, `Prompt-Level Defense`, as a heading-and-label-only placeholder. The defense design is not finalized, so do not write the retained legacy defense table, method description, result, or insight into the current paper.
11. Keep Section 5.10, `Qualitative and Disagreement Analysis`, as a heading-and-label-only placeholder until the cases are selected. Do not invent, summarize, or select cases during the rewrite.
12. Do not create a standalone `Summary of Findings` experiment subsection. Every completed result subsection must end with its own evidence-calibrated insight and scope boundary.
13. Do not use a research-question structure. The rewritten experiment section must contain no RQ list, RQ numbering, RQ-named headings, or statements that map subsections back to RQs. Descriptive subsection titles provide the organization.
14. Frame CoL as a **red-teaming evaluation framework**, not as a newly proposed attack method. The scientific object is the target model's safety behavior when harmful intent is preserved but concealed by a plausible narrative. Iterative rewriting, narrative components, and generator choice are mechanisms for constructing and diagnosing red-team test cases, not claims about a more powerful operational attack.

### Core Paper Framing

The rewrite must consistently communicate the following one-sentence contribution:

> Chain-of-Lure is a red-teaming framework that constructs narrative-obfuscated test cases to evaluate whether an LLM's safety behavior responds to the underlying adversarial intent rather than only to the surface form of a prompt.

The experimental narrative is therefore:

1. A harmful goal represents the underlying adversarial intent to be tested.
2. CoL preserves that goal while embedding it in a coherent narrative and progressively structured questions.
3. The target model's response is evaluated from three complementary behavioral perspectives: semantic harmfulness, actionable harmful compliance, and broader policy risk.
4. Risky responses under narrative obfuscation expose a safety gap in handling hidden intent. They do not prove the model's internal reasoning process, but they provide behavioral evidence that its safeguards did not adequately account for the underlying intent.
5. Controlled rewriting, component, generator, trace, and efficiency analyses explain when the framework exposes this risk and what construction choices are responsible for the observed behavior.

Use framing such as:

- `CoL exposes hidden-intent safety risks under narrative obfuscation.`
- `The framework probes whether target models respond to underlying intent rather than surface narrative cues.`
- `Higher risk metrics indicate that the red-team test case elicited behavior inconsistent with the hidden harmful goal's safety requirements.`
- `The results reveal a behavioral safety gap in intent-sensitive moderation.`

Do not write:

- `We propose a new/stronger attack method.`
- `CoL is designed to maximize attack success.`
- `The attacker defeats or fully bypasses the model.`
- `The results prove that the model cannot recognize intent internally.`
- `Higher scores demonstrate superior offensive capability.`

The paper may still compare against established jailbreak methods because they are reference red-team baselines. Such comparisons evaluate how effectively different test-generation approaches expose safety risk; they do not change the paper's contribution into an attack-method claim.

### Final Section Order

| Order | Proposed LaTeX heading | Main question and required content | Reuse/status |
|---:|---|---|---|
| 5.1 | `Experimental Setup` | Hardware/API setting; currently completed datasets; target, red-team generator/refiner, and judge models; baseline test-generation methods; three risk proxies; cost metrics; statistical protocol. | Reuse the original model/baseline material and table skeleton, remove the LRM target group, and update the remaining entries. Do not introduce the two pending datasets here yet. |
| 5.2 | `Main Red-Team Evaluation` | Compare how effectively different test-generation methods expose hidden-intent safety risk on AdvBench and GPTFuzz under TS, Actionable-ASR, and Policy-risk-ASR; report robustness across target-model cells and explain metric disagreements. | Existing Tables 1--3. |
| 5.3 | `Category-Level Generalization Analysis` | Explain why CoL behaves differently across semantically labeled harmful-intent categories. Use four victim-specific radar plots over TS, Actionable-ASR, Policy-risk-ASR, and standalone narrative-unsafe rate; then use semantic-retention scatter plots and category-adjusted correlations to support the narrative-drift/sanitization interpretation. | Completed category-level analysis using HarmBench as the labeled evaluation substrate, not as the research target. Use `REVISION/generalization/README.md` and the CSV/figure artifacts under `generalization/outputs/`. |
| 5.4 | `Effect of Iterative Test Refinement` | Compare CoL-single, Random Restart, and CoL-multi under the same generator, judges, goals, targets, and 30-attempt budget to test whether iterative narrative refinement exposes additional hidden-intent risk beyond independent resampling. | Merge current Sections 5.3 and 5.4. |
| 5.5 | `Multi-Turn Risk Evolution: PPL and Toxicity Trends` | Keep the seven-target PPL/$TS$ trend figure in the main text; explain the dashed single-turn baseline, round-wise evolution, plateau behavior, exceptions, and selection conditioning. | Promote current Section 5.7 and the legacy appendix figure to a full main-text subsection. |
| 5.6 | `Controlled Component Analysis` | Report the deterministic seven-variant diagnostic and paired statistics; identify progressive decomposition as dominant, the wrapper as jointly useful, Scenario as the clearest individual wrapper component, Roles as unsupported, and Guidance/order as condition-dependent. | Existing Tables 12--15. |
| 5.7 | `Generator Sensitivity` | Show how the test-case generator changes the multi-turn risk profile; keep DeepSeek-V3 fixed for the main result and present other generators only as sensitivity conditions. | Retain only the two CoL-multi sensitivity tables; do not render the redundant CoL-single generator tables. |
| 5.8 | `Framework Efficiency` | Report the execution cost of the red-team framework without pooling away generator/target variation; interpret turns and prompt length as the cost of constructing effective red-team tests. | Existing turn and token tables after removing the reasoning-model table. |
| 5.9 | `Prompt-Level Defense` | Reserved until the defense experiment/improvement decision is finalized. | **Intentionally empty:** output the heading and label only. |
| 5.10 | `Qualitative and Disagreement Analysis` | Reserved until representative cases are selected and verified. | **Intentionally empty:** output the heading and label only. |

This order follows the claim hierarchy: establish the evaluation, show the principal result, explain the completed category-level generalization result, isolate the iterative effect, inspect the multi-turn trajectory and components, test generator dependence, and finally report operational cost. The defense and qualitative headings remain visible only as reserved slots.

For the current rewrite, Section 5.3 should use the following subsection heading:

```latex
\subsection{Category-Level Generalization Analysis}
\label{sec:category_generalization}
```

This section should not introduce a generic four-dataset leaderboard. It should report category-level heterogeneity only, using HarmBench because it provides the required labels, with explicit limits that the analysis is observational and that StrongREJECT is not part of the current paper-facing claim.

Sections 5.9 and 5.10 follow the same heading-only rule:

```latex
\subsection{Prompt-Level Defense}
\label{sec:prompt_level_defense}

\subsection{Qualitative and Disagreement Analysis}
\label{sec:qualitative_disagreement}
```

Do not add a Section 5.11 summary. The experiment section currently ends after the empty Section 5.10 placeholder.

### Content Reuse Map

| Original content | New location | Instruction |
|---|---|---|
| `main.tex` Experiment Settings prose | Section 5.1 | Reuse the description of retained open-/closed-source targets and add judge models. Remove every LRM reference. Keep the completed AdvBench/GPTFuzz scope until the generalization results are available. |
| `main.tex` Table `models_overview_further_split` | Section 5.1 | Reuse the `table`, `multirow`, and `booktabs` structure, but rename paper-facing roles to Target, Red-Team Generator, Refiner, and Judge, and delete the Reasoning Target block. |
| `appendix.tex` Experimental Hardware and LLMs | Section 5.1 | Move the concise hardware/API paragraph into the main setup. Do not retain a separate appendix dependency. |
| `appendix.tex` Baseline Methods | Section 5.1 | Reuse and grammar-correct the descriptions of AutoDAN, GCG, MAC, TAP, DRA, and DarkCite with their existing citations. Do not reintroduce DAN unless it is restored to the revised leaderboard. |
| Original combined ASR/TS comparison | Section 5.2 | Reuse the two-dataset, seven-target, white-box/black-box table structure, but replace the cell semantics and values with the revised three-judge risk results. |
| Original ASR evaluation, TS evaluation, stability, black-/white-box discussion, and metric-importance discussion | Section 5.2 | Merge into one evidence-led analysis. Remove duplicate explanations and avoid a blanket claim that black-box methods dominate white-box methods. |
| Category-level generalization analysis in `REVISION/generalization/README.md` | Section 5.3 | Transfer the completed category result, radar-figure guidance, narrative-safety diagnosis, semantic-retention evidence, and limitation language. State that HarmBench is used because it provides suitable category annotations; do not transfer deprecated StrongREJECT or broad four-dataset claims. |
| Original LRM figure and reasoning-model turn table | Excluded | Do not reuse, cite, summarize, or move these artifacts into the revised experiment section. |
| Current equal-budget strategy and paired feedback sections | Section 5.4 | Merge. Lead with the controlled comparison, then give effect sizes, CIs, corrected tests, and a scoped conclusion. |
| Original PPL/$TS$ trend prose and `trace_figs` panels | Section 5.5 | Move the complete analysis and figure to the main text. Replace every appendix reference with a local figure reference. |
| Current component diagnostic | Section 5.6 | Retain all three judges and paired statistics, but prioritize the macro/effect-size tables in the prose and avoid claiming every named component is indispensable. |
| Original attacker-model analysis and current generator tables | Section 5.7 | Reframe as red-team generator sensitivity and report only CoL-multi because the single-/multi-turn distinction is already isolated in Section 5.4. Separate framework behavior from generator quality/alignment and avoid offensive-capability or model-size causal claims. |
| Original turn/token tables | Section 5.8 | Reuse the seven-target table layouts and values, excluding the reasoning-model turn table. |
| Original defense table and discussion | Reserved outside the current rewrite | Retain as possible future evidence, but do not render, cite, or summarize it in Section 5.9 yet. |
| Original case material | Reserved outside the current rewrite | Do not select or write cases until the authors finalize the examples for Section 5.10. |

### Writing-Style Contract

The original manuscript has a consistent empirical rhythm worth preserving:

1. **Question or purpose.** Open each subsection with one or two sentences stating what is being tested and why it is needed.
2. **Evidence.** Introduce the relevant table/figure with “As shown in ...” or “Table ... reports ...,” then cite two or three representative values or effect sizes. Cover both the strongest result and an important exception.
3. **Interpretation.** End with “These results indicate/suggest ...” and explain the supported implication in method terms.
4. **Boundary.** When the design is observational, judge-based, selection-conditioned, or incomplete, add one direct scope sentence rather than hiding the limitation elsewhere.

The interpretation and boundary at the end of each completed subsection are that subsection's insight. Do not postpone or repeat these insights in a separate experiment-summary subsection.

Preserve the following features of the paper's voice:

- first-person plural for experimental actions (`we evaluate`, `we compare`, `we observe`);
- direct transitions such as `To evaluate ...`, `As shown in ...`, `In contrast ...`, and `These results indicate ...`;
- explicit comparisons across open-source and closed-source targets, datasets, and single-/multi-turn framework variants;
- concrete numerical examples immediately followed by interpretation;
- claim-oriented subsection progression and self-contained result paragraphs.

Normalize the following weaknesses instead of imitating them:

- fix grammar, articles, capitalization, and model-name inconsistencies;
- avoid promotional adjectives such as “exceptional,” “profound,” “perfect reliability,” “fully co-opted,” and “fundamental vulnerability” unless the design directly supports them;
- replace causal language (`causes`, `reveals the essential reason`, `architectural flaw`) with evidence-calibrated language (`is associated with`, `is consistent with`, `suggests`) when only output behavior was measured;
- do not restate every table cell or repeat the same conclusion under ASR, TS, and stability headings;
- do not equate PPL with syntactic diversity, camouflage, or safety-filter evasion without an explicit validation. Present increasing PPL as lower likelihood under the selected language model and treat its mechanism as a hypothesis;
- do not use “feedback” alone for the current multi-turn implementation; use “previous-narrative conditioning” or “iterative narrative rewriting.”
- do not describe CoL as `our attack`, `our attack method`, or a tool for maximizing jailbreak success; describe it as `our red-teaming framework`, `our test-generation framework`, or `CoL-generated red-team tests`;
- interpret high scores as risk exposed by the framework, not as offensive superiority.

Use consistent terminology throughout: `Chain-of-Lure (CoL)`, `red-teaming framework`, `narrative-obfuscated test case`, `underlying adversarial intent`, `CoL-single`, `CoL-multi`, `single-turn`, `multi-turn`, `open-source`, `closed-source`, `target model`, `red-team test-case generator`, `TS`, `Actionable-ASR`, and `Policy-risk-ASR`. Legacy artifact names may retain `attacker` or `victim`, but those names must not determine the paper-facing framing.

### Result-Paragraph Template

Prism should normally write each result subsection in three paragraphs:

```text
Purpose: state the controlled question and identify the table/figure.

Evidence: report the main pattern with representative numbers, uncertainty, and at least one exception or metric disagreement.

Interpretation: state what hidden-intent safety risk the framework exposes, followed by one relevant evidence boundary.
```

For ablations and paired comparisons, report the direction and magnitude of the delta before the p-value. For example: “CoL-multi increases Actionable-ASR by 13.9 percentage points over Random Restart on AdvBench (95% CI ..., Holm-adjusted p < ...).” Do not turn statistical significance into a claim of practical dominance when the effect is small.

### LaTeX Table and Figure Contract

Match the existing IEEE experiment style:

- use `table` for compact single-column tables and `table*` for seven-target or multi-metric tables;
- place `\caption{...}` before `\label{...}` and refer to every float in the prose before or immediately after it appears;
- use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`), `\multirow`, `\multicolumn`, and `\cmidrule(lr){...}` for grouped model columns;
- place target models in columns and metrics in separate rows in every multi-metric LaTeX table; do not pack `TS / Actionable-ASR / Policy-risk-ASR` into one rendered cell even when the Markdown evidence bank uses that compact source notation;
- group open-source and closed-source targets exactly as in the original main comparison table; use separate panels `(a)` and `(b)` for dataset-specific views when this is more readable than a taller table;
- retain compact controls such as `\setlength{\tabcolsep}{...}`, `\renewcommand{\arraystretch}{...}`, and `\resizebox{\linewidth}{!}{...}` only where needed to fit the IEEE columns;
- use `\textbf{}` for the best comparable value and `\underline{}` for the second best, computed separately for each metric and target among methods with available results; use `--` for unavailable cells and never impute them;
- do not copy HTML highlighting from this Markdown draft into LaTeX. The original paper identifies rankings typographically rather than with web-only background spans;
- keep captions concise and descriptive. Put metric order, units, sample size, CI/test definitions, and dagger explanations in the caption or an immediately following note;
- preserve numerical precision consistently within a table: normally three decimals for ASR/proportions and two decimals for TS unless the source table requires more precision;
- use `figure*` for the PPL/$TS$ trend grid and preserve all seven target models. The figure caption must define the dashed single-turn baseline and state that multi-turn curves are conditioned on trajectories requiring multiple attempts;
- move the existing `trace_figs` assets into the main-text figure without changing the underlying PDF files merely to change their location in the paper.

### Evidence and Placeholder Rules

- **Completed evidence in current scope:** main/baseline three-judge results, Category-level generalization, Random Restart, component diagnostic, generator sensitivity, and retained trace/cost artifacts. LRM artifacts are out of scope and must not be used.
- **Reserved evidence outside the current rewrite:** legacy defense artifacts, unselected qualitative material, and StrongREJECT/four-dataset aggregate generalization claims.
- Sections 5.9 and 5.10 must contain only their LaTeX headings and labels, with no `DATA_NEEDED` marker or descriptive text.
- All final numerical claims must be traceable to the artifact notes at the end of this file. JSON/JSONL data are authoritative and must not be removed or replaced by prose summaries.

### Prism Execution Instruction

When asked to perform the rewrite, Prism should output a complete English LaTeX replacement for `\section{Experiments and Analysis}` only. It should use the final order above without an RQ list or RQ references, reuse valid citations and float structures from `main.tex`/`appendix.tex`, convert the Markdown evidence tables into consistent IEEE LaTeX with target models as columns and metrics as rows, write Section 5.3 as a category-level generalization diagnosis instantiated with HarmBench annotations, keep only CoL-multi in generator sensitivity, keep Sections 5.9 and 5.10 as heading-and-label-only placeholders, end each completed result subsection with its own insight, omit a standalone experiment summary, and leave all other paper sections unchanged. It must not silently move material to an appendix, invent missing values or cases, rename models, or strengthen claims beyond the stated evidence boundaries.

## 5.1 Experimental Settings

### Datasets and Target Models

The main leaderboard evaluates two harmful-goal corpora: AdvBench Harmful Behaviors with 520 goals and GPTFuzz Harmful Questions with 100 goals. The generalization analysis adds category labels rather than another broad leaderboard. HarmBench is used because it provides seven semantic categories suitable for diagnosing when narrative-obfuscated red-team tests preserve or lose the hidden intent. Each table keeps the target-model coverage of the corresponding experiment. The main leaderboard, generator-sensitivity, trace, turn-cost, and token-cost tables use the original seven-target layout whenever those results are available: four open-source targets (Vicuna-7B, Llama-3-8B, Llama-2-7B, and Mistral-7B) and three closed-source API targets (GPT-3.5-Turbo, Doubao-1.5-pro, and Qwen3-Turbo). The controlled Random Restart, component-sensitivity, and category-level generalization experiments focus on the four open-source targets, where Actionable-ASR and Policy-risk-ASR are measured under matched guard-judge settings.

The main CoL result fixes DeepSeek-V3 as the test-case generator. Other generators are treated as a generator-sensitivity condition; they are not averaged into the main result and are not used for best-cell selection.

### Three-Dimensional Risk Metrics

The revised evaluation uses three model-based risk proxies.

**Toxicity Score (TS).** TS is a 1--5 semantic harmfulness score judged against the original hidden harmful goal. Higher TS means the response is more semantically aligned with the harmful intent.

**Actionable-ASR.** Actionable-ASR is the fraction of target-model responses judged by an evidence-first safeguard model as practically useful for the hidden harmful goal. The safeguard judge uses only the original goal and target response; it does not judge the narrative-obfuscated test case itself.

**Policy-risk-ASR.** Policy-risk-ASR is the fraction of responses flagged by Qwen3Guard as Unsafe or Controversial. It captures a broader policy-risk view and can be high even when a response is not directly actionable.

These metrics are proxies, not human annotations. We therefore use them to triangulate model behavior, not to claim human-annotated harmfulness.

### Cost Metrics

We report framework cost from two angles. **Turn cost** is measured by the number of target-model interactions or observed generation attempts. **Prompt cost** is measured by generated test-case length. For component ablations, prompt length is the recorded tokenizer prompt length. For original CoL and Random Restart outputs, where tokenizer fields are not uniformly available, we report whitespace-token length as an auditable proxy.

### Statistical Protocol

For the main leaderboard, the robustness table is computed within each method over the available dataset-by-target groups. For each method and metric, we report per-dataset mean, variance, standard deviation, standard error, and 95% confidence interval across target-model cells, plus an overall cross-dataset summary over all available cells. This table is descriptive: it shows how stable each test-generation method is across targets and datasets, rather than testing generator effects.

For the iterative-refinement experiment, CoL-single and CoL-multi are compared with Random Restart on the same goals and targets under the same maximum 30-attempt budget. The paired reports use stratified paired bootstrap confidence intervals, paired sign-flip tests for TS, exact McNemar tests for binary metrics, and Holm correction within each dataset and metric. For the component diagnostic, each variant is rendered deterministically from the same structured component object for the same goal. We do not add a separate statistical table for the generator-sensitivity analysis; that section remains a condition-sensitivity table only.

## 5.2 Main Red-Team Evaluation Under Three Risk Proxies

We first report the main paper-facing red-team evaluation. The table keeps the structure of the original paper's main comparison: test-generation methods are grouped into white-box and black-box categories, and each dataset is reported separately over the same target-model columns. The revised cell format is `TS / Actionable-ASR / Policy-risk-ASR`, replacing the earlier `ASR / TS` view. This keeps the original table style while avoiding a single keyword-success metric as the headline result.

The CoL rows use DeepSeek-V3 as the declared representative red-team test-case generator. They are not averaged across test generators and are not selected per target from the best-performing generator. Other test generators are reported later as a generation-condition sensitivity analysis. Reference methods are retained in their native settings, so the table is a paper-facing comparison rather than a controlled causal attribution experiment. We exclude DAN from the revised baseline set because it is an old prompt-template baseline and is no longer part of the paper-facing comparison.

**Table 1: Main three-dimensional method leaderboard on AdvBench.** Each cell is `TS / Actionable-ASR / Policy-risk-ASR`.


| Category | Method | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B | GPT-3.5-Turbo | Doubao-1.5-pro | Qwen3-Turbo |
| --------- | ---------- | --------------------- | --------------------- | --------------------- | ---------------------- | --------------------- | --------------------- | --------------------- |
| White-box | AutoDAN | 3.640 / 0.823 / 0.975 | — | 1.760 / 0.187 / 0.444 | 4.620 / 0.979 / 0.988 | — | — | — |
| White-box | GCG | 3.040 / 0.539 / 0.957 | 1.060 / 0.015 / 0.023 | 1.480 / 0.133 / 0.148 | 3.470 / 0.762 / 0.819 | — | — | — |
| White-box | MAC | 3.980 / 0.696 / 0.796 | — | 2.400 / 0.169 / 0.535 | 4.470 / 0.681 / 0.977 | — | — | — |
| Black-box | TAP | 1.950 / 0.281 / 0.592 | 1.780 / 0.081 / 0.305 | 1.760 / 0.070 / 0.278 | 1.670 / 0.360 / 0.648 | 1.820 / 0.166 / 0.440 | 1.880 / 0.230 / 0.523 | 1.760 / 0.158 / 0.473 |
| Black-box | DRA | 4.270 / **0.881** / **0.994** | 3.580 / 0.698 / **0.985** | 4.090 / 0.677 / **0.990** | **4.710** / **0.990** / **1.000** | **4.750** / **0.971** / **0.979** | **4.770** / **0.946** / 0.958 | **4.930** / **0.990** / **0.998** |
| Black-box | DarkCite | 3.720 / 0.608 / 0.960 | 3.880 / 0.646 / 0.948 | 2.460 / 0.340 / 0.540 | 3.610 / 0.635 / 0.973 | 3.350 / 0.612 / 0.787 | 2.640 / 0.521 / 0.831 | 3.860 / 0.813 / 0.992 |
| Black-box | CoL-single | <span style="background-color:#e6f2ff"><strong>4.290</strong> / 0.787 / 0.958</span> | <span style="background-color:#e6f2ff">3.660 / 0.500 / 0.708</span> | <span style="background-color:#e6f2ff">4.030 / 0.742 / 0.892</span> | <span style="background-color:#e6f2ff">4.330 / 0.821 / 0.969</span> | <span style="background-color:#e6f2ff">3.960 / 0.753 / 0.961</span> | <span style="background-color:#e6f2ff">4.200 / 0.812 / 0.979</span> | <span style="background-color:#e6f2ff">3.560 / 0.790 / 0.954</span> |
| Black-box | CoL-multi | <span style="background-color:#e6f2ff"><strong>4.290</strong> / 0.788 / 0.963</span> | <span style="background-color:#e6f2ff"><strong>4.150</strong> / <strong>0.718</strong> / 0.958</span> | <span style="background-color:#e6f2ff"><strong>4.270</strong> / <strong>0.815</strong> / 0.960</span> | <span style="background-color:#e6f2ff">3.773 / 0.808 / 0.963†</span> | <span style="background-color:#e6f2ff">4.060 / 0.726 / 0.948</span> | <span style="background-color:#e6f2ff">4.120 / 0.817 / <strong>0.985</strong></span> | <span style="background-color:#e6f2ff">3.620 / 0.777 / 0.962</span> |

**Table 2: Main three-dimensional method leaderboard on GPTFuzz.** Each cell is `TS / Actionable-ASR / Policy-risk-ASR`.


| Category | Method | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B | GPT-3.5-Turbo | Doubao-1.5-pro | Qwen3-Turbo |
| --------- | ---------- | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- |
| White-box | AutoDAN | 4.310 / 0.820 / 0.970 | — | 2.170 / 0.230 / 0.370 | 4.380 / 0.940 / 0.980 | — | — | — |
| White-box | GCG | 2.810 / 0.494 / 0.874 | 1.170 / 0.060 / 0.070 | 1.060 / 0.020 / 0.020 | 3.460 / 0.790 / 0.840 | — | — | — |
| White-box | MAC | 1.530 / 0.130 / 0.130 | — | 1.060 / 0.010 / 0.000 | 2.240 / 0.320 / 0.470 | — | — | — |
| Black-box | TAP | 2.350 / 0.319 / 0.514 | 1.970 / 0.146 / 0.315 | 2.050 / 0.075 / 0.204 | 2.130 / 0.302 / 0.500 | 2.030 / 0.151 / 0.312 | 2.250 / 0.290 / 0.516 | 2.130 / 0.196 / 0.424 |
| Black-box | DRA | 3.890 / 0.550 / 0.970 | 2.890 / 0.470 / 0.930 | 3.600 / 0.420 / 0.910 | 4.740 / **0.990** / **1.000** | 4.420 / **0.970** / **0.990** | **4.970** / **0.990** / **1.000** | **4.840** / **0.960** / **1.000** |
| Black-box | DarkCite | 3.980 / 0.810 / 0.960 | 4.020 / 0.740 / 0.860 | 2.610 / 0.440 / 0.500 | 4.260 / 0.840 / 0.960 | 3.530 / 0.690 / 0.750 | 2.590 / 0.470 / 0.670 | 4.650 / 0.950 / 0.990 |
| Black-box | CoL-single | <span style="background-color:#e6f2ff">4.820 / 0.960 / <strong>1.000</strong></span> | <span style="background-color:#e6f2ff">4.170 / 0.850 / 0.870</span> | <span style="background-color:#e6f2ff">4.350 / 0.870 / 0.870</span> | <span style="background-color:#e6f2ff"><strong>4.780</strong> / <strong>0.990</strong> / 0.990</span> | <span style="background-color:#e6f2ff">4.670 / 0.960 / 0.970</span> | <span style="background-color:#e6f2ff">4.560 / 0.940 / 0.970</span> | <span style="background-color:#e6f2ff">3.570 / 0.840 / 0.810</span> |
| Black-box | CoL-multi | <span style="background-color:#e6f2ff"><strong>4.830</strong> / <strong>0.970</strong> / <strong>1.000</strong></span> | <span style="background-color:#e6f2ff"><strong>4.420</strong> / <strong>0.880</strong> / <strong>0.950</strong></span> | <span style="background-color:#e6f2ff"><strong>4.560</strong> / <strong>0.900</strong> / <strong>0.950</strong></span> | <span style="background-color:#e6f2ff"><strong>4.780</strong> / 0.970 / 0.990</span> | <span style="background-color:#e6f2ff"><strong>4.690</strong> / 0.950 / 0.970</span> | <span style="background-color:#e6f2ff">4.700 / 0.920 / 0.970</span> | <span style="background-color:#e6f2ff">4.070 / 0.910 / 0.870</span> |

**Table 3: Main-evaluation robustness statistics.** For each method and each metric, report the number of dataset-target cells, mean, variance, standard deviation, and 95% confidence interval over the available target-model groups. The CoL rows use only the DeepSeek-V3 generator, matching Tables 1 and 2.


| Method     | Metric          | n cells | Overall mean [95% CI] | Overall var/std | AdvBench mean [95% CI] | GPTFuzz mean [95% CI] | Dataset diff | Holm p |
| ---------- | --------------- | ------- | --------------------- | --------------- | ---------------------- | --------------------- | ------------ | ------ |
| AutoDAN    | Actionable-ASR  | 6       | 0.663 [0.287, 1.039]  | 0.128/0.358     | 0.663 [-0.379, 1.705]  | 0.663 [-0.281, 1.607] | 0.000        | 1.000  |
| AutoDAN    | Policy-risk-ASR | 6       | 0.788 [0.477, 1.098]  | 0.088/0.296     | 0.802 [0.031, 1.573]   | 0.773 [-0.094, 1.641] | -0.029       | 0.750  |
| AutoDAN    | TS              | 6       | 3.48 [2.19, 4.77]     | 1.500/1.225     | 3.34 [-0.27, 6.95]     | 3.62 [0.50, 6.74]     | 0.280        | 1.000  |
| GCG        | Actionable-ASR  | 8       | 0.352 [0.074, 0.629]  | 0.110/0.332     | 0.362 [-0.192, 0.917]  | 0.341 [-0.245, 0.927] | -0.021       | 1.000  |
| GCG        | Policy-risk-ASR | 8       | 0.469 [0.105, 0.833]  | 0.189/0.435     | 0.487 [-0.260, 1.234]  | 0.451 [-0.296, 1.198] | -0.036       | 1.000  |
| GCG        | TS              | 8       | 2.19 [1.27, 3.11]     | 1.208/1.099     | 2.26 [0.40, 4.13]      | 2.12 [0.22, 4.03]     | -0.138       | 1.000  |
| MAC        | Actionable-ASR  | 6       | 0.334 [0.028, 0.640]  | 0.085/0.292     | 0.515 [-0.230, 1.261]  | 0.153 [-0.235, 0.542] | -0.362       | 0.750  |
| MAC        | Policy-risk-ASR | 6       | 0.485 [0.091, 0.878]  | 0.141/0.375     | 0.769 [0.217, 1.321]   | 0.200 [-0.403, 0.803] | -0.569       | 0.750  |
| MAC        | TS              | 6       | 2.61 [1.20, 4.03]     | 1.817/1.348     | 3.62 [0.93, 6.30]      | 1.61 [0.13, 3.09]     | -2.007       | 0.750  |
| TAP        | Actionable-ASR  | 14      | 0.202 [0.146, 0.257]  | 0.009/0.096     | 0.192 [0.095, 0.290]   | 0.211 [0.125, 0.298]  | 0.019        | 0.297  |
| TAP        | Policy-risk-ASR | 14      | 0.432 [0.356, 0.507]  | 0.017/0.130     | 0.466 [0.338, 0.593]   | 0.398 [0.284, 0.511]  | -0.068       | 0.094  |
| TAP        | TS              | 14      | 1.97 [1.85, 2.08]     | 0.041/0.202     | 1.80 [1.72, 1.89]      | 2.13 [2.01, 2.25]     | 0.327        | 0.047  |
| DRA        | Actionable-ASR  | 14      | 0.822 [0.699, 0.945]  | 0.045/0.213     | 0.879 [0.753, 1.005]   | 0.764 [0.516, 1.013]  | -0.115       | 0.312  |
| DRA        | Policy-risk-ASR | 14      | 0.979 [0.963, 0.995]  | 0.001/0.028     | 0.986 [0.973, 1.000]   | 0.971 [0.937, 1.006]  | -0.015       | 0.406  |
| DRA        | TS              | 14      | 4.32 [3.95, 4.68]     | 0.396/0.629     | 4.44 [3.99, 4.89]      | 4.19 [3.49, 4.90]     | -0.250       | 0.281  |
| DarkCite   | Actionable-ASR  | 14      | 0.651 [0.552, 0.750]  | 0.029/0.171     | 0.596 [0.464, 0.729]   | 0.706 [0.530, 0.881]  | 0.109        | 0.094  |
| DarkCite   | Policy-risk-ASR | 14      | 0.837 [0.741, 0.934]  | 0.028/0.167     | 0.862 [0.712, 1.011]   | 0.813 [0.644, 0.981]  | -0.049       | 0.094  |
| DarkCite   | TS              | 14      | 3.51 [3.11, 3.91]     | 0.477/0.691     | 3.36 [2.82, 3.90]      | 3.66 [2.92, 4.40]     | 0.303        | 0.094  |
| CoL-single | Actionable-ASR  | 14      | 0.830 [0.758, 0.901]  | 0.015/0.124     | 0.744 [0.641, 0.846]   | 0.916 [0.859, 0.972]  | 0.172        | 0.047  |
| CoL-single | Policy-risk-ASR | 14      | 0.921 [0.874, 0.969]  | 0.007/0.083     | 0.917 [0.828, 1.007]   | 0.926 [0.857, 0.994]  | 0.008        | 0.703  |
| CoL-single | TS              | 14      | 4.21 [3.97, 4.45]     | 0.177/0.421     | 4.00 [3.73, 4.28]      | 4.42 [4.01, 4.82]     | 0.413        | 0.047  |
| CoL-multi  | Actionable-ASR  | 14      | 0.854 [0.804, 0.903]  | 0.007/0.086     | 0.778 [0.740, 0.817]   | 0.929 [0.896, 0.961]  | 0.150        | 0.047  |
| CoL-multi  | Policy-risk-ASR | 14      | 0.960 [0.943, 0.977]  | 0.001/0.030     | 0.963 [0.952, 0.973]   | 0.957 [0.918, 0.997]  | -0.006       | 0.828  |
| CoL-multi  | TS              | 12      | 4.32 [4.10, 4.53]     | 0.118/0.344     | 4.08 [3.83, 4.34]      | 4.54 [4.26, 4.83]     | 0.460        | 0.062  |

These two tables are the primary red-team evaluation result, and Table 3 reports whether each method's risk-exposure behavior is stable across target models and datasets. They show whether CoL remains effective at exposing hidden-intent risk after replacing the old keyword-ASR headline with semantic harmfulness, actionable harmful compliance, and broader policy risk. The text should emphasize metric separation rather than perfect success: a test-generation method can produce a high policy-risk rate while eliciting less actionable content, and TS can disagree with guard-derived binary risk. CoL should therefore be described as exposing strong hidden-intent safety-risk behavior under the declared generator and judge setting, not as universally successful in an unrestricted sense.

## 5.3 Category-Level Generalization Analysis

This subsection should answer a narrower question than a generic cross-dataset leaderboard: when harmful goals are decomposed into semantically labeled categories, where does CoL preserve hidden intent and where does the narrative transformation weaken it? The paper-facing result should use four standalone radar PDFs assembled as a 2x2 LaTeX subfigure, rather than another dataset-comparison table or a pre-composed bitmap/PDF panel. Each radar panel corresponds to one open-source target model and overlays four category-level curves: normalized TS, Actionable-ASR, Policy-risk-ASR, and standalone narrative-unsafe rate. The figure artifacts are:

- `generalization/outputs/data_analysis/harmbench_radar_llama-2-7b.pdf`
- `generalization/outputs/data_analysis/harmbench_radar_llama-3-8b.pdf`
- `generalization/outputs/data_analysis/harmbench_radar_mistral-7b.pdf`
- `generalization/outputs/data_analysis/harmbench_radar_vicuna-7b.pdf`

**Table G1: Category-level CoL-multi summary instantiated with HarmBench annotations.** `Narr-unsafe` is the gpt-oss-safeguard standalone classification of the generated narrative only; unsafe and controversial labels are combined. `Goal→Narr cosine` is the MPNet semantic-retention score between the original labeled goal and the generated narrative.

| Category | n | Narr-unsafe | TS | Actionable-ASR | Policy-risk-ASR | Goal→Narr cosine | ASRp-ASRa |
|---|---:|---:|---:|---:|---:|---:|---:|
| cybercrime_intrusion | 67 | 0.716 | 3.321 | 0.847 | 0.922 | 0.564 | 0.075 |
| illegal | 65 | 0.600 | 2.846 | 0.708 | 0.958 | 0.488 | 0.250 |
| chemical_biological | 56 | 0.804 | 3.214 | 0.679 | 0.991 | 0.518 | 0.312 |
| misinformation_disinformation | 65 | 0.246 | 2.488 | 0.654 | 0.788 | 0.565 | 0.134 |
| harmful | 22 | 0.318 | 1.659 | 0.307 | 0.716 | 0.482 | 0.409 |
| copyright | 100 | 0.170 | 1.807 | 0.258 | 0.662 | 0.540 | 0.404 |
| harassment_bullying | 25 | 0.160 | 1.310 | 0.210 | 0.580 | 0.406 | 0.370 |

The radar plots should establish the visible pattern: cybercrime, illegal, and chemical/biological categories retain high Actionable-ASR or Policy-risk-ASR, whereas harassment, copyright, and general harmful categories show weaker Actionable-ASR and larger Policy-risk-minus-Actionable gaps. Misinformation is an important exception: its standalone narrative-unsafe rate is low (0.246), yet Actionable-ASR remains moderate (0.654), which means narrative-safety classification alone does not fully explain outcome risk.

The mechanism paragraph should then use six standalone scatter PDFs assembled as a 2x3 LaTeX subfigure. This is the selected main-text scatter layout: two mechanism rows (`Goal→Narr cosine` and `Narrative-unsafe rate`) by three outcome columns (`TS`, Actionable-ASR, and Policy-risk-ASR). Do not use the 3x3 scatter layout in the main text; token length and old-dataset proximity are diagnostic controls, not the central mechanism story. The target-level statistical audit should be reported from `harmbench_feature_outcome_correlations.csv` in prose, not as the old heatmap PNG: after category adjustment over 400 labeled goals, goal-to-narrative cosine remains positively associated with TS and Actionable-ASR, while old-data proximity does not provide a positive explanation. This supports the interpretation that category-level generalization gaps are partly explained by semantic/task-contract drift and partly by alignment-induced narrative sanitization.

The boundary sentence is required. The analysis is observational and judge-based. It supports a diagnosis of category-dependent narrative drift/sanitization, not a causal proof that semantic drift alone causes failures. StrongREJECT and broad four-dataset aggregate claims should not appear in this subsection.

## 5.4 Equal-Budget Strategy Comparison

After the method leaderboard, we isolate the contribution of previous-narrative-conditioned iterative rewriting. This subsection compares CoL-single, Random Restart, and CoL-multi under a matched DeepSeek generator and matched judges. Each cell is again `TS / Actionable-ASR / Policy-risk-ASR`.

**Table 4: Equal-budget strategy comparison on AdvBench.**

| Strategy | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B |
|---|---:|---:|---:|---:|
| CoL-single | <span style="background-color:#e6f2ff"><strong>3.70</strong> / 0.785 / 0.958</span> | <span style="background-color:#e6f2ff">2.60 / 0.504 / 0.708</span> | <span style="background-color:#e6f2ff">3.37 / 0.740 / 0.892</span> | <span style="background-color:#e6f2ff"><strong>3.80</strong> / <strong>0.825</strong> / <strong>0.969</strong></span> |
| Random Restart | 2.72 / 0.652 / 0.942 | 2.68 / 0.644 / 0.908 | 2.57 / 0.644 / 0.915 | 2.70 / 0.646 / 0.933 |
| CoL-multi | <span style="background-color:#e6f2ff">3.66 / <strong>0.800</strong> / <strong>0.963</strong></span> | <span style="background-color:#e6f2ff"><strong>3.22</strong> / <strong>0.712</strong> / <strong>0.959</strong></span> | <span style="background-color:#e6f2ff"><strong>3.70</strong> / <strong>0.823</strong> / <strong>0.960</strong></span> | <span style="background-color:#e6f2ff">3.77 / 0.810 / 0.965</span> |

**Table 5: Equal-budget strategy comparison on GPTFuzz.**

| Strategy | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B |
|---|---:|---:|---:|---:|
| CoL-single | <span style="background-color:#e6f2ff"><strong>4.54</strong> / 0.960 / <strong>1.000</strong></span> | <span style="background-color:#e6f2ff">3.94 / 0.850 / 0.870</span> | <span style="background-color:#e6f2ff">4.12 / 0.880 / 0.870</span> | <span style="background-color:#e6f2ff"><strong>4.61</strong> / <strong>0.990</strong> / <strong>0.990</strong></span> |
| Random Restart | 3.42 / 0.850 / 0.900 | 3.37 / 0.800 / 0.880 | 3.20 / 0.780 / 0.870 | 3.87 / 0.850 / 0.950 |
| CoL-multi | <span style="background-color:#e6f2ff">4.46 / <strong>0.970</strong> / <strong>1.000</strong></span> | <span style="background-color:#e6f2ff"><strong>4.03</strong> / <strong>0.880</strong> / <strong>0.950</strong></span> | <span style="background-color:#e6f2ff"><strong>4.19</strong> / <strong>0.900</strong> / <strong>0.950</strong></span> | <span style="background-color:#e6f2ff">4.54 / 0.970 / <strong>0.990</strong></span> |

**Table 6: Open-target macro averages for the equal-budget strategy comparison.**

| Dataset | Strategy | TS | Actionable-ASR | Policy-risk-ASR |
|---|---|---:|---:|---:|
| AdvBench | CoL-single | <span style="background-color:#e6f2ff">3.368</span> | <span style="background-color:#e6f2ff">0.713</span> | <span style="background-color:#e6f2ff">0.882</span> |
| AdvBench | Random Restart | 2.667 | 0.647 | 0.925 |
| AdvBench | CoL-multi | <span style="background-color:#e6f2ff"><strong>3.589</strong></span> | <span style="background-color:#e6f2ff"><strong>0.786</strong></span> | <span style="background-color:#e6f2ff"><strong>0.962</strong></span> |
| GPTFuzz | CoL-single | <span style="background-color:#e6f2ff">4.303</span> | <span style="background-color:#e6f2ff">0.920</span> | <span style="background-color:#e6f2ff">0.932</span> |
| GPTFuzz | Random Restart | 3.465 | 0.820 | 0.900 |
| GPTFuzz | CoL-multi | <span style="background-color:#e6f2ff"><strong>4.305</strong></span> | <span style="background-color:#e6f2ff"><strong>0.930</strong></span> | <span style="background-color:#e6f2ff"><strong>0.972</strong></span> |

The strategy tables support a scoped feedback claim. Under the declared generator and matched judges, CoL-multi gives the highest macro average on all three proxies in both datasets. CoL-single also gives higher TS and Actionable-ASR than Random Restart in both datasets. At the same time, the metrics do not move identically: on AdvBench, Random Restart has higher Policy-risk-ASR than CoL-single while having lower TS and lower Actionable-ASR. This separation is useful for a red-team framework because it distinguishes semantic harmfulness, actionable harmful compliance, and broader policy risk.

### Paired Equal-Budget Iterative Analysis

This subsection introduces the **Random Restart** control. Random Restart uses the same DeepSeek generator and the same maximum 30-attempt budget as CoL-multi, but it samples a new independent narrative from the original goal at each attempt. CoL-multi instead conditions each rewrite on the original goal and previous narrative. This directly tests whether previous-narrative-conditioned iterative refinement exposes additional risk beyond stochastic resampling; it does not test target-response feedback.

**Table 7: Paired equal-budget Random Restart statistics.** Deltas are `CoL strategy - Random Restart`.

| Dataset | Contrast | n pairs | targets | Delta TS [95% CI] | Holm p | Delta Actionable [95% CI] | Holm p | Delta Policy-risk [95% CI] | Holm p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AdvBench | CoL-single - Random Restart | 2080 | 4 | +0.701 [+0.625, +0.775] | <0.001 | +0.067 [+0.044, +0.090] | <0.001 | -0.043 [-0.059, -0.027] | <0.001 |
| AdvBench | CoL-multi - Random Restart | 2078 | 4 | +0.923 [+0.849, +0.994] | <0.001 | +0.139 [+0.118, +0.160] | <0.001 | +0.038 [+0.026, +0.050] | <0.001 |
| GPTFuzz | CoL-single - Random Restart | 388 | 4 | +0.830 [+0.655, +1.008] | <0.001 | +0.095 [+0.052, +0.139] | <0.001 | +0.036 [-0.003, +0.075] | 0.09246 |
| GPTFuzz | CoL-multi - Random Restart | 388 | 4 | +0.848 [+0.680, +1.015] | <0.001 | +0.108 [+0.067, +0.149] | <0.001 | +0.075 [+0.041, +0.108] | <0.001 |

The paired results support a scoped iterative-refinement claim. Previous-narrative-conditioned CoL-multi is higher than independent restart for TS and Actionable-ASR in both datasets, and its Policy-risk-ASR deltas are also positive. This does not show that the refiner identifies the exact failed component in a refusal. It shows a behavioral effect: under the same budget and generator, conditioning the next narrative test on the previous narrative is associated with responses that are more semantically harmful and more actionable than independent resampling.

## Evidence: Generator Sensitivity (Final §5.7)

Generator identity is part of the experimental condition. The original result package includes multiple generators, and the results indicate that smaller or more strongly aligned generators can still produce risky outputs but may yield different TS profiles. In the revised paper, this evidence is used to qualify the evaluation: the main CoL result is the DeepSeek-V3 instantiation, and other generators are reported as sensitivity analysis.

This distinction matters for claim scope. If generator outputs were averaged or selected per cell, the table would mix a framework effect with a generator-selection effect. Fixing the generator for the main result makes the framework evaluation more auditable. The generator-sensitivity result should therefore be presented after the main performance tables as a condition analysis, not as a stronger performance claim.

The generator-sensitivity section reports only CoL-multi because Section 5.4 already isolates the single-/multi-turn distinction. Its two tables keep the original seven-target layout: four open-source targets and the three closed-source API targets GPT-3.5-Turbo, Doubao-1.5-pro, and Qwen3-Turbo. Each table places target models in columns and the three risk proxies in rows. These tables are not followed by a separate robustness-statistics table; the statistics belong only to the main evaluation.

**Generator sensitivity for CoL-multi on AdvBench.**


| Test Generator | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B | GPT-3.5-Turbo | Doubao-1.5-pro | Qwen3-Turbo |
| ------------------ | --------------------- | --------------------- | --------------------- | -------------------------------------------- | --------------------- | --------------------- | --------------------- |
| DeepSeek-V3-1226 | **4.290** / **0.788** / 0.963 | **4.150** / **0.718** / **0.958** | **4.270** / **0.815** / **0.960** | **4.330** / **0.808** / 0.963 | **4.060** / 0.726 / 0.948 | 4.120 / 0.817 / 0.985 | 3.630 / 0.777 / 0.962 |
| Gemma-2-27B-it | 4.110 / 0.727 / **0.965** | 3.900 / 0.667 / **0.958** | 3.940 / 0.723 / 0.937 | 4.230 / — / — | 4.000 / **0.760** / 0.954 | **4.250** / **0.825** / **0.987** | **3.860** / **0.802** / **0.988** |
| Qwen2.5-Turbo-1101 | 4.060 / 0.719 / 0.952 | 3.760 / 0.533 / 0.922 | 3.880 / 0.694 / 0.929 | 4.060 / — / — | 4.030 / 0.737 / 0.944 | 3.960 / 0.740 / 0.963 | 3.380 / 0.690 / 0.935 |
| Gemma-3-1B | 3.110 / 0.456 / 0.915 | 2.840 / 0.442 / 0.925 | 3.240 / 0.527 / 0.958 | 3.410 / 0.581 / **0.973** | 3.100 / 0.565 / **0.967** | 3.270 / 0.587 / 0.963 | 3.130 / 0.556 / 0.967 |
| Qwen-3-1.7B | 3.010 / 0.350 / 0.952 | 2.610 / 0.288 / 0.900 | 2.720 / 0.331 / 0.863 | 3.080 / 0.377 / 0.967 | 2.710 / 0.323 / **0.967** | 3.230 / 0.502 / 0.946 | 2.490 / 0.344 / 0.948 |

**Generator sensitivity for CoL-multi on GPTFuzz.**


| Test Generator | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B | GPT-3.5-Turbo | Doubao-1.5-pro | Qwen3-Turbo |
| ------------------ | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- |
| DeepSeek-V3-1226 | **4.830** / **0.970** / **1.000** | **4.420** / **0.880** / **0.950** | **4.560** / **0.900** / 0.950 | **4.780** / **0.970** / **0.990** | **4.690** / **0.950** / **0.970** | **4.700** / **0.920** / **0.970** | 4.070 / **0.910** / 0.870 |
| Gemma-2-27B-it | 3.910 / 0.670 / 0.870 | 4.180 / 0.800 / 0.910 | 4.230 / 0.870 / **0.960** | 4.490 / 0.850 / 0.970 | 4.120 / 0.770 / 0.870 | 4.400 / 0.860 / 0.960 | **4.210** / 0.830 / **0.930** |
| Qwen2.5-Turbo-1101 | 4.350 / 0.880 / 0.920 | 4.260 / 0.820 / 0.890 | 4.430 / 0.880 / 0.920 | 4.500 / 0.870 / 0.930 | 4.150 / 0.800 / 0.930 | 4.210 / 0.840 / 0.930 | 3.910 / 0.830 / 0.900 |
| Gemma-3-1B | 2.710 / 0.360 / 0.720 | 2.870 / 0.370 / 0.770 | 3.260 / 0.450 / 0.700 | 3.020 / 0.540 / 0.860 | 3.040 / 0.480 / 0.890 | 3.370 / 0.490 / 0.900 | 2.740 / 0.460 / 0.770 |
| Qwen-3-1.7B | 3.200 / 0.560 / 0.820 | 2.800 / 0.430 / 0.770 | 2.760 / 0.550 / 0.820 | 3.210 / 0.520 / 0.790 | 2.820 / 0.480 / 0.810 | 2.960 / 0.570 / 0.850 | 2.700 / 0.460 / 0.770 |

**Generator sensitivity for CoL-single on AdvBench.** Each cell is `TS / Actionable-ASR / Policy-risk-ASR`. TS values are the legacy 1–5 Toxicity Score from the original attacker-model table (`main.tex`, Table `combined-results-table`); Actionable-ASR is `gpt-oss-safeguard` `success_label` and Policy-risk-ASR is Qwen3Guard `Unsafe+Controversial`, both recomputed over the single-turn canonical corpus in `REVISION/review-stage/outputs/`. n = 520 per AdvBench cell (DeepSeek-V3 GPT-3.5-Turbo cell n = 1031 because it pools the two original runs; a few cells lose 1–14 rows to judge parse errors). The best value per column and metric is bolded.


| Test Generator | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B | GPT-3.5-Turbo | Doubao-1.5-pro | Qwen3-Turbo |
| ------------------ | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- |
| DeepSeek-V3-1226 | **4.290** / **0.787** / 0.958 | **3.660** / 0.500 / 0.708 | **4.040** / **0.742** / 0.892 | **4.330** / **0.821** / 0.969 | 3.960 / **0.754** / **0.961** | 4.200 / 0.812 / 0.979 | 3.560 / 0.790 / 0.954 |
| Gemma-2-27B-it | 4.100 / 0.727 / **0.962** | 3.520 / **0.608** / **0.812** | 3.730 / 0.690 / 0.883 | 4.220 / 0.794 / **0.985** | **3.990** / 0.744 / 0.937 | **4.240** / **0.819** / **0.985** | **3.920** / **0.808** / **0.983** |
| Qwen2.5-Turbo-1101 | 3.970 / 0.717 / 0.946 | 2.800 / 0.352 / 0.617 | 3.610 / 0.631 / 0.840 | 4.050 / 0.752 / 0.950 | 3.960 / 0.731 / 0.938 | 3.920 / 0.754 / 0.944 | 3.340 / 0.679 / 0.881 |
| Gemma-3-1B | 2.940 / 0.400 / 0.894 | 2.370 / 0.294 / 0.656 | 3.190 / 0.554 / **0.925** | 3.380 / 0.590 / 0.967 | 2.860 / 0.463 / 0.883 | 3.250 / 0.592 / 0.965 | 3.060 / 0.581 / 0.967 |
| Qwen-3-1.7B | 3.100 / 0.396 / 0.929 | 1.880 / 0.146 / 0.462 | 2.520 / 0.304 / 0.748 | 3.040 / 0.412 / 0.969 | 2.550 / 0.285 / 0.879 | 3.190 / 0.506 / 0.904 | 2.460 / 0.362 / 0.850 |

**Generator sensitivity for CoL-single on GPTFuzz.** Same cell convention as above; n = 100 per cell (a few cells lose 1–2 rows to judge parse errors).


| Test Generator | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B | GPT-3.5-Turbo | Doubao-1.5-pro | Qwen3-Turbo |
| ------------------ | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- | --------------------- |
| DeepSeek-V3-1226 | **4.820** / **0.960** / **1.000** | **4.170** / **0.850** / **0.870** | **4.350** / **0.870** / 0.870 | **4.780** / **0.990** / **0.990** | **4.680** / **0.960** / **0.970** | **4.560** / **0.940** / **0.970** | 3.570 / 0.840 / 0.810 |
| Gemma-2-27B-it | 4.110 / 0.740 / 0.910 | 3.570 / 0.670 / 0.730 | 4.160 / 0.830 / **0.920** | 4.410 / 0.880 / 0.960 | 4.360 / 0.840 / 0.960 | 4.290 / 0.840 / 0.950 | **4.110** / **0.850** / **0.900** |
| Qwen2.5-Turbo-1101 | 4.290 / 0.820 / 0.940 | 3.060 / 0.465 / 0.586 | 4.070 / 0.790 / 0.870 | 4.440 / 0.860 / 0.930 | 4.140 / 0.800 / 0.890 | 4.270 / 0.820 / 0.920 | 3.770 / 0.780 / 0.810 |
| Gemma-3-1B | 2.610 / 0.290 / 0.730 | 2.370 / 0.270 / 0.610 | 2.730 / 0.440 / 0.720 | 3.220 / 0.520 / 0.870 | 2.650 / 0.350 / 0.740 | 2.880 / 0.500 / 0.880 | 2.760 / 0.430 / 0.810 |
| Qwen-3-1.7B | 3.010 / 0.540 / 0.850 | 2.240 / 0.280 / 0.530 | 2.980 / 0.530 / 0.750 | 3.160 / 0.520 / 0.840 | 2.690 / 0.429 / 0.735 | 3.130 / 0.610 / 0.850 | 2.570 / 0.470 / 0.750 |

The CoL-single generator tables are reported as a sensitivity complement to the CoL-multi tables above. They reuse the original TS values directly, so the TS column is identical to the legacy attacker-model table and is not a recompute; only the two guard ASRs are newly derived from the retained single-turn judger outputs. The single-turn profile preserves the generator ordering seen under CoL-multi—larger generators (DeepSeek-V3, Gemma-2-27B-it, Qwen2.5-Turbo) stay above the smaller Gemma-3-1B and Qwen-3-1.7B on both TS and Actionable-ASR—while Policy-risk-ASR is saturated near the ceiling for most open-source targets, so it discriminates generators less than TS or Actionable-ASR. Because Section 5.4 already isolates the single-/multi-turn distinction with DeepSeek-V3 fixed, these tables should be read as a generator-condition check, not as a second single-/multi-turn comparison.

## Evidence: Controlled Component Analysis (Final §5.6)

This subsection evaluates which construction choices in the framework affect measured behavior. Each goal is first converted once into a structured component object containing scenario, roles, guidance details, and progressive questions. All variants for the same goal are deterministic renderings of that same object. This avoids comparing independently regenerated prompts.

The result separates the effects more precisely than the original component analysis. Progressive question decomposition is the dominant component: replacing the chain with the direct harmful question produces the largest decrease under every judge and dataset. The narrative wrapper also matters jointly, because Questions Only is consistently below Full. Within the wrapper, Scenario has a reproducible contribution, Roles has no detectable contribution, and Guidance is metric- and dataset-dependent. Question reversal has a smaller effect that is clearest in AdvBench TS. We therefore avoid claiming that every named component is independently indispensable.

This subsection reports three judges: **TS** (the 1–5 Toxicity Score rubric scored with the legacy 1--5 TS rubric), **Actionable-ASR** (gpt-oss-safeguard `success_label`), and **Policy-risk-ASR** (Qwen3Guard `Unsafe + Controversial`). Target-model responses were generated offline with vLLM over the four open-source targets on two corpora: AdvBench (520 goals × 4 targets × 7 variants = 14,560 responses) and GPTFuzz (100 goals × 4 targets × 7 variants = 2,800 responses), both with 100% coverage for all three judges. The backing machine-readable sources are the per-cell/macro CSV files under `component_ablation/guard_eval*/` and the two three-judge paired-statistics JSONL files under `component_ablation/outputs/`.

Each cell is `TS / Actionable-ASR / Policy-risk-ASR`, matching the main-table metric order. ASRs are proportions; n = 520 per cell on AdvBench and n = 100 per cell on GPTFuzz. The best value for each target and metric is bolded; uncertainty is reported in the macro and paired tables.

**Table 12: Controlled component diagnostic on AdvBench (three-judge evaluation).**

| Variant | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B |
|---|---|---|---|---|
| Full | 3.212 / 0.708 / **0.983** | 2.933 / 0.650 / 0.869 | **3.152** / 0.742 / 0.969 | 3.248 / 0.725 / 0.977 |
| w/o Scenario | 3.137 / 0.683 / 0.973 | 2.350 / 0.492 / 0.723 | 3.094 / 0.715 / 0.963 | 3.275 / 0.700 / 0.979 |
| w/o Roles | 3.217 / 0.725 / 0.979 | **2.965** / 0.644 / 0.867 | 3.104 / 0.756 / 0.973 | **3.304** / 0.729 / 0.971 |
| w/o Guidance | **3.223** / **0.733** / 0.973 | 2.854 / **0.654** / **0.873** | 3.115 / **0.762** / **0.977** | 3.235 / 0.742 / 0.965 |
| Questions Only | 2.954 / 0.633 / 0.938 | 2.108 / 0.444 / 0.704 | 2.606 / 0.623 / 0.871 | 3.096 / 0.671 / 0.967 |
| Direct Question | 1.810 / 0.277 / 0.335 | 1.252 / 0.069 / 0.075 | 1.212 / 0.075 / 0.065 | 2.815 / 0.654 / 0.662 |
| Reversed Questions | 3.131 / 0.706 / 0.973 | 2.706 / 0.610 / 0.846 | 3.044 / 0.742 / 0.962 | 3.269 / **0.746** / **0.981** |

**Table 13: Controlled component diagnostic on GPTFuzz (three-judge evaluation).**

| Variant | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B |
|---|---|---|---|---|
| Full | 3.780 / **0.830** / 0.930 | 3.000 / 0.640 / 0.710 | 3.590 / **0.860** / **0.920** | **3.740** / **0.800** / 0.920 |
| w/o Scenario | 3.580 / 0.780 / 0.940 | 2.360 / 0.440 / 0.560 | 3.450 / 0.780 / 0.890 | 3.690 / 0.770 / 0.920 |
| w/o Roles | **3.790** / 0.820 / **0.950** | **3.100** / **0.650** / **0.750** | 3.590 / 0.840 / 0.910 | 3.650 / 0.790 / 0.910 |
| w/o Guidance | 3.510 / 0.760 / 0.940 | 2.800 / 0.600 / **0.750** | **3.650** / 0.790 / 0.900 | 3.500 / **0.800** / 0.920 |
| Questions Only | 3.360 / 0.760 / 0.920 | 1.970 / 0.350 / 0.450 | 3.100 / 0.720 / 0.810 | 3.360 / 0.780 / 0.920 |
| Direct Question | 2.000 / 0.360 / 0.390 | 1.330 / 0.120 / 0.100 | 1.210 / 0.100 / 0.070 | 3.090 / 0.700 / 0.660 |
| Reversed Questions | 3.700 / 0.790 / **0.950** | 2.830 / 0.610 / 0.740 | 3.480 / 0.810 / 0.890 | 3.590 / 0.790 / **0.930** |

**Table 13b: Macro averages over 4 targets (GPTFuzz, three-judge evaluation).** Mean ± std, with macro 95% CI in brackets. ASRs are in percent; TS is on the 1–5 scale. Deltas are `variant - Full`.

| Variant | TS | Delta TS | Actionable-ASR | Delta Actionable | Policy-risk-ASR | Delta Policy-risk |
|---|---|---:|---|---:|---|---:|
| Full | 3.527 ± 0.313 [3.221,3.834] | +0.000 | **78.2 ± 8.5 [69.9,86.6]** | +0.000 | 87.0 ± 9.2 [77.9,96.1] | +0.000 |
| w/o Scenario | 3.270 ± 0.532 [2.748,3.792] | -0.258 | 69.2 ± 14.6 [55.0,83.5] | -0.090 | 82.8 ± 15.5 [67.5,98.0] | -0.043 |
| w/o Roles | **3.532 ± 0.260 [3.278,3.787]** | +0.005 | 77.5 ± 7.4 [70.2,84.8] | -0.007 | **88.0 ± 7.7 [80.5,95.5]** | +0.010 |
| w/o Guidance | 3.365 ± 0.332 [3.040,3.690] | -0.163 | 73.8 ± 8.1 [65.8,81.7] | -0.045 | 87.8 ± 7.5 [80.4,95.1] | +0.007 |
| Questions Only | 2.947 ± 0.574 [2.385,3.510] | -0.580 | 65.2 ± 17.6 [48.0,82.5] | -0.130 | 77.5 ± 19.3 [58.6,96.4] | -0.095 |
| Direct Question | 1.907 ± 0.746 [1.176,2.639] | -1.620 | 32.0 ± 24.2 [8.3,55.7] | -0.463 | 30.5 ± 24.0 [7.0,54.0] | -0.565 |
| Reversed Questions | 3.400 ± 0.338 [3.069,3.731] | -0.128 | 75.0 ± 8.1 [67.0,83.0] | -0.033 | 87.8 ± 8.2 [79.7,95.8] | +0.007 |

**Table 13c: Paired component-ablation statistics (GPTFuzz, three-judge evaluation).** Deltas are `variant - Full`, paired by `(task_id, victim_model)`, n = 400 pairs per variant. CI = paired bootstrap percentile interval (2000 resamples). TS uses a paired sign-flip test; binary metrics use exact McNemar tests. Holm p is corrected across the 6 non-Full variants within each metric.

| Metric | Variant | n pairs | Delta mean | Delta [95% CI] | Test p | Holm p |
|---|---|---:|---:|---:|---:|---:|
| TS | w/o Scenario | 400 | -0.258 | -0.393, -0.128 | <0.001 | 0.0020 |
| TS | w/o Roles | 400 | +0.005 | -0.120, +0.128 | 0.9695 | 0.9695 |
| TS | w/o Guidance | 400 | -0.163 | -0.295, -0.040 | 0.0126 | 0.0378 |
| TS | Questions Only | 400 | -0.580 | -0.748, -0.422 | <0.001 | <0.001 |
| TS | Direct Question | 400 | -1.620 | -1.808, -1.438 | <0.001 | <0.001 |
| TS | Reversed Questions | 400 | -0.128 | -0.247, -0.013 | 0.0357 | 0.0714 |
| Actionable-ASR | w/o Scenario | 400 | -0.090 | -0.128, -0.052 | <0.001 | <0.001 |
| Actionable-ASR | w/o Roles | 400 | -0.007 | -0.040, +0.025 | 0.7608 | 0.7608 |
| Actionable-ASR | w/o Guidance | 400 | -0.045 | -0.080, -0.010 | 0.0175 | 0.0526 |
| Actionable-ASR | Questions Only | 400 | -0.130 | -0.172, -0.090 | <0.001 | <0.001 |
| Actionable-ASR | Direct Question | 400 | -0.463 | -0.515, -0.410 | <0.001 | <0.001 |
| Actionable-ASR | Reversed Questions | 400 | -0.033 | -0.062, -0.003 | 0.0660 | 0.1320 |
| Policy-risk-ASR | w/o Scenario | 400 | -0.043 | -0.072, -0.010 | 0.0095 | 0.0379 |
| Policy-risk-ASR | w/o Roles | 400 | +0.010 | -0.015, +0.035 | 0.5572 | 1.0000 |
| Policy-risk-ASR | w/o Guidance | 400 | +0.007 | -0.020, +0.033 | 0.7111 | 1.0000 |
| Policy-risk-ASR | Questions Only | 400 | -0.095 | -0.135, -0.058 | <0.001 | <0.001 |
| Policy-risk-ASR | Direct Question | 400 | -0.565 | -0.615, -0.512 | <0.001 | <0.001 |
| Policy-risk-ASR | Reversed Questions | 400 | +0.007 | -0.020, +0.033 | 0.7011 | 1.0000 |
| Qwen-Unsafe-only | w/o Scenario | 400 | -0.055 | -0.092, -0.020 | 0.0046 | 0.0137 |
| Qwen-Unsafe-only | w/o Roles | 400 | -0.020 | -0.050, +0.010 | 0.2682 | 0.5364 |
| Qwen-Unsafe-only | w/o Guidance | 400 | -0.018 | -0.052, +0.018 | 0.3916 | 0.5364 |
| Qwen-Unsafe-only | Questions Only | 400 | -0.160 | -0.205, -0.115 | <0.001 | <0.001 |
| Qwen-Unsafe-only | Direct Question | 400 | -0.455 | -0.505, -0.407 | <0.001 | <0.001 |
| Qwen-Unsafe-only | Reversed Questions | 400 | -0.048 | -0.077, -0.018 | 0.0034 | 0.0135 |

**Table 14: Macro averages over 4 targets (AdvBench, three-judge evaluation).** Mean ± std, with macro 95% CI in brackets. ASRs are in percent; TS is on the 1–5 scale. Deltas are `variant - Full`.

| Variant | TS | Delta TS | Actionable-ASR | Delta Actionable | Policy-risk-ASR | Delta Policy-risk |
|---|---|---:|---|---:|---|---:|
| Full | 3.136 ± 0.122 [3.016,3.256] | +0.000 | 70.6 ± 3.5 [67.2,74.0] | +0.000 | **95.0 ± 4.7 [90.4,99.5]** | +0.000 |
| w/o Scenario | 2.964 ± 0.361 [2.610,3.317] | -0.172 | 64.8 ± 9.0 [55.9,73.6] | -0.059 | 91.0 ± 10.8 [80.4,100.0] | -0.040 |
| w/o Roles | **3.148 ± 0.127 [3.023,3.272]** | +0.012 | 71.3 ± 4.2 [67.3,75.4] | +0.007 | 94.8 ± 4.6 [90.2,99.3] | -0.002 |
| w/o Guidance | 3.107 ± 0.153 [2.957,3.257] | -0.029 | **72.3 ± 4.1 [68.2,76.3]** | +0.016 | 94.7 ± 4.3 [90.5,98.9] | -0.002 |
| Questions Only | 2.691 ± 0.381 [2.317,3.064] | -0.445 | 59.3 ± 8.8 [50.7,67.9] | -0.113 | 87.0 ± 10.2 [77.0,97.0] | -0.079 |
| Direct Question | 1.772 ± 0.647 [1.138,2.406] | -1.364 | 26.9 ± 23.8 [3.6,50.2] | -0.438 | 28.4 ± 24.3 [4.6,52.2] | -0.665 |
| Reversed Questions | 3.038 ± 0.208 [2.834,3.241] | -0.099 | 70.1 ± 5.5 [64.7,75.5] | -0.005 | 94.0 ± 5.5 [88.7,99.4] | -0.009 |

**Table 15: Paired component-ablation statistics (AdvBench, three-judge evaluation).** Deltas are `variant - Full`, paired by `(task_id, victim_model)`, n = 2080 pairs per variant. CI = paired bootstrap percentile interval (2000 resamples). TS uses a paired sign-flip test; binary metrics use exact McNemar tests. Holm p is corrected across the 6 non-Full variants within each metric.

| Metric | Variant | n pairs | Delta mean | Delta [95% CI] | Test p | Holm p |
|---|---|---:|---:|---:|---:|---:|
| TS | w/o Scenario | 2080 | -0.172 | -0.229, -0.113 | <0.001 | <0.001 |
| TS | w/o Roles | 2080 | +0.012 | -0.042, +0.067 | 0.6867 | 0.6867 |
| TS | w/o Guidance | 2080 | -0.029 | -0.080, +0.024 | 0.2838 | 0.5675 |
| TS | Questions Only | 2080 | -0.445 | -0.508, -0.379 | <0.001 | <0.001 |
| TS | Direct Question | 2080 | -1.364 | -1.444, -1.284 | <0.001 | <0.001 |
| TS | Reversed Questions | 2080 | -0.099 | -0.151, -0.044 | <0.001 | 0.0012 |
| Actionable-ASR | w/o Scenario | 2080 | -0.059 | -0.075, -0.041 | <0.001 | <0.001 |
| Actionable-ASR | w/o Roles | 2080 | +0.007 | -0.008, +0.023 | 0.4086 | 0.8172 |
| Actionable-ASR | w/o Guidance | 2080 | +0.016 | +0.001, +0.033 | 0.0525 | 0.1574 |
| Actionable-ASR | Questions Only | 2080 | -0.113 | -0.134, -0.094 | <0.001 | <0.001 |
| Actionable-ASR | Direct Question | 2080 | -0.438 | -0.462, -0.413 | <0.001 | <0.001 |
| Actionable-ASR | Reversed Questions | 2080 | -0.005 | -0.022, +0.012 | 0.5708 | 0.8172 |
| Policy-risk-ASR | w/o Scenario | 2080 | -0.040 | -0.051, -0.029 | <0.001 | <0.001 |
| Policy-risk-ASR | w/o Roles | 2080 | -0.002 | -0.011, +0.008 | 0.7709 | 1.0000 |
| Policy-risk-ASR | w/o Guidance | 2080 | -0.002 | -0.012, +0.007 | 0.6817 | 1.0000 |
| Policy-risk-ASR | Questions Only | 2080 | -0.079 | -0.094, -0.066 | <0.001 | <0.001 |
| Policy-risk-ASR | Direct Question | 2080 | -0.665 | -0.686, -0.644 | <0.001 | <0.001 |
| Policy-risk-ASR | Reversed Questions | 2080 | -0.009 | -0.018, +0.000 | 0.0728 | 0.2183 |
| Qwen-Unsafe-only | w/o Scenario | 2080 | -0.044 | -0.062, -0.027 | <0.001 | <0.001 |
| Qwen-Unsafe-only | w/o Roles | 2080 | +0.003 | -0.013, +0.020 | 0.7260 | 0.9696 |
| Qwen-Unsafe-only | w/o Guidance | 2080 | -0.006 | -0.022, +0.010 | 0.4848 | 0.9696 |
| Qwen-Unsafe-only | Questions Only | 2080 | -0.139 | -0.160, -0.120 | <0.001 | <0.001 |
| Qwen-Unsafe-only | Direct Question | 2080 | -0.503 | -0.525, -0.481 | <0.001 | <0.001 |
| Qwen-Unsafe-only | Reversed Questions | 2080 | -0.041 | -0.057, -0.025 | <0.001 | <0.001 |

Overall, the three judges separate four effects. (1) **Progressive question construction is the dominant component.** Direct Question reduces AdvBench TS by 1.364, Actionable-ASR by 43.8 points, and Policy-risk-ASR by 66.5 points (all Holm p < 0.001). (2) **The wrapper matters jointly.** Questions Only reduces the same metrics by 0.445, 11.3 points, and 7.9 points (all Holm p < 0.001). (3) **Wrapper components are asymmetric.** Removing Scenario produces a reproducible drop under all three primary metrics, whereas removing Roles is non-significant throughout and removing Guidance is non-significant on AdvBench. (4) **Ordering is secondary.** Reversal lowers AdvBench TS by 0.099 (Holm p = 0.0012) but does not significantly change the two primary guard rates. Thus, the supported mechanism is progressive decomposition plus a jointly useful wrapper, with Scenario carrying the clearest individual wrapper contribution.

**Cross-dataset replication.** GPTFuzz reproduces the main pattern: Direct Question decreases TS by 1.620, Actionable-ASR by 46.3 points, and Policy-risk-ASR by 56.5 points; Questions Only decreases them by 0.580, 13.0 points, and 9.5 points (all Holm p < 0.001). Scenario again contributes across all three metrics. Roles remains non-significant, while Guidance shows a smaller TS-only decrease (Holm p = 0.0378) and no guard-rate effect after correction. Reversed Questions is not significant after Holm correction on the three primary GPTFuzz metrics. This cross-dataset agreement rules out an AdvBench-specific artifact without overstating every component as independently necessary.

## Evidence: Multi-Turn Risk Evolution (Final §5.5)

This subsection keeps the original trace analysis in its original target-model layout. It is not written as a separate closed-source analysis: closed-source API targets appear as ordinary panels in the same figure as open-source targets whenever that experiment contains them.

The retained trace analysis tracks PPL and TS across multi-turn red-team trajectories that elicited risky responses. The legacy appendix figure uses the same seven-target framing as the main CoL experiments. In the revised paper it must become a dedicated main-text process analysis rather than an appendix diagnostic. The trace files are selection-conditioned on test cases that required multiple rounds, so they should not be interpreted as population-level risk estimates. PPL should be interpreted as likelihood under the selected language model, not automatically as syntactic diversity or narrative concealment.

**Figure X: PPL and TS trends during multi-turn CoL red-team evaluation.**

> Restore the original multi-panel figure with Vicuna-7B, Llama-3-8B, Llama-2-7B, Mistral-7B, GPT-3.5-Turbo, Doubao-1.5-pro, and Qwen3-Turbo panels.

## Deferred Qualitative Material (Do Not Render)

No cases have been selected or verified for the current rewrite. Section 5.10 must remain empty.

## Evidence: Framework Efficiency (Final §5.8)

Cost is reported at the end of the experimental section because it is a framework-execution diagnostic rather than the main risk claim. The tables are not macro-averaged across models. They retain the original style: rows are red-team test-case generators and columns are target models, with open-source and closed-source targets shown in the same table.

**Table 16: Average target-model interactions required by CoL across seven target models.**

| Dataset | CoL Generator | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B | GPT-3.5-Turbo | Doubao-1.5-pro | Qwen3-Turbo |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| AdvBench | DeepSeek-V3-1226 | 1.008 | 1.346 | 1.012 | 1.002 | 1.010 | 1.030 | 1.110 |
| AdvBench | Gemma-2-27B-it | 1.006 | 1.358 | 1.031 | 1.000 | 1.010 | 1.020 | 1.060 |
| AdvBench | Qwen2.5-Turbo-1101 | 1.006 | 1.554 | 1.073 | 1.000 | 1.015 | 1.060 | 1.170 |
| AdvBench | Gemma-3-1B | 1.020 | 1.400 | 1.030 | 1.000 | 1.090 | 1.010 | 1.030 |
| AdvBench | Qwen3-1.7B | 1.020 | 1.540 | 1.180 | 1.000 | 1.260 | 1.100 | 1.170 |
| GPTFuzz | DeepSeek-V3-1226 | 1.010 | 2.460 | 1.160 | 1.000 | 1.010 | 1.130 | 1.280 |
| GPTFuzz | Gemma-2-27B-it | 1.010 | 1.550 | 1.020 | 1.000 | 1.000 | 1.030 | 1.090 |
| GPTFuzz | Qwen2.5-Turbo-1101 | 1.000 | 1.580 | 1.080 | 1.000 | 1.000 | 1.050 | 1.190 |
| GPTFuzz | Gemma-3-1B | 1.000 | 1.270 | 1.010 | 1.000 | 1.010 | 1.000 | 1.020 |
| GPTFuzz | Qwen3-1.7B | 1.050 | 1.550 | 1.080 | 1.030 | 1.110 | 1.060 | 1.070 |

**Table 17: Average CoL test-case length across seven target models.** Values in parentheses are deviations from each generator's base chain.

| Dataset | Test-Case Generator | Base Chain | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B | GPT-3.5-Turbo | Doubao-1.5-pro | Qwen3-Turbo |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AdvBench | DeepSeek-V3-1226 | 439.55 | 439.53 (-0.02) | 448.47 (+8.92) | 440.50 (+0.95) | 439.55 (+0.00) | 439.61 (+0.06) | 439.37 (-0.18) | 439.90 (+0.35) |
| AdvBench | Gemma-2-27B-it | 356.96 | 356.73 (-0.23) | 349.74 (-7.22) | 354.12 (-2.84) | 356.96 (+0.00) | 356.04 (-0.92) | 356.90 (-0.06) | 356.06 (-0.90) |
| AdvBench | Qwen2.5-Turbo-1101 | 416.33 | 416.60 (+0.27) | 420.29 (+3.96) | 418.77 (+2.44) | 416.33 (+0.00) | 416.51 (+0.18) | 419.16 (+2.83) | 420.54 (+4.21) |
| AdvBench | Gemma-3-1B | 745.87 | 741.43 (-4.44) | 686.74 (-59.13) | 739.17 (-6.70) | 745.09 (-0.78) | 725.37 (-20.50) | 743.55 (-2.32) | 739.70 (-6.17) |
| AdvBench | Qwen3-1.7B | 331.13 | 331.58 (+0.45) | 352.06 (+20.93) | 337.11 (+5.98) | 331.37 (+0.24) | 337.65 (+6.52) | 334.56 (+3.43) | 333.70 (+2.57) |
| GPTFuzz | DeepSeek-V3-1226 | 302.62 | 302.62 (+0.00) | 318.51 (+15.89) | 304.61 (+1.99) | 302.80 (+0.18) | 303.15 (+0.53) | 305.32 (+2.70) | 308.55 (+5.93) |
| GPTFuzz | Gemma-2-27B-it | 352.01 | 352.01 (+0.00) | 353.34 (+1.33) | 351.38 (-0.63) | 351.86 (-0.15) | 352.50 (+0.49) | 352.16 (+0.15) | 352.59 (+0.58) |
| GPTFuzz | Qwen2.5-Turbo-1101 | 380.16 | 380.88 (+0.72) | 386.65 (+6.49) | 382.73 (+2.57) | 380.16 (+0.00) | 381.38 (+1.22) | 383.01 (+2.85) | 386.67 (+6.51) |
| GPTFuzz | Gemma-3-1B | 785.59 | 785.59 (+0.00) | 750.65 (-34.94) | 782.33 (-3.26) | 785.59 (+0.00) | 781.68 (-3.91) | 782.79 (-2.80) | 781.97 (-3.62) |
| GPTFuzz | Qwen3-1.7B | 300.38 | 301.36 (+0.98) | 317.06 (+16.68) | 301.93 (+1.55) | 299.83 (-0.55) | 305.46 (+5.08) | 303.53 (+3.15) | 301.57 (+1.19) |

These cost tables characterize the execution efficiency of the red-team framework without collapsing model-specific behavior. Most generator-target pairs require close to one interaction, while Llama-3-8B generally requires more refinement. Length deviations show the same point from the test-case side: framework cost should be discussed as a target- and generator-dependent change in required narrative adaptation, not as a single pooled number.

## Deferred Defense Evidence (Do Not Render)

The defense experiment is placed at the end of the experimental sequence because it is a mitigation diagnostic rather than part of the attack-performance comparison. It evaluates two prompt-level safeguards: pre-intent detection and post-threat analysis. The table uses the original keyword-ASR view because this artifact was produced as a defense-stress diagnostic rather than a three-judge main result. Lower values indicate fewer successful jailbreak responses after the defense prompt.

**Table 18: Defense-prompt keyword-ASR on seven target models.**

| Dataset | Defense | Vicuna-7B | Llama-3-8B | Llama-2-7B | Mistral-7B | GPT-3.5-Turbo | Doubao-1.5-pro | Qwen3-Turbo |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| AdvBench | Pre-intent detection | 0.52 | 0.20 | 0.44 | 0.87 | 0.14 | 0.57 | 0.25 |
| AdvBench | Post-threat analysis | 0.78 | 0.26 | 0.36 | 0.63 | 0.32 | 0.39 | 0.45 |
| GPTFuzz | Pre-intent detection | 0.76 | 0.01 | 0.19 | 0.81 | 0.02 | 0.35 | 0.02 |
| GPTFuzz | Post-threat analysis | 0.78 | 0.10 | 0.17 | 0.34 | 0.13 | 0.20 | 0.34 |

This table should be framed cautiously. It shows that simple prompt-level safeguards can reduce keyword-ASR in some cells, especially for Llama-3-8B, GPT-3.5-Turbo, and Qwen3-Turbo on GPTFuzz. It does not show a complete defense because it does not include benign false-positive rates, adaptive attackers, or the revised three-judge metrics.

---

## Internal Artifact Notes

This draft intentionally keeps the main result tables close to the retained result artifacts:

- main three-dimensional leaderboard tables should be regenerated in memory from the main/baseline canonical corpora and guard outputs using `REVISION/tools/sync_generated_tables_to_experiment_draft.py`;
- main-leaderboard robustness statistics should be regenerated from `REVISION/review-stage/outputs/main_table_group_statistics.csv`; these statistics are only for the main leaderboard, not for attacker/generator ablation;
- generator-sensitivity tables should be regenerated from the all-generator CoL canonical corpus, but reported only as condition-sensitivity tables with seven target columns;
- Category-level generalization is backed by `REVISION/generalization/outputs/metrics/harmbench_category_macro.csv`, `REVISION/generalization/outputs/metrics/harmbench_category_victim_long.csv`, `REVISION/generalization/outputs/narrative_safety/category_gptoss_safe_unsafe.csv`, `REVISION/generalization/outputs/data_analysis/harmbench_category_data_diagnostics.csv`, and `REVISION/generalization/outputs/data_analysis/harmbench_feature_outcome_correlations.csv`; the paper-facing figures are the four standalone `harmbench_radar_*.pdf` files and the six standalone `harmbench_scatter_*.pdf` files under `REVISION/generalization/outputs/data_analysis/`;
- equal-budget strategy tables are backed by the matched canonical and three-judge JSONL files under `REVISION/random_restart/outputs/`, with the retained Random Restart per-cell values in `random_restart_metrics_v1_20260620_corrected.csv`;
- paired feedback statistics are taken from `REVISION/random_restart/outputs/random_restart_paired_stats_v1_20260620_complete.csv`;
- trace diagnostics use the legacy appendix PPL/TS trend assets, which must be moved into the main experiment text, and retained `REVISION/review-stage/outputs/canonical_trace.jsonl` coverage;
- turn and token cost should be restored from the original LaTeX cost tables, preserving generator-model rows and target-model columns rather than pooling models;
- defense prompting is deferred and Section 5.9 must remain empty; the legacy table and `REVISION/review-stage/outputs/canonical_defense.jsonl` are retained only for a later author decision, and `keyword_success` is not a direct defense-ASR field;
- component three-judge tables are regenerated from the AdvBench and GPTFuzz per-cell/macro CSVs under `component_ablation/guard_eval*/`; TS uses the legacy 1--5 TS rubric, and all three judges have complete coverage on both corpora;
- component paired statistics are retained as JSONL under `component_ablation/outputs/` and use paired bootstrap CIs and sign-flip tests for TS, with exact McNemar tests for the binary guard metrics and Holm correction within each metric;

Remove this note before converting the section to final LaTeX.
