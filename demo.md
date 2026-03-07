# Demo Script

Five Claude-powered workflows for a communications team, each solving a specific daily problem. Run each demo independently or in sequence.

## Before You Start

```bash
source .venv/bin/activate
```

Ensure your `.env` has a valid `ANTHROPIC_API_KEY`. If running demos back-to-back, leave ~30 seconds between them to avoid rate limits.

---

## Demo 1: Live Press Digest

**The problem:** Every morning, the comms team manually scans dozens of news sources to figure out what happened overnight. It takes 30-60 minutes before they even know what to prioritize.

**What this does:** Fetches real articles from 7 RSS feeds, then has Claude score each for relevance, classify by topic and sentiment, and write a rationale for why it matters to the comms team.

### Steps

```bash
# Step 1: Fetch live articles from RSS feeds (no API key needed, ~5 seconds)
python scripts/run_fetch_articles.py --limit 15

# Step 2: Run the digest against real articles (~30-45 seconds)
python scripts/run_press_digest.py --live
```

### What to look at

Open `outputs/press_digest.md` — articles are ranked by relevance with scores, topics, sentiment, and a rationale explaining *why* each story matters for Anthropic's comms team. Note that these are today's actual headlines, not sample data.

### Key talking points
- Claude analyzes each article via **tool_use** (structured function calling), not freeform text parsing — this guarantees valid, schema-conformant output every time
- Articles are analyzed in **parallel** (5 workers) for faster throughput
- The relevance threshold is configurable — the team can tune how selective the digest is

---

## Demo 2: Rapid Response Triage

**The problem:** When a crisis breaks — a viral social media post, a regulatory announcement, a competitor move — the first 30 minutes are spent figuring out *how bad it is* and *who needs to know*. That's wasted time.

**What this does:** Claude assesses each incoming event, assigns a priority tier (P0/P1/P2), generates initial talking points aligned with company values, and recommends who to loop in and what the first 30 minutes should look like.

### Steps

```bash
python scripts/run_rapid_response.py
```

### What to look at

Open `outputs/rapid_response_alerts.json`. Look at:
- **P0 events** (e.g., viral misinformation, FTC investigation) — note the talking points reference Anthropic's specific values (safety, transparency, responsible development)
- **Escalation notes** — concrete guidance on who to loop in and what to do first
- **P2 events** (e.g., minor competitor blog post) — note Claude correctly de-prioritizes noise

### Key talking points
- The tier definitions (P0/P1/P2) mirror real comms team playbooks
- Talking points are grounded in Anthropic's actual messaging — not generic PR language
- The system prompt explicitly prevents dishonest or dismissive talking points

---

## Demo 3: Spokesperson Briefing

**The problem:** Prepping a spokesperson for a media interview takes a comms strategist 2-3 hours of research — pulling recent coverage, drafting key messages, anticipating tough questions, identifying landmines.

**What this does:** Claude synthesizes recent coverage, key messages, and the engagement context into a complete spokesperson prep document — including anticipated questions with suggested framing, landmines to avoid, and bridging language for difficult moments.

### Steps

```bash
python scripts/run_briefing.py
```

### What to look at

Open `outputs/briefing.md`. This is a full briefing for Dario Amodei's CNBC Squawk Box interview. Note:
- **Anticipated Questions** — these are the tough ones a business journalist would actually ask, not softballs
- **Landmines to Avoid** — topics to redirect away from, with reasoning
- **Bridging Language** — specific pivot phrases like "What I'd emphasize is..." for navigating difficult moments
- The briefing references the *specific* recent coverage from the mock data (Kaiser Permanente deployment, NYT op-ed, etc.)

### Key talking points
- This uses Claude's **direct generation** (no tool_use) because the output is a long-form document, not structured data — choosing the right Claude integration pattern for each task
- The system prompt instructs Claude to be honest about difficult questions — a briefing that only includes softballs is worse than no briefing

---

## Demo 4: Message Pull-Through Tracker

**The problem:** After a product launch or executive interview, the comms team asks "did our messages land?" Currently that's a subjective gut check. There's no systematic way to measure whether journalists actually reflected the company's key narratives in their reporting.

**What this does:** Claude analyzes each article against Anthropic's key messaging framework, scores how faithfully each narrative was reflected (verbatim, paraphrased, thematic, distorted, or absent), and flags distortions — where journalists twisted the intended message.

### Steps

```bash
# Option A: Run against live articles (more impressive, requires step 1 from Demo 1)
python scripts/run_pull_through.py --live

# Option B: Run against sample articles
python scripts/run_pull_through.py
```

### What to look at

Open `outputs/pull_through_report.md`. Key sections:
- **Narrative Health Dashboard** — per-message scores with visual bars showing which narratives are landing and which aren't
- **Distortion Alerts** — where journalists twisted Anthropic's intended messaging (this is the most valuable insight for a comms team)
- **Source Fidelity** — which outlets most faithfully reflect Anthropic's messaging vs. which ones distort it

### Key talking points
- This turns a subjective "how'd we do?" into **quantifiable data** the comms team can track over time
- Distortion detection is arguably the most valuable feature — knowing *where* your message is being twisted is more actionable than knowing it's absent
- The scoring weights are tuned: verbatim > paraphrased > thematic > absent, and distorted *reduces* the score (a twisted message is worse than an absent one)

---

## Demo 5: Internal Comms Pipeline

**The problem:** Internal communications (all-hands updates, FAQs, leadership messages) go through multiple rounds of drafting and review. The drafting takes time, the review is unstructured ("looks fine I guess"), and reformatting for different channels (email vs. Slack) is tedious busywork.

**What this does:** A three-stage pipeline — Claude drafts the content from a brief, then a *separate* Claude call reviews it with structured editorial feedback (tone, clarity, alignment, sensitivity), and finally Claude formats the approved content for each distribution channel.

### Steps

```bash
python scripts/run_internal_comms.py
```

### What to look at

Open `outputs/internal_comms_report.md`. The report shows all three stages:

1. **Stage 1: Draft** — A full all-hands message from Dario Amodei covering Q1 milestones, scaling challenges, and an FTC inquiry. Note the authentic executive voice — not corporate boilerplate.

2. **Stage 2: Editorial Review** — Structured scores for tone, clarity, and alignment, plus:
   - **Sensitivity Flags** — phrases that could be problematic if leaked (e.g., "can't predict timelines or outcomes" re: FTC)
   - **Suggested Edits** — concrete, actionable changes with reasoning
   - **Approval Recommendation** — approve / revise / escalate

3. **Stage 3: Channel Formatting** — The same content adapted for email (full paragraphs) and Slack (mrkdwn with tl;dr, bullet points, kept under 3000 chars)

### Key talking points
- The review stage uses **tool_use** for structured output while the draft stage uses **direct generation** — this project demonstrates knowing when to use which Claude integration pattern
- The system prompt warns Claude to write as if content could appear on the front page of the NYT — internal comms at AI companies frequently leak
- The human remains in the loop — Claude drafts and reviews, but a human must approve before distribution

---

## Full Sequence (if running all five)

For a complete demo, this order tells the best story — it follows a comms team through their day:

```bash
# Morning: What happened overnight?
python scripts/run_fetch_articles.py --limit 15
python scripts/run_press_digest.py --live

# Crisis breaks: How bad is it?
python scripts/run_rapid_response.py

# Prep for media: Get the CEO ready
python scripts/run_briefing.py

# Afternoon: Did our messages land?
python scripts/run_pull_through.py --live

# End of day: Draft the all-hands
python scripts/run_internal_comms.py
```

Total runtime: ~3-4 minutes with pauses between scripts to avoid rate limits.

## Output files to have open

Keep these ready to show after each script runs:
- `outputs/press_digest.md`
- `outputs/rapid_response_alerts.json`
- `outputs/briefing.md`
- `outputs/pull_through_report.md`
- `outputs/internal_comms_report.md`

A Markdown previewer (VS Code preview, Marked, or similar) makes the `.md` outputs much more visually impressive than raw text.
