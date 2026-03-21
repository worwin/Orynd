# Task 05: Review Signals Only

## Goal
Evaluate signals and position using existing repo data only.

## Read
- all files under `assets/gold/`
- `assets/gold/framework/freshness_rules.md`
- `assets/gold/framework/scoring.md`

## Edit only
- `assets/gold/signals/signal_state.md`
- `assets/gold/trades/current_position.md`

## Do not edit
- snapshot files
- thesis files
- journal files

## Rules
- Do not browse or fetch new data
- Use only existing repo information
- Apply freshness rules even without new data
- If data is stale, confidence must be reduced
- If core macro inputs are stale, confidence must be capped according to the freshness rules
- Enforce signal score and signal language alignment
- Explicitly state whether the stance is degraded due to stale inputs
- If information is insufficient, keep stance neutral

## Output
- Updated signal_state.md
- Updated current_position.md
- Brief explanation of decision
