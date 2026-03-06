# ABOUTME: Integration tests for the rapid response workflow.
# ABOUTME: Calls Claude API to verify event assessment and alert generation.
from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from comms_ai_portfolio.claude_client import assess_event
from comms_ai_portfolio.rapid_response import build_alerts


class TestEventAssessment(unittest.TestCase):
    """Test Claude's event assessment produces valid structured output."""

    def test_critical_event(self) -> None:
        event = {
            "event_id": "test-001",
            "summary": "Major data breach confirmed: Claude API leaked user conversation logs to unauthorized third parties. Multiple news outlets reporting.",
            "source": "eng-monitor",
            "timestamp": "2026-03-05T12:00:00Z",
        }
        result = assess_event(event)

        self.assertIn("priority_score", result)
        self.assertIn("tier", result)
        self.assertIn("talking_points", result)
        self.assertIn("escalation_note", result)
        self.assertEqual(result["tier"], "P0")
        self.assertIsInstance(result["talking_points"], list)
        self.assertGreater(len(result["talking_points"]), 0)

    def test_low_priority_event(self) -> None:
        event = {
            "event_id": "test-002",
            "summary": "Minor competitor Cohere publishes a routine blog post about their latest model update. No significant market impact expected.",
            "source": "competitive-intel",
            "timestamp": "2026-03-05T12:00:00Z",
        }
        result = assess_event(event)

        self.assertEqual(result["tier"], "P2")

    def test_build_alerts_integration(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "alerts.json"
            summary = build_alerts(
                repo_root / "data" / "mock_events.json",
                output,
            )
            self.assertTrue(output.exists())
            self.assertGreater(summary["alert_count"], 0)

            with output.open() as f:
                alerts = json.load(f)
            for alert in alerts:
                self.assertIn("talking_points", alert)
                self.assertIn("rationale", alert)
                self.assertIn("escalation_note", alert)


if __name__ == "__main__":
    unittest.main()
