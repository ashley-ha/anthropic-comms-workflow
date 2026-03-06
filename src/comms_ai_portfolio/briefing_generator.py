# ABOUTME: Spokesperson briefing generator powered by Claude.
# ABOUTME: Synthesizes recent coverage and key messages into interview prep documents.
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .claude_client import generate_briefing


def build_briefing(input_path: Path, output_path: Path) -> dict[str, Any]:
    """Generate a spokesperson briefing document from a request file.

    The request file contains spokesperson details, engagement context,
    key messages, and recent coverage. Claude synthesizes these into a
    structured prep document.

    Args:
        input_path: Path to JSON briefing request file.
        output_path: Path where the Markdown briefing will be written.

    Returns:
        Summary dict with spokesperson, outlet, and word count.
    """
    with input_path.open("r", encoding="utf-8") as f:
        request = json.load(f)

    briefing_text = generate_briefing(
        spokesperson=request["spokesperson"],
        engagement_type=request["engagement_type"],
        outlet=request["outlet"],
        date=request["date"],
        topics=request["topics"],
        key_messages=request["key_messages"],
        recent_coverage=request.get("recent_coverage", []),
    )

    lines = [
        f"# Spokesperson Briefing: {request['spokesperson']}",
        f"**{request['engagement_type']}** with {request['outlet']} | {request['date']}",
        "",
        "---",
        "",
        briefing_text,
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "spokesperson": request["spokesperson"],
        "outlet": request["outlet"],
        "engagement_type": request["engagement_type"],
        "word_count": len(briefing_text.split()),
    }
