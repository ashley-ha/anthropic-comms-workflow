# Evaluation Framework

This directory contains a runnable evaluation harness that measures Claude's performance against human-labeled ground truth.

## Running Evals

```bash
python evals/eval_runner.py
```

This will:
1. Run Claude against every article in `data/eval_articles_labeled.json`
2. Run Claude against every event in `data/eval_events_labeled.json`
3. Print a detailed report to stdout
4. Save metrics to `outputs/eval_results.json`

## Datasets

### Article Eval Set (`data/eval_articles_labeled.json`)
10 articles with human labels for:
- `relevance_score` (1-10)
- `topic` (policy, product, business, safety, competition, general)
- `sentiment` (positive, negative, neutral, mixed)

### Event Eval Set (`data/eval_events_labeled.json`)
6 events with human labels for:
- `tier` (P0, P1, P2)

## Metrics

### Press Digest
| Metric | Description | Target |
|--------|-------------|--------|
| Relevance accuracy (within 2) | % of articles scored within 2 points of human label | >80% |
| Topic accuracy | % of articles with matching topic classification | >75% |
| Sentiment accuracy | % of articles with matching sentiment | >70% |
| Relevance MAE | Mean absolute error of relevance scores | <2.0 |

### Rapid Response
| Metric | Description | Target |
|--------|-------------|--------|
| Tier accuracy | % of events with matching tier assignment | >85% |
| P0 recall | % of true P0 events correctly identified | >95% |
| P0 false positive rate | % of non-P0 events incorrectly labeled P0 | <15% |

## YAML Spec Files

The `.yaml` files in this directory declare metric names and thresholds for CI/CD gating (future integration). They are not currently connected to an automated runner but serve as the contract for what "passing" means.

## Extending the Eval Set

To add new labeled examples:
1. Add articles/events to the appropriate `data/eval_*_labeled.json` file
2. Include human labels in the `labels` field
3. Re-run `python evals/eval_runner.py` to see updated metrics
4. Consider adding examples that target known failure modes (edge cases, ambiguous articles)
