# Task 05: Review Signals Only

## Goal
Evaluate signals and position using existing repo data only.

## Read
- all files under `assets/silver/`
- `assets/silver/framework/decision_protocol.md`
- `assets/silver/framework/freshness_rules.md`
- `assets/silver/framework/scoring.md`

## Edit only
- `assets/silver/signals/signal_state.md`
- `assets/silver/trades/current_position.md`

## Do not edit
- snapshot files
- thesis files
- journal files

## Rules
- Do not browse or fetch new data
- Use only existing repo information
- Must apply `assets/silver/framework/decision_protocol.md`, `assets/silver/framework/scoring.md`, and `assets/silver/framework/freshness_rules.md`
- Apply freshness rules even without new data
- If data is stale, confidence must be reduced
- If core macro inputs are stale, confidence must be capped according to the freshness rules
- Enforce signal score and signal language alignment
- If the score remains `0`, the wording must stay explicitly neutral
- Technical pivot levels must be labeled as watch levels unless independently confirmed
- Keep facts and interpretation strictly separated
- Explicitly state whether macro inputs are stale or aligned
- Explicitly include a data freshness assessment
- Explicitly state whether the stance is degraded due to stale inputs
- If information is insufficient, keep stance neutral

## Output
- Updated signal_state.md
- Updated current_position.md
- Brief explanation of decision
