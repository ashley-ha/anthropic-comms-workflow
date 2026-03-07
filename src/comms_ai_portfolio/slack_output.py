# ABOUTME: Slack webhook integration for delivering digests and alerts.
# ABOUTME: Formats outputs into Slack Block Kit messages and posts via webhook.
from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any

# Slack limits: 50 blocks per message, 3000 chars per text block
MAX_ARTICLES_IN_SLACK = 10


def _md_to_mrkdwn(text: str) -> str:
    """Convert Markdown formatting to Slack mrkdwn."""
    # Replace Markdown links [text](url) with Slack links <url|text>
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<\2|\1>", text)
    # Strip blockquote markers (Slack renders > natively)
    # Strip heading markers
    text = re.sub(r"^#{1,3}\s+", "", text, flags=re.MULTILINE)
    return text


def _parse_digest_articles(content: str) -> tuple[str, list[dict[str, str]]]:
    """Parse the Markdown digest into a summary line and article entries."""
    lines = content.split("\n")
    summary = ""
    articles: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for line in lines:
        if line.startswith("**") and "articles selected" in line:
            summary = _md_to_mrkdwn(line)
        elif line.startswith("### "):
            if current.get("title"):
                articles.append(current)
            # Strip "### 1. " prefix
            current = {"title": re.sub(r"^###\s+\d+\.\s+", "", line), "meta": "", "rationale": "", "link": ""}
        elif current and line.startswith("**Source:**"):
            current["meta"] = _md_to_mrkdwn(line)
        elif current and line.startswith("**Relevance:**"):
            current["meta"] += "\n" + _md_to_mrkdwn(line)
        elif current and line.startswith(">"):
            current["rationale"] = line.lstrip("> ").strip()
        elif current and line.startswith("[Read full article]"):
            current["link"] = _md_to_mrkdwn(line)

    if current.get("title"):
        articles.append(current)

    return summary, articles


def post_digest_to_slack(digest_path: Path, webhook_url: str | None = None) -> bool:
    """Post a press digest summary to Slack via webhook.

    Parses the Markdown digest and builds proper Slack Block Kit messages
    with one section per article, dividers, and correct mrkdwn formatting.

    Args:
        digest_path: Path to the generated Markdown digest.
        webhook_url: Slack webhook URL. Falls back to SLACK_WEBHOOK_URL env var.

    Returns:
        True if posted successfully, False otherwise.
    """
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        print("No SLACK_WEBHOOK_URL configured, skipping Slack delivery.")
        return False

    content = digest_path.read_text(encoding="utf-8")
    summary, articles = _parse_digest_articles(content)

    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Daily Press Digest"},
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": summary}],
        },
        {"type": "divider"},
    ]

    for article in articles[:MAX_ARTICLES_IN_SLACK]:
        text = f"*{article['title']}*\n{article['meta']}"
        if article["rationale"]:
            text += f"\n>{article['rationale']}"
        if article["link"]:
            text += f"\n{article['link']}"

        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
        blocks.append({"type": "divider"})

    remaining = len(articles) - MAX_ARTICLES_IN_SLACK
    if remaining > 0:
        blocks.append({
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"_+ {remaining} more articles — see full digest for details_"}],
        })

    return _post_webhook(url, {"blocks": blocks})


def post_alerts_to_slack(alerts_path: Path, webhook_url: str | None = None) -> bool:
    """Post rapid response alerts to Slack via webhook.

    Only P0 and P1 alerts are posted. P2 alerts are logged but not pushed.

    Args:
        alerts_path: Path to the generated JSON alerts.
        webhook_url: Slack webhook URL. Falls back to SLACK_WEBHOOK_URL env var.

    Returns:
        True if posted successfully, False otherwise.
    """
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        print("No SLACK_WEBHOOK_URL configured, skipping Slack delivery.")
        return False

    with alerts_path.open("r", encoding="utf-8") as f:
        alerts = json.load(f)

    urgent = [a for a in alerts if a["tier"] in {"P0", "P1"}]
    if not urgent:
        print("No P0/P1 alerts to post.")
        return False

    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Rapid Response Alert"},
        },
    ]

    for alert in urgent:
        emoji = ":rotating_light:" if alert["tier"] == "P0" else ":warning:"
        text = (
            f"{emoji} *{alert['tier']}* — {alert['summary']}\n"
            f"*Score:* {alert['priority_score']}/10 | *SLA:* {alert['response_sla_hours']}h\n"
            f"*Owners:* {', '.join(alert['owners'])}\n"
            f"*Rationale:* {alert['rationale']}\n"
            f"*Talking points:*\n"
            + "\n".join(f"  - {tp}" for tp in alert["talking_points"])
        )
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
        blocks.append({"type": "divider"})

    return _post_webhook(url, {"blocks": blocks})


def _post_webhook(url: str, payload: dict[str, Any]) -> bool:
    """Post a JSON payload to a Slack webhook URL."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status == 200
