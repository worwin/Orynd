# Task 04: Update Silver

## Goal
Update silver thesis, signals, and position using snapshot data.

## Read
- `AGENTS.md`
- all files under `assets/silver/`

## Use as inputs
- `assets/silver/data/market_snapshot.md`
- `assets/silver/data/macro_snapshot.md`
- `assets/silver/data/sentiment_snapshot.md`
- `assets/silver/framework/freshness_rules.md`
- `assets/silver/framework/decision_protocol.md`
- `assets/silver/framework/scoring.md`

## Edit only
- `assets/silver/thesis/current_state.md`
- `assets/silver/signals/signal_state.md`
- `assets/silver/trades/current_position.md`
- `assets/silver/journal/notes.md`

## Do not edit
- snapshot files
- core thesis
- signal rules

## Output structure
- Facts
- Interpretation
- Signal
- Confidence
- Signal score
- Action
- Risk
- Invalidation
- Data freshness assessment

## Additional requirements
- Include confidence level: high, medium, or low
- List top 3 facts driving the conclusion
- List top 2 risks to the thesis

## Rules
- Do not invent data
- Must apply `assets/silver/framework/decision_protocol.md`, `assets/silver/framework/scoring.md`, and `assets/silver/framework/freshness_rules.md`
- Apply `assets/silver/framework/freshness_rules.md` before assigning confidence
- If core macro inputs are stale, confidence must be capped
- If freshness is poor, prefer neutral stance and lower confidence
- Signal language must match signal score
- If the score remains `0`, the wording must stay explicitly neutral
- Technical pivot levels must be labeled as watch levels unless independently confirmed
- Keep facts and interpretation strictly separated
- Must explicitly state whether macro inputs are stale or aligned
- If signals conflict, default to neutral or hold
- Preserve previous journal entries
- This is the light update task: a rewrite is allowed but not required if the current files already remain accurate under the latest framework and inputs
