# ABOUTME: Data models for articles, events, and briefing requests.
# ABOUTME: Used across press digest, rapid response, and briefing generator workflows.
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Article:
    title: str
    body: str
    source: str
    url: str
    published_at: str


@dataclass
class AnalyzedArticle:
    title: str
    body: str
    source: str
    url: str
    published_at: str
    relevance_score: int
    topic: str
    sentiment: str
    rationale: str


@dataclass
class Event:
    event_id: str
    summary: str
    source: str
    timestamp: str


@dataclass
class AlertAssessment:
    event_id: str
    timestamp: str
    source: str
    summary: str
    priority_score: int
    tier: str
    owners: list[str]
    response_sla_hours: int
    human_review_required: bool
    rationale: str
    talking_points: list[str]


@dataclass
class BriefingRequest:
    spokesperson: str
    engagement_type: str
    outlet: str
    date: str
    topics: list[str]
    key_messages: list[str]
    recent_coverage: list[Article] = field(default_factory=list)
