# Task 00A: Extract EDGAR Facts

## Goal
Convert stored SEC EDGAR artifacts into normalized JSON that downstream analysis can read reliably.

## Inputs
- existing `filings/edgar/normalized/filings_manifest.json`
- existing `filings/edgar/raw/companyfacts/*.json`
- stored `full_submission.txt` files when available

## Outputs
- `filings/edgar/extracted/extraction_manifest.json`
- `filings/edgar/extracted/extraction_summary.md`
- `filings/edgar/extracted/companyfacts/annual_statement_history.json`
- `filings/edgar/extracted/companyfacts/quarterly_statement_history.json`
- `filings/edgar/extracted/companyfacts/buffett_metric_history.json`
- `filings/edgar/extracted/companyfacts/latest_summary.json`
- `filings/edgar/extracted/13f/holdings_manifest.json` when `13F-HR` filings are present
- `filings/edgar/extracted/13f/by_filing/` when `13F-HR` filings are present

## Required command
```powershell
python assets/equities/scripts/extract_edgar_facts.py --ticker AAPL
```

## Rules
- Use the stored repo artifacts as the working memory.
- Prefer `companyfacts` for normalized statement history.
- Treat `full_submission.txt` as the canonical raw filing artifact.
- Treat SEC filing HTML and folder indexes as optional enrichment.
- Keep outputs filing-linked and machine-readable.
