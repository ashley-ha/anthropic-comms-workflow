# ABOUTME: Slack webhook integration for delivering digests and alerts.
# ABOUTME: Formats outputs into Slack Block Kit messages and posts via webhook.
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any


def post_digest_to_slack(digest_path: Path, webhook_url: str | None = None) -> bool:
    """Post a press digest summary to Slack via webhook.

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
    # Truncate for Slack's 3000-char block limit
    if len(content) > 2800:
        content = content[:2800] + "\n\n_[Truncated — see full digest in shared drive]_"

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Daily Press Digest"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": content},
            },
        ],
    }

    return _post_webhook(url, payload)


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
