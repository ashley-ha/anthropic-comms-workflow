#!/usr/bin/env python3
# ABOUTME: Entry point for the press digest workflow.
# ABOUTME: Loads env, runs Claude-powered article analysis, and optionally posts to Slack.
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from comms_ai_portfolio.press_digest import build_digest
from comms_ai_portfolio.slack_output import post_digest_to_slack


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    threshold = int(os.getenv("DIGEST_RELEVANCE_THRESHOLD", "6"))

    print(f"Building press digest (threshold={threshold})...")
    output_path = root / "outputs" / "press_digest.md"
    summary = build_digest(
        input_path=root / "data" / "mock_articles.json",
        output_path=output_path,
        threshold=threshold,
    )
    print(f"Digest complete: {summary}")

    if os.getenv("SLACK_WEBHOOK_URL"):
        print("Posting to Slack...")
        post_digest_to_slack(output_path)
        print("Posted.")
    else:
        print("No SLACK_WEBHOOK_URL set, skipping Slack delivery.")
        print(f"View digest at: {output_path}")
