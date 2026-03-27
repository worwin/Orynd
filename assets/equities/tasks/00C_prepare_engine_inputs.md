# Task 00C: Prepare Engine Inputs

## Goal
Convert extracted SEC filing data into a stable engine-ready input package for scoring, prediction, and decision workflows.

## Inputs
- `filings/edgar/extracted/companyfacts/annual_statement_history.json`
- `filings/edgar/extracted/companyfacts/quarterly_statement_history.json`
- `filings/edgar/extracted/companyfacts/buffett_metric_history.json`
- `filings/accounting_notes.md`
- `latest_10k.md`
- `latest_10q.md`
- `latest_8k.md`
- `proxy_def14a.md`

## Outputs
- `analysis/fundamental_snapshot.md`
- `analysis/valuation_snapshot.md`
- `analysis/long_term_analysis.md`
- future engine input JSON if the repo adds a dedicated model-input file

## Rules
- Use filing-derived numbers as the default source of truth.
- Carry forward coverage gaps and confidence penalties from the filing review step.
- Keep feature generation deterministic where possible.
- Distinguish slow-moving quality variables from event-driven updates.

## Notes
- This task is where SEC history becomes engine-ready context.
- It should feed Buffett analysis first, and later any prediction or ranking layer.
