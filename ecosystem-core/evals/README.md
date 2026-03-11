# Eval Harness v0

Lightweight local eval harness for agent tasks.

## Scope
- Two tracks:
  - **WorkOps** (execution-heavy operational tasks)
  - **KnowledgeOps** (retrieval, synthesis, reasoning tasks)
- Placeholder golden set included (20 total):
  - `tasks/workops/golden_tasks.jsonl` (10)
  - `tasks/knowledgeops/golden_tasks.jsonl` (10)
- Scoring schema in `config/scoring_schema.v0.yaml`.

## Quick start

```bash
cd /home/node/.openclaw/workspace/agent-ecosystem/ecosystem-core/evals
python3 scripts/run_eval.py \
  --predictions results/sample_predictions.jsonl \
  --out results/latest_report.json
```

This validates prediction format, joins predictions with gold tasks, and computes:
- per-task score (0..1)
- track-level averages
- overall average

## Prediction format
One JSON object per line:

```json
{"task_id":"workops_001","predicted_answer":"...","metadata":{"model":"agent-x"}}
```

## What is runnable now
- Golden tasks load + schema checks.
- Deterministic exact/substring scoring.
- Weighted aggregation by task `weight`.
- JSON report generation.

## Known gaps (v0 -> v1)
- No LLM-judge for open-ended/free-form outputs.
- No latency/cost/error-rate metrics yet.
- No multi-turn trajectory scoring.
- No CI wiring (GitHub Action) yet.
- No dataset version pinning or signed manifests.
