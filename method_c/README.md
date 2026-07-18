# Method C Runners

| File | Status | Purpose |
|---|---|---|
| `reattack_multiThread.py` | active | History-conditioned CoL-multi runner. Parameterized, resumable, and stable-indexed; `--workers 1` also covers single-worker execution. |
| `random_restart_multiThread.py` | active | Equal-budget independent Random Restart control. |
| `reattack_multiThread_trace.py` | retained | Legacy per-iteration trace collection used for PPL and TS trend analysis. Do not delete while trace figures remain in the paper. |
| `reattack_multiThread_lrm.py` | active | LRM-aware variant that captures victim reasoning (`reasoning_content`) alongside the final output. Use `--victim-enable-thinking` for vLLM / Qwen3 thinking mode. |
| `utils.py` | active | Shared refusal phrases and rewrite prompts. |

The obsolete hard-coded `reattack.py` and duplicate `reattack_singleThread.py` runners were removed. API keys must be supplied through environment variables and must not be committed to source files.

## Switching the LRM Target API

`reattack_multiThread_lrm.py` calls the target/victim model through the OpenAI Python SDK. Any OpenAI-compatible endpoint can be used by changing the victim arguments:

```bash
export VICTIM_API_KEY="..."
python method_c/reattack_multiThread_lrm.py \
  --input attack_story/story_set_gptfuzz/deepseekv3-gptfuzz-story.json \
  --run-name new-target-smoke \
  --victim-base-url "https://your-provider.example/v1" \
  --victim-model "provider-model-name" \
  --victim-label "paper-facing-target-name" \
  --attacker-api-key-env ARK_API_KEY \
  --limit 2 \
  --resume
```

The same fields can be supplied as defaults through environment variables: `VICTIM_BASE_URL`, `VICTIM_MODEL`, `VICTIM_LABEL`, `VICTIM_API_KEY_ENV`, `VICTIM_ENABLE_THINKING`, `VICTIM_STREAM`, `VICTIM_EXTRA_BODY_JSON`, and `VICTIM_REASONING_EFFORT`.

For vLLM / Qwen3 thinking mode, keep using `--victim-enable-thinking`. For APIs that only emit `reasoning_content` in streamed deltas, add `--victim-stream`. For explicit effort-controlled experiments, pass `--victim-reasoning-effort {low,medium,high}`; omit it to use the provider/model default. Provider-specific OpenAI-compatible request options can be passed with `--victim-extra-body-json '{"key":"value"}'`.
