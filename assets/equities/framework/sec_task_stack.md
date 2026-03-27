# SEC Task Stack

## Purpose
Define the repeatable task order for SEC-driven equity coverage in this repo.

## Task stack
1. `00_pull_edgar_filings.md`
   Pull raw SEC filings and companyfacts into the ticker workspace.
2. `00A_extract_edgar_facts.md`
   Normalize stored SEC artifacts into machine-readable statement and metric history.
3. `00B_build_filing_review_pack.md`
   Produce human-readable filing review files from the raw and extracted SEC artifacts.
4. `00C_prepare_engine_inputs.md`
   Convert filing-derived outputs into stable analysis and engine-ready inputs.
5. `04_review_filings.md`
   Review the latest filings with the normalized context already in place.
6. `05_build_long_term_analysis.md`
   Build the investment memo and broader analysis layer.
7. `06_run_buffett_entry_exit.md`
   Generate the Buffett-style action decision.

## Why this order
- Raw memory lands first.
- Deterministic extraction happens before interpretation.
- Human-readable review happens before scoring or prediction.
- Engine inputs inherit the same source discipline and freshness checks.

## Current implementation status
- `00`: implemented
- `00A`: implemented
- `00B`: task defined, review-file generation to be expanded
- `00C`: task defined, engine-input packaging to be expanded
- `04` onward: existing workflow already present in repo
