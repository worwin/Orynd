# Task 08: Critic Review

## Goal
Evaluate the quality of the current gold decision and identify weaknesses in reasoning.

## Read
- all files under `assets/gold/`
- `assets/gold/framework/decision_protocol.md`
- `assets/gold/framework/scoring.md`
- `assets/gold/framework/freshness_rules.md`

## Do not edit
Do not modify any files.

## Evaluate
- Are facts correctly separated from interpretation?
- Are there any freshness violations, including stale macro inputs being used as tactical drivers?
- Are there any confidence violations, including confidence set too high for the data quality?
- Are any inputs overweighted or ignored?
- Are there contradictions between macro, sentiment, and price?
- Is the signal justified by the evidence?
- Is the confidence level appropriate?
- Were freshness rules applied correctly?
- Were stale core macro inputs allowed to support confidence above the permitted cap?
- Does signal language agree with the numeric signal score?
- Are technical pivot levels labeled only as watch levels unless independently confirmed?
- Is there any improper use of technical levels?
- Is there any mixing of facts and interpretation?

## Output
- Strengths of the current decision
- Weaknesses or blind spots
- Severity levels: high, medium, low
- Explicit recommendation: downgrade confidence, change score, or keep as-is
- Suggested improvements to reasoning
- Suggested improvements to the system itself

## Rules
- Be critical and precise
- Do not restate the decision without analysis
- Focus on improving decision quality
- Call out any facts that are actually interpretation
- Call out any confidence overstatement caused by stale or mismatched data
- Call out any mismatch between signal wording and signal score
- Call out any missing or weak data freshness assessment
- Assign a severity level to each major weakness
- End with an explicit recommendation: downgrade confidence, change score, or keep as-is
