#!/usr/bin/env python3
# ABOUTME: Entry point for the spokesperson briefing generator.
# ABOUTME: Loads env, sends briefing request to Claude, and writes a formatted prep document.
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from comms_ai_portfolio.briefing_generator import build_briefing


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]

    print("Generating spokesperson briefing...")
    output_path = root / "outputs" / "briefing.md"
    summary = build_briefing(
        input_path=root / "data" / "briefing_request.json",
        output_path=output_path,
    )
    print(f"Briefing complete: {summary}")
    print(f"View briefing at: {output_path}")
