#!/usr/bin/env python3
# ABOUTME: Entry point for the rapid response workflow.
# ABOUTME: Loads env, runs Claude-powered event triage, and optionally posts alerts to Slack.
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from comms_ai_portfolio.rapid_response import build_alerts
from comms_ai_portfolio.slack_output import post_alerts_to_slack


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]

    print("Running rapid response analysis...")
    output_path = root / "outputs" / "rapid_response_alerts.json"
    summary = build_alerts(
        input_path=root / "data" / "mock_events.json",
        output_path=output_path,
    )
    print(f"Alerts complete: {summary}")

    if os.getenv("SLACK_WEBHOOK_URL"):
        print("Posting P0/P1 alerts to Slack...")
        post_alerts_to_slack(output_path)
        print("Posted.")
    else:
        print("No SLACK_WEBHOOK_URL set, skipping Slack delivery.")
        print(f"View alerts at: {output_path}")
