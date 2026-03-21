# Task 08: Critic Review

## Goal
Evaluate the quality of the current gold decision and identify weaknesses in reasoning.

## Read
- all files under `assets/gold/`

## Do not edit
Do not modify any files.

## Evaluate
- Are facts correctly separated from interpretation?
- Are any inputs overweighted or ignored?
- Are there contradictions between macro, sentiment, and price?
- Is the signal justified by the evidence?
- Is the confidence level appropriate?
- Were freshness rules applied correctly?
- Were stale core macro inputs allowed to support confidence above the permitted cap?
- Does signal language agree with the numeric signal score?
- Are technical pivot levels labeled only as watch levels unless independently confirmed?

## Output
- Strengths of the current decision
- Weaknesses or blind spots
- Suggested improvements to reasoning
- Suggested improvements to the system itself

## Rules
- Be critical and precise
- Do not restate the decision without analysis
- Focus on improving decision quality
- Call out any facts that are actually interpretation
- Call out any confidence overstatement caused by stale or mismatched data
- Call out any mismatch between signal wording and signal score
