#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
GOLD_PATHS = [
    ROOT / "tasks" / "workops" / "golden_tasks.jsonl",
    ROOT / "tasks" / "knowledgeops" / "golden_tasks.jsonl",
]

def load_jsonl(path: Path):
    items = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSONL at {path}:{i}: {e}")
    return items

def norm(s):
    return str(s).strip().lower()

def score_task(gold, pred):
    method = gold.get("method", "exact_match")
    g = gold.get("gold_answer", "")
    p = pred.get("predicted_answer", "") if pred else ""

    if method == "exact_match":
        return 1.0 if norm(g) == norm(p) else 0.0
    if method == "substring_match":
        return 1.0 if norm(g) in norm(p) else 0.0
    raise ValueError(f"Unsupported method: {method}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True, help="Path to predictions JSONL")
    ap.add_argument("--out", default=str(ROOT / "results" / "latest_report.json"))
    args = ap.parse_args()

    gold = []
    for gp in GOLD_PATHS:
        gold.extend(load_jsonl(gp))

    preds = load_jsonl(Path(args.predictions))
    pred_map = {p["task_id"]: p for p in preds if "task_id" in p}

    required_gold_keys = {"task_id", "track", "gold_answer"}
    for t in gold:
        missing = required_gold_keys - t.keys()
        if missing:
            raise ValueError(f"Gold task {t.get('task_id')} missing keys: {sorted(missing)}")

    per_task = []
    track_scores = defaultdict(lambda: {"weighted_sum": 0.0, "weight_total": 0.0, "count": 0})
    overall_weighted_sum = 0.0
    overall_weight_total = 0.0

    for t in gold:
        task_id = t["task_id"]
        track = t["track"]
        weight = float(t.get("weight", 1.0))
        p = pred_map.get(task_id)
        s = score_task(t, p)

        per_task.append({
            "task_id": task_id,
            "track": track,
            "method": t.get("method", "exact_match"),
            "weight": weight,
            "score": s,
            "has_prediction": p is not None,
        })

        track_scores[track]["weighted_sum"] += s * weight
        track_scores[track]["weight_total"] += weight
        track_scores[track]["count"] += 1

        overall_weighted_sum += s * weight
        overall_weight_total += weight

    track_summary = {}
    for track, vals in track_scores.items():
        denom = vals["weight_total"] or 1.0
        track_summary[track] = {
            "num_tasks": vals["count"],
            "weighted_avg": vals["weighted_sum"] / denom,
        }

    report = {
        "harness_version": "v0",
        "num_gold_tasks": len(gold),
        "num_predictions": len(preds),
        "coverage": sum(1 for r in per_task if r["has_prediction"]) / (len(gold) or 1),
        "overall_weighted_avg": (overall_weighted_sum / (overall_weight_total or 1.0)),
        "track_summary": track_summary,
        "per_task": per_task,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote report: {out_path}")
    print(json.dumps({
        "overall_weighted_avg": report["overall_weighted_avg"],
        "coverage": report["coverage"],
        "tracks": report["track_summary"],
    }, indent=2))

if __name__ == "__main__":
    main()
