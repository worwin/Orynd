# Scoring Framework

## Signal Score
- +2 = strong bullish
- +1 = mild bullish
- 0 = neutral
- -1 = mild bearish
- -2 = strong bearish

## Confidence Score
- 0-100%

## Confidence bands
- High = 76-100%
- Medium = 51-75%
- Low = 0-50%

## Interpretation
- Signal score reflects directional conviction
- Confidence reflects quality, freshness, and consistency of inputs

## Rules
- Mixed signals -> score near 0
- High confidence requires alignment across macro, sentiment, and price
- Apply `assets/gold/framework/freshness_rules.md` before assigning confidence
- If core macro inputs are stale beyond tactical freshness limits, confidence cannot exceed low
- If market and macro timestamps are mixed, confidence must be capped according to the freshness rules
- Proxy substitutions such as broad dollar index instead of `DXY` reduce confidence and must be stated explicitly
- Slow-moving inputs such as ETF flows and central-bank demand may support context, but they cannot by themselves justify high tactical confidence

## Signal language agreement
- Signal wording must match the numeric score
- `+2` and `+1` require bullish language
- `-2` and `-1` require bearish language
- `0` requires neutral language
- If the writer wants to note directional pressure while keeping a `0` score, use wording such as "neutral with bullish pressure" or "neutral with bearish pressure" and make clear that the score remains neutral

## Technical level handling
- Unconfirmed pivot levels are watch levels, not validated breakout or invalidation levels
- Do not let unconfirmed pivots drive a stronger score by themselves
- To use a technical level as a decision trigger rather than a watch level, independently confirm it with broader chart structure, repeated closes, or another verified technical reference
