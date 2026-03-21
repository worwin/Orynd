# Task 07: Force Refresh Update

## Goal
Force a full rewrite of the current decision files even if the conclusion does not change.

## Read
- `AGENTS.md`
- all files under `assets/gold/`

## Use as inputs
- `assets/gold/data/market_snapshot.md`
- `assets/gold/data/macro_snapshot.md`
- `assets/gold/data/sentiment_snapshot.md`
- `assets/gold/framework/decision_protocol.md`
- `assets/gold/framework/scoring.md`
- `assets/gold/framework/freshness_rules.md`

## Rewrite every time
Always rewrite these files, even if the final stance remains the same:
- `assets/gold/thesis/current_state.md`
- `assets/gold/signals/signal_state.md`
- `assets/gold/trades/current_position.md`
- `assets/gold/journal/notes.md`

## Required sections
- Facts
- Interpretation
- Signal
- Confidence
- Signal score
- Action
- Risk
- Invalidation
- Top 3 facts
- Top 2 risks

## Rules
- No-op behavior is not allowed
- Preserve journal history by appending, not overwriting
- If evidence is mixed, a neutral outcome is acceptable, but the files must still be refreshed
- Use the decision protocol and scoring framework
- Apply freshness rules before setting confidence or tactical conviction
- If core macro inputs are stale, confidence must be capped
- If signal wording implies bullishness or bearishness, the signal score must agree
- If the score remains `0`, the wording must stay explicitly neutral
- Technical pivot levels must be labeled as watch levels unless independently confirmed
- Keep facts and interpretation strictly separated
