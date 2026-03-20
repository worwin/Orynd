# Task 03: Revise Market Snapshot

## Goal
Improve the accuracy and internal consistency of the market snapshot.

## Read
- `assets/gold/data/market_snapshot.md`

## Edit only
- `assets/gold/data/market_snapshot.md`

## Requirements
- Ensure current price, support, and resistance are internally consistent
- Distinguish clearly:
  - current price
  - recent high
  - current support
  - current resistance
  - former support that has failed
- Include timestamp and sources

## Rules
- Do not use support levels above current price unless labeled as former support
- If support/resistance cannot be verified, say so instead of guessing
- Prefer cleaner, more recent data sources
- Do not modify other files

## Output format
- Timestamp
- Raw facts
- Interpretation
- Notes
- Sources
