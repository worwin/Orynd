# Task 04: Update Gold

## Goal
Update gold thesis, signals, and position using snapshot data.

## Read
- `AGENTS.md`
- all files under `assets/gold/`

## Use as inputs
- `assets/gold/data/market_snapshot.md`
- `assets/gold/data/macro_snapshot.md`
- `assets/gold/data/sentiment_snapshot.md`

## Edit only
- `assets/gold/thesis/current_state.md`
- `assets/gold/signals/signal_state.md`
- `assets/gold/trades/current_position.md`
- `assets/gold/journal/notes.md`

## Do not edit
- snapshot files
- core thesis
- signal rules

## Output structure
- Facts
- Interpretation
- Signal
- Action
- Invalidation

## Additional requirements
- Include confidence level: high, medium, or low
- List top 3 facts driving the conclusion
- List top 2 risks to the thesis

## Rules
- Do not invent data
- If signals conflict, default to neutral or hold
- Preserve previous journal entries
