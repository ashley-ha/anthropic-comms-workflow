# Architecture

## System Overview

This project implements three Claude-powered communications workflows:

1. **Press Digest** — Daily coverage monitoring and analysis
2. **Rapid Response** — Real-time event triage and alert routing
3. **Briefing Generator** — Spokesperson prep document synthesis

All three workflows use the Anthropic SDK to call Claude with structured tool definitions, ensuring reliable JSON output for downstream processing.

## Claude Integration Pattern

Each workflow follows the same pattern:

```
Raw Data → Claude Analysis (tool_use) → Structured Output → Formatting → Delivery
```

**Why tool_use for structured outputs:** Instead of prompting Claude to output JSON in freeform text (which can produce invalid JSON or drift from schema), we define tool schemas that Claude fills in via function calling. This guarantees valid, schema-conformant output every time — critical for production reliability.

### Article Analysis Tool Schema

```json
{
  "relevance_score": 1-10,
  "topic": "policy|product|business|safety|competition|general",
  "sentiment": "positive|negative|neutral|mixed",
  "rationale": "Why this matters for Comms"
}
```

### Event Assessment Tool Schema

```json
{
  "priority_score": 1-10,
  "tier": "P0|P1|P2",
  "rationale": "Why this tier was assigned",
  "talking_points": ["point1", "point2"],
  "escalation_note": "First 30 minutes playbook"
}
```

### Briefing Generation

Uses direct message-based generation (no tool_use) since the output is a long-form document rather than structured data.

## Data Flow

```
Press Digest:
  mock_articles.json → Claude analyze_article() → filter by threshold → format Markdown → Slack webhook

Rapid Response:
  mock_events.json → Claude assess_event() → sort by priority → format JSON → Slack webhook (P0/P1 only)

Briefing Generator:
  briefing_request.json → Claude generate_briefing() → format Markdown
```

## Evaluation Architecture

The eval harness (`evals/eval_runner.py`) runs Claude against human-labeled datasets and measures:

- **Relevance accuracy**: Is Claude's relevance score within 2 points of the human label?
- **Topic/sentiment accuracy**: Does Claude agree with human classification?
- **Tier accuracy**: Does Claude assign the same priority tier?
- **P0 recall**: Does Claude catch all true critical events?
- **P0 false positive rate**: Does Claude over-escalate?

Results are saved to `outputs/eval_results.json` for tracking over time.

## Reliability Principles

- **Structured outputs via tool_use** for guaranteed schema conformance
- **Human-in-the-loop** for P0/P1 alerts (never auto-escalate critical events)
- **Transparent scoring** with rationale for every decision (auditable by Comms leads)
- **Threshold-based filtering** to control digest length and reduce noise
- **Eval-driven development** — measure before deploying, track after
