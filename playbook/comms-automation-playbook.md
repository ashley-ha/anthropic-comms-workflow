# Comms Automation Playbook

A replicable guide for building and deploying AI-powered communications workflows. Designed to be adapted by other teams across Anthropic.

---

## 1) Workflow: Daily Press Digest

### Problem
Manual clip curation is slow (1-2 hours/day), inconsistent across team members, and hard to scale during high-volume news cycles. Junior team members may miss nuanced relevance signals.

### Solution
Claude analyzes each article from monitored sources for:
- **Relevance** (1-10 score) to Anthropic's communications interests
- **Topic classification** (policy, product, business, safety, competition)
- **Sentiment analysis** (positive, negative, neutral, mixed)
- **Rationale** explaining why each article matters or doesn't

Articles above the relevance threshold are compiled into a formatted Slack digest each morning.

### Key Design Decisions
- **Tool_use for structured output**: Guarantees valid JSON from Claude, not freeform text parsing
- **Per-article rationale**: Builds trust by making AI reasoning transparent and auditable
- **Configurable threshold**: Team leads adjust sensitivity based on news volume (default: 6/10)
- **Human review preserved**: Digest is a recommendation, not a replacement for editorial judgment

### Rollout Plan
| Week | Phase | Details |
|------|-------|---------|
| 1 | Shadow mode | Run in parallel with manual process, compare outputs |
| 2 | Pilot | 3 team members receive AI digest alongside manual clips |
| 3 | Evaluation | Review eval metrics, adjust threshold, collect feedback |
| 4+ | Full rollout | Replace manual morning clips with AI digest + human review |

### KPIs
- Time spent on morning clip curation (target: 60% reduction)
- Relevance precision at top 10 clips (target: >80%)
- Topic classification accuracy (target: >75%)
- Team satisfaction score (target: >4/5)

---

## 2) Workflow: Rapid Response Alerting

### Problem
High-risk stories and events can be detected too late or routed inconsistently. Different team members apply different severity thresholds, leading to missed P0 events or unnecessary P0 escalations.

### Solution
Claude assesses each incoming event for:
- **Priority score** (1-10) and **tier assignment** (P0/P1/P2)
- **Rationale** for the tier assignment
- **Talking points** tailored to Anthropic's values and messaging
- **Escalation guidance** for the first 30 minutes

### Tier Definitions
| Tier | SLA | Owners | Examples |
|------|-----|--------|----------|
| P0 | 1 hour | Comms Lead, Legal, Policy, Exec On-Call | Data breach, safety incident, regulatory action |
| P1 | 4 hours | Comms Lead, Policy | Negative coverage trend, media inquiry with deadline |
| P2 | 24 hours | Comms Operations | Routine competitor news, minor social chatter |

### Key Design Decisions
- **Human-in-the-loop for P0/P1**: Claude recommends, humans decide
- **Talking points as starting points**: Never use AI-generated messaging verbatim without review
- **Conservative escalation**: Better to over-alert than miss a true P0
- **Slack delivery for urgency**: P0/P1 alerts push to Slack immediately; P2 logged only

### Rollout Plan
| Week | Phase | Details |
|------|-------|---------|
| 1-2 | Shadow mode | Run alongside existing monitoring, compare tier assignments |
| 3 | Pilot | Policy and legal-sensitive sources only |
| 4 | Evaluation | Measure tier accuracy, P0 recall, false positive rate |
| 5+ | Expand | Add all source types, reduce human review for P2 |

### KPIs
- Tier assignment accuracy vs. human reviewers (target: >85%)
- P0 recall (target: >95% — never miss a true crisis)
- P0 false positive rate (target: <15%)
- Mean time to first alert (target: <5 min from event ingestion)

---

## 3) Workflow: Spokesperson Briefing Generator

### Problem
Preparing spokesperson briefings for media engagements requires synthesizing recent coverage, key messages, competitive context, and anticipated questions. This takes 2-4 hours per briefing and quality varies by preparer.

### Solution
Claude generates structured briefing documents containing:
1. Engagement overview
2. Key messages to land
3. Recent coverage context
4. Anticipated tough questions with suggested framing
5. Landmines to avoid
6. Bridging language for difficult moments

### Key Design Decisions
- **Always requires human review**: Briefings are drafts, never sent directly to spokespeople
- **Recent coverage grounding**: Claude references actual articles, not hallucinated context
- **Adversarial question generation**: Claude is prompted to think like a tough journalist

### KPIs
- Time to produce a briefing (target: 30 min including human review, down from 2-4 hours)
- Spokesperson satisfaction with prep quality (target: >4/5)
- Coverage of actual questions asked in interview (target: >70% anticipated)

---

## 4) Training and Enablement

- **45-minute onboarding** per workflow (see `docs/TRAINING_PLAN.md`)
- **1-page quick-start guide** per workflow
- **Weekly office hours** during first 30 days
- **Feedback form** linked in all AI-generated outputs
- **Monthly eval review** with team leads to track quality trends

---

## 5) Governance and Safety

- **Human-in-the-loop** for all high-severity outputs (P0/P1 alerts, spokesperson briefings)
- **Audit trail**: Every Claude call logged with input, output, and timestamp
- **Prompt versioning**: System prompts tracked in source control with changelogs
- **Eval gates**: New prompt versions must pass eval thresholds before deployment
- **No external data ingestion** without legal/terms-of-service review
- **Data minimization**: Only article metadata and summaries sent to Claude, not full copyrighted text

---

## 6) Replication Guide for Other Teams

This playbook is designed to be adapted. To apply these patterns to a different function:

1. **Discover**: Audit the team's workflows for repetitive, time-consuming, or inconsistent processes
2. **Build**: Design Claude-powered tools with structured outputs and human-in-the-loop
3. **Evaluate**: Create labeled datasets and run evals before deployment
4. **Train**: Develop role-specific training with hands-on drills
5. **Measure**: Track KPIs from day 1 and review monthly
6. **Iterate**: Use feedback loops to improve prompts, thresholds, and workflows

The `evals/` framework and this playbook structure can be copied directly as starting templates.
