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
- Data freshness assessment
- Top 3 facts
- Top 2 risks

## Rules
- No-op behavior is not allowed
- Preserve journal history by appending, not overwriting
- If evidence is mixed, a neutral outcome is acceptable, but the files must still be refreshed
- Must apply `assets/gold/framework/decision_protocol.md`, `assets/gold/framework/scoring.md`, and `assets/gold/framework/freshness_rules.md`
- Must explicitly state whether macro inputs are stale or aligned
- Must explicitly include a data freshness assessment in the output
- Must cap confidence according to the freshness rules
- Must ensure signal language matches signal score
- If the score remains `0`, the wording must stay explicitly neutral
- Must label technical levels as watch levels unless independently confirmed
- Must reject outputs that mix facts and interpretation
