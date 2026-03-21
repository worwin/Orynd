# Decision Protocol

## Required structure
Every gold decision must follow this order:

1. Facts
2. Interpretation
3. Signal
4. Confidence
5. Signal score
6. Action
7. Risk
8. Invalidation

## Definitions
- Facts: raw data only
- Interpretation: meaning of facts
- Signal: directional conclusion
- Confidence: data quality and alignment assessment
- Signal score: numeric directional mapping that must match signal language
- Action: what to do
- Risk: what could go wrong
- Invalidation: what breaks the thesis

## Rules
- Do not mix facts with interpretation
- Facts must be observable inputs, timestamps, levels, or directly quoted source outputs
- Statements such as "gold is not acting like a haven" belong in Interpretation unless paired with explicit measured evidence
- Interpretation must explain the meaning of facts and may not introduce uncited new facts
- Apply `assets/gold/framework/freshness_rules.md` before assigning confidence or tactical weight
- If core macro inputs are stale, confidence must be capped according to the freshness rules
- If timestamps across market and macro inputs are mixed, say so explicitly
- Signal language and signal score must agree
- A `0` signal score must use neutral language
- A bullish or bearish pressure note is allowed only if the text makes clear that the numeric score remains neutral
- Technical pivot levels are watch levels by default
- Do not use pivot-based levels as thesis invalidation or breakout confirmation unless they are independently confirmed
- If a pivot level is used tactically, label it explicitly as a watch level unless independent confirmation is documented
- Do not skip steps
- Reject outputs that violate structure
