# ABOUTME: Runnable evaluation harness for press digest and rapid response workflows.
# ABOUTME: Scores Claude outputs against human-labeled ground truth and reports metrics.
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from comms_ai_portfolio.claude_client import analyze_article, assess_event


def run_article_eval(data_path: Path) -> dict[str, Any]:
    """Evaluate Claude's article analysis against human labels.

    Metrics:
    - relevance_accuracy: % of articles where Claude's score is within 2 of label
    - topic_accuracy: % of articles where topic matches
    - sentiment_accuracy: % of articles where sentiment matches
    - relevance_mae: Mean absolute error on relevance scores
    """
    with data_path.open("r", encoding="utf-8") as f:
        articles = json.load(f)

    results = []
    for article in articles:
        labels = article.pop("labels")
        analysis = analyze_article(article)
        results.append({
            "title": article["title"],
            "predicted": analysis,
            "labeled": labels,
        })

    relevance_within_2 = sum(
        1 for r in results
        if abs(r["predicted"]["relevance_score"] - r["labeled"]["relevance_score"]) <= 2
    )
    topic_matches = sum(
        1 for r in results if r["predicted"]["topic"] == r["labeled"]["topic"]
    )
    sentiment_matches = sum(
        1 for r in results if r["predicted"]["sentiment"] == r["labeled"]["sentiment"]
    )
    relevance_errors = [
        abs(r["predicted"]["relevance_score"] - r["labeled"]["relevance_score"])
        for r in results
    ]

    n = len(results)
    metrics = {
        "total_articles": n,
        "relevance_accuracy_within_2": round(relevance_within_2 / n, 3),
        "topic_accuracy": round(topic_matches / n, 3),
        "sentiment_accuracy": round(sentiment_matches / n, 3),
        "relevance_mae": round(sum(relevance_errors) / n, 2),
    }

    return {"metrics": metrics, "details": results}


def run_event_eval(data_path: Path) -> dict[str, Any]:
    """Evaluate Claude's event assessment against human labels.

    Metrics:
    - tier_accuracy: % of events where tier matches
    - tier_confusion: breakdown of mismatches
    - p0_recall: % of true P0 events correctly identified
    - p0_false_positive_rate: % of non-P0 events incorrectly labeled P0
    """
    with data_path.open("r", encoding="utf-8") as f:
        events = json.load(f)

    results = []
    for event in events:
        labels = event.pop("labels")
        assessment = assess_event(event)
        results.append({
            "event_id": event["event_id"],
            "predicted_tier": assessment["tier"],
            "labeled_tier": labels["tier"],
            "rationale": assessment["rationale"],
        })

    tier_matches = sum(1 for r in results if r["predicted_tier"] == r["labeled_tier"])
    true_p0 = [r for r in results if r["labeled_tier"] == "P0"]
    p0_recall = (
        sum(1 for r in true_p0 if r["predicted_tier"] == "P0") / len(true_p0)
        if true_p0
        else 0.0
    )
    non_p0 = [r for r in results if r["labeled_tier"] != "P0"]
    p0_fp_rate = (
        sum(1 for r in non_p0 if r["predicted_tier"] == "P0") / len(non_p0)
        if non_p0
        else 0.0
    )

    # Confusion breakdown
    confusion: dict[str, dict[str, int]] = {}
    for r in results:
        key = f"{r['labeled_tier']}->{r['predicted_tier']}"
        confusion[key] = confusion.get(key, 0) + 1

    n = len(results)
    metrics = {
        "total_events": n,
        "tier_accuracy": round(tier_matches / n, 3),
        "p0_recall": round(p0_recall, 3),
        "p0_false_positive_rate": round(p0_fp_rate, 3),
        "confusion": confusion,
    }

    return {"metrics": metrics, "details": results}


def print_report(name: str, result: dict[str, Any]) -> None:
    """Pretty-print an eval report to stdout."""
    print(f"\n{'=' * 60}")
    print(f"  EVAL REPORT: {name}")
    print(f"{'=' * 60}")
    for key, value in result["metrics"].items():
        if isinstance(value, dict):
            print(f"\n  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")

    print(f"\n  Details:")
    for detail in result["details"]:
        if "title" in detail:
            pred = detail["predicted"]
            lab = detail["labeled"]
            match = "PASS" if abs(pred["relevance_score"] - lab["relevance_score"]) <= 2 else "FAIL"
            print(f"    [{match}] {detail['title'][:50]}...")
            print(f"          predicted: rel={pred['relevance_score']} topic={pred['topic']} sent={pred['sentiment']}")
            print(f"          labeled:   rel={lab['relevance_score']} topic={lab['topic']} sent={lab['sentiment']}")
        else:
            match = "PASS" if detail["predicted_tier"] == detail["labeled_tier"] else "FAIL"
            print(f"    [{match}] {detail['event_id']}: predicted={detail['predicted_tier']} labeled={detail['labeled_tier']}")

    print(f"\n{'=' * 60}\n")


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parents[1] / "data"

    print("Running article evaluation...")
    article_result = run_article_eval(data_dir / "eval_articles_labeled.json")
    print_report("Press Digest — Article Analysis", article_result)

    print("Running event evaluation...")
    event_result = run_event_eval(data_dir / "eval_events_labeled.json")
    print_report("Rapid Response — Event Triage", event_result)

    # Save results
    output_dir = Path(__file__).resolve().parents[1] / "outputs"
    output_dir.mkdir(exist_ok=True)
    with (output_dir / "eval_results.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "article_eval": article_result["metrics"],
                "event_eval": event_result["metrics"],
            },
            f,
            indent=2,
        )
    print(f"Results saved to {output_dir / 'eval_results.json'}")
