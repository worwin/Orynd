# Task 00: Pull EDGAR Filings

## Goal
Pull SEC EDGAR filings and store them in the ticker workspace in a standard structure.

## Why this exists
- Filing review should sit on top of raw primary-source artifacts.
- The repo should keep its own working memory per ticker.
- Buffett-style analysis needs filing history, not just one latest summary.

## Inputs
- ticker
- forms to sync, such as `10-K`, `10-Q`, `8-K`, `DEF 14A`
- optional lookback controls such as `limit` or `since`

## Output structure
- `filings/edgar/raw/submissions/`
- `filings/edgar/raw/companyfacts/`
- `filings/edgar/archive/<FORM>/<FILED_DATE>__<ACCESSION>/`
  - canonical raw artifact: `full_submission.txt`
  - optional enrichments: SEC filing HTML and folder index when available
- `filings/edgar/normalized/filings_manifest.json`
- `filings/edgar/normalized/latest_by_form.json`
- `filings/filing_index.md`

## Required command
```powershell
python assets/equities/scripts/sec_edgar_sync.py --ticker AAPL --forms 10-K --limit 20 --user-agent "Orynd Research you@example.com"
```

## Rules
- Use the SEC API and SEC archive paths directly.
- Declare a real SEC-compliant user agent on every run.
- Keep the request rate comfortably below the SEC fair-access limit.
- Store raw artifacts before attempting interpretation.
- Do not overwrite analytical review files such as `latest_10k.md`.

## Notes
- This task is the ingestion layer.
- `04_review_filings.md` is the interpretation layer that reads the synced artifacts.
