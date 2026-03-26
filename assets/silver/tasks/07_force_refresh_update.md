# Task 07: Force Refresh Update

## Goal
Force a full rewrite of the current decision files even if the conclusion does not change.

## Read
- `AGENTS.md`
- all files under `assets/silver/`

## Use as inputs
- `assets/silver/data/market_snapshot.md`
- `assets/silver/data/macro_snapshot.md`
- `assets/silver/data/sentiment_snapshot.md`
- `assets/silver/framework/decision_protocol.md`
- `assets/silver/framework/scoring.md`
- `assets/silver/framework/freshness_rules.md`

## Rewrite every time
Always rewrite these files, even if the final stance remains the same:
- `assets/silver/thesis/current_state.md`
- `assets/silver/signals/signal_state.md`
- `assets/silver/trades/current_position.md`
- `assets/silver/journal/notes.md`

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
- Forced rewrite behavior must be preserved even if the final stance does not change
- Preserve journal history by appending, not overwriting
- If evidence is mixed, a neutral outcome is acceptable, but the files must still be refreshed
- Must apply `assets/silver/framework/decision_protocol.md`, `assets/silver/framework/scoring.md`, and `assets/silver/framework/freshness_rules.md`
- Must explicitly state whether macro inputs are stale or aligned
- Must explicitly include a data freshness assessment in the output
- Must explicitly state whether the stance is degraded due to stale inputs
- Must cap confidence according to the freshness rules
- Must ensure signal language matches signal score
- If the score remains `0`, the wording must stay explicitly neutral
- Must label technical levels as watch levels unless independently confirmed
- Must reject outputs that mix facts and interpretation
