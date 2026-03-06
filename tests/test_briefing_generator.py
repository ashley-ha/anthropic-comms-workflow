# ABOUTME: Integration tests for the spokesperson briefing generator.
# ABOUTME: Calls Claude API to verify briefing generation from request data.
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from comms_ai_portfolio.briefing_generator import build_briefing


class TestBriefingGenerator(unittest.TestCase):
    """Test Claude's briefing generation produces complete prep documents."""

    def test_build_briefing_integration(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "briefing.md"
            summary = build_briefing(
                repo_root / "data" / "briefing_request.json",
                output,
            )
            self.assertTrue(output.exists())
            self.assertEqual(summary["spokesperson"], "Dario Amodei")
            self.assertGreater(summary["word_count"], 100)

            content = output.read_text()
            self.assertIn("Spokesperson Briefing", content)
            # Briefing should address anticipated questions
            content_lower = content.lower()
            self.assertTrue(
                "question" in content_lower or "q:" in content_lower or "anticipated" in content_lower,
                "Briefing should include anticipated questions section",
            )


if __name__ == "__main__":
    unittest.main()
