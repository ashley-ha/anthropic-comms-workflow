# ABOUTME: Integration tests for the press digest workflow.
# ABOUTME: Calls Claude API to verify article analysis and digest generation.
from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from comms_ai_portfolio.claude_client import analyze_article
from comms_ai_portfolio.press_digest import build_digest


class TestArticleAnalysis(unittest.TestCase):
    """Test Claude's article analysis produces valid structured output."""

    def test_highly_relevant_article(self) -> None:
        article = {
            "title": "Anthropic launches Claude 4 with breakthrough safety features",
            "body": "Anthropic released Claude 4 today with new constitutional AI improvements and enterprise features.",
            "source": "TechCrunch",
            "url": "https://example.com/claude4",
            "published_at": "2026-03-05T08:00:00Z",
        }
        result = analyze_article(article)

        self.assertIn("relevance_score", result)
        self.assertIn("topic", result)
        self.assertIn("sentiment", result)
        self.assertIn("rationale", result)
        self.assertIsInstance(result["relevance_score"], int)
        self.assertGreaterEqual(result["relevance_score"], 7)
        self.assertIn(result["topic"], ["policy", "product", "business", "safety", "competition", "general"])
        self.assertIn(result["sentiment"], ["positive", "negative", "neutral", "mixed"])

    def test_irrelevant_article(self) -> None:
        article = {
            "title": "Local sports team wins championship",
            "body": "The hometown team celebrated their victory in the regional basketball finals.",
            "source": "Local News",
            "url": "https://example.com/sports",
            "published_at": "2026-03-05T08:00:00Z",
        }
        result = analyze_article(article)

        self.assertLessEqual(result["relevance_score"], 3)

    def test_build_digest_integration(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "digest.md"
            summary = build_digest(
                repo_root / "data" / "articles.json",
                output,
                threshold=6,
            )
            self.assertTrue(output.exists())
            self.assertGreater(summary["selected_count"], 0)
            self.assertIn("topic_mix", summary)
            content = output.read_text()
            self.assertIn("# Daily Press Digest", content)


if __name__ == "__main__":
    unittest.main()
