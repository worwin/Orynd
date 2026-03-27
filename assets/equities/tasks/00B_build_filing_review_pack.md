# Task 00B: Build Filing Review Pack

## Goal
Turn stored SEC filings and extracted facts into human-readable review files for the ticker workspace.

## Inputs
- `filings/edgar/normalized/filings_manifest.json`
- `filings/edgar/extracted/companyfacts/*.json`
- latest filing folders under `filings/edgar/archive/`

## Update
- `filing_index.md`
- `latest_10k.md`
- `latest_10q.md`
- `latest_8k.md`
- `proxy_def14a.md`
- `accounting_notes.md`
- `latest_13f.md` when `13F-HR` filings are present

## Required sections
- Facts
- Interpretation
- Accounting flags
- Missing data or stale coverage
- Source filings used

## Required command
```powershell
python assets/equities/scripts/build_filing_review_pack.py --ticker AAPL
```

## Rules
- Prefer extracted JSON for repeatable metrics and trend checks.
- Use `full_submission.txt` and primary filing documents for context, disclosures, and edge cases.
- Separate facts from interpretation.
- Flag unclear accounting treatments explicitly.
- Preserve historical context when the latest filing changes an earlier understanding.

## Notes
- This task is the human-readable bridge between raw SEC memory and the Buffett decision layer.
- `04_review_filings.md` should point to this process conceptually even if the final implementation lives there.
- For 13F filers, the review pack should summarize holdings concentration and recent filing history even when operating-company filing types are absent.
