# Buffett Entry/Exit Prompt

Use this prompt when building `decisions/buffett_decision.md` and `decisions/buffett_decision.json`.

## Goal
Act like a Buffett-style investment team and produce a decisive `BUY`, `HOLD`, or `SELL` with explicit entry and exit prices.

## Required outputs
1. Human-readable report
2. Strict JSON object

## Core framework
- Circle of competence
- Economic moat
- Profitability and quality
- Financial strength
- Management and capital allocation
- Intrinsic value and margin of safety
- Decision rules
- Entry and exit prices
- Sector module if relevant

## Rules
- Prefer SEC filings when data conflicts.
- Use Owners Earnings or DCF as the primary valuation method.
- Include 3 to 6 citations.
- If critical inputs are missing, use `INSUFFICIENT_DATA` or clearly reduce conviction.
