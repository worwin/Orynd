# Task 06: Run Buffett Entry/Exit

## Goal
Generate the decisive Buffett-style action layer.

## Read
- all target ticker files
- `assets/equities/framework/decision_protocol.md`
- `assets/equities/framework/scoring.md`
- `assets/equities/framework/freshness_rules.md`
- `assets/equities/framework/buffett_rules.md`
- `assets/equities/framework/valuation_rules.md`
- `assets/equities/framework/json_schema.md`

## Update
- `decisions/buffett_decision.md`
- `decisions/buffett_decision.json`

## Rules
- Choose exactly one of `BUY`, `HOLD`, `SELL`, or `INSUFFICIENT_DATA`.
- Include explicit entry and exit prices.
- If critical filing coverage is missing, reduce confidence and say so.
