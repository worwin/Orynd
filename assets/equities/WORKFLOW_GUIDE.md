# Equities Workflow Guide

## What this system is
This is the stock-analysis operating system for Buffett-style long-term investing.

It has:
- a shared framework in `assets/equities/framework/`
- portfolio-level files in `assets/equities/portfolio/`
- reusable tasks in `assets/equities/tasks/`
- one workspace per stock in `assets/equities/tickers/<TICKER>/`

## How to think about the tasks
You do not usually run every task manually in order unless you want maximum control.

There are two normal ways to use the system:
- raw filing sync plus review
- full workflow
- targeted task

## New filing ingestion layer
Before filing review, you can now sync raw SEC artifacts directly into the ticker workspace.

Use:
- `Run assets/equities/tasks/00_pull_edgar_filings.md for AAPL`
- `Pull EDGAR filings for AAPL`
- `Sync 10-K and 10-Q filings for MSFT`

## Full workflow
Use this when you want the whole company updated from research through decision and report.

Say:
- `Run assets/equities/tasks/update_company.md for AAPL`
- `Run the full equity workflow for MSFT`
- `Update company AAPL`

What that means operationally:
1. review company profile files
2. sync raw SEC filings if needed
3. extract normalized EDGAR facts if needed
4. build the filing review pack if needed
5. prepare engine inputs if needed
6. review filings
7. refresh analysis files
8. run Buffett entry/exit decision
9. run critic review
10. update position
11. generate final report

## Targeted task mode
Use this when only one part of the workflow needs to change.

Examples:
- `Run assets/equities/tasks/04_review_filings.md for AAPL`
- `Run assets/equities/tasks/06_run_buffett_entry_exit.md for BRK-B`
- `Run assets/equities/tasks/09_generate_final_report.md for V`

## What each task does

### Task 01
`01_audit_equities_repo.md`

Use when:
- you want to inspect what exists
- you want to see what is missing
- you want a repo health check

### Task 02
`02_create_company_workspace.md`

Use when:
- adding a new stock for the first time

You can say:
- `Create a company workspace for JPM`

### Task 00
`00_pull_edgar_filings.md`

Use when:
- you want to ingest primary SEC artifacts into the ticker workspace
- you want long filing history, not just one latest filing summary
- you want raw data available before running the filing review

### Task 00A
`00A_extract_edgar_facts.md`

Use when:
- you want statement-level JSON extracted from stored SEC artifacts
- you want Buffett-ready metrics before analysis and decision work
- you want `13F-HR` submission text parsed into holdings JSON

### Task 00B
`00B_build_filing_review_pack.md`

Use when:
- you want readable `10-K`, `10-Q`, `8-K`, and proxy review files built from stored SEC data
- you want accounting notes refreshed from the extracted filing history

### Task 00C
`00C_prepare_engine_inputs.md`

Use when:
- you want filing-derived data packaged for Buffett scoring or later prediction work
- you want analysis files grounded in the extracted SEC history

### Task 03
`03_populate_company_profile.md`

Use when:
- you want the slow-moving business understanding built out
- business model, moat, management, risks, and capital allocation need to be populated

### Task 04
`04_review_filings.md`

Use when:
- a new 10-K, 10-Q, 8-K, or proxy is out
- you want the primary-source evidence refreshed
- the raw EDGAR sync has already been run or you are about to run it

### Task 05
`05_build_long_term_analysis.md`

Use when:
- you want the broad investment memo
- fundamentals, valuation context, technical context, and sentiment need to be refreshed

### Task 06
`06_run_buffett_entry_exit.md`

Use when:
- you want the actual Buffett-style decision
- you want `BUY`, `HOLD`, `SELL`, or `INSUFFICIENT_DATA`
- you want entry prices, exit prices, and JSON output

### Task 07
`07_critic_review.md`

Use when:
- you want the thesis attacked
- you want accounting, moat, or valuation weaknesses surfaced

### Task 08
`08_update_position.md`

Use when:
- actual holdings changed
- the recommendation changed and you want the live position file updated

Important:
- this task must distinguish actual holdings from recommended action

### Task 09
`09_generate_final_report.md`

Use when:
- you want the final decision memo for the stock

## Do I say `run task 0-9`?
Not exactly.

The cleanest options are:
- `Run assets/equities/tasks/00_pull_edgar_filings.md for AAPL`
- `Run assets/equities/tasks/00A_extract_edgar_facts.md for AAPL`
- `Run assets/equities/tasks/00B_build_filing_review_pack.md for AAPL`
- `Run assets/equities/tasks/00C_prepare_engine_inputs.md for AAPL`
- `Run assets/equities/tasks/update_company.md for AAPL`
- `Run the full equity workflow for AAPL`
- `Run task 04 for AAPL`
- `Run task 06 for AAPL`

The current numbered task set is `00` through `09`.

## Recommended normal workflow

### First time covering a stock
1. Run task `02`
2. Run task `00`
3. Run task `00A`
4. Run task `00B`
5. Run task `00C`
6. Run task `03`
7. Run task `04`
8. Run task `05`
9. Run task `06`
10. Run task `07`
11. Run task `08`
12. Run task `09`

### Existing covered stock, normal refresh
1. Run `update_company.md`

### Earnings or filing refresh
1. Run task `00`
2. Run task `00A`
3. Run task `00B`
4. Run task `00C`
5. Run task `04`
6. Run task `05`
7. Run task `06`
8. Run task `07`
9. Run task `08` if needed
10. Run task `09`

### Holdings-only change
1. Run task `08`

## Best user commands
These are the most natural prompts to use with me:

- `Create a workspace for COST`
- `Run the full equity workflow for AAPL`
- `Run task 04 for MSFT`
- `Run Buffett entry/exit for BRK-B`
- `Generate the final report for V`
- `Update the position file for AAPL to 20 shares`

## What files matter most

### Slow-moving understanding
- `company_profile/`
- `filings/`

### Live analysis
- `analysis/`

### Action layer
- `decisions/buffett_decision.md`
- `decisions/buffett_decision.json`
- `trades/current_position.md`
- `reports/latest_report.md`

## Confidence guidance
For equities, confidence should come mainly from:
- filing coverage
- accounting clarity
- moat and management understanding
- valuation quality

It should not come mainly from:
- short-term price movement
- social sentiment
- technical indicators alone

## Practical rule of thumb
If you are unsure what to ask for, use:
- `Run the full equity workflow for <TICKER>`

That is the safest default.

