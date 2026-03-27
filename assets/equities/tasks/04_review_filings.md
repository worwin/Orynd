# Task 04: Review Filings

## Goal
Extract the important facts from the latest SEC filings.

## Prerequisite
- Run `assets/equities/tasks/00_pull_edgar_filings.md` first when raw EDGAR artifacts are stale or missing.
- Run `assets/equities/tasks/00A_extract_edgar_facts.md` when you want normalized statement history before review.
- Run `assets/equities/tasks/00B_build_filing_review_pack.md` when you want the readable filing files refreshed from stored SEC data.

## Read
- latest `10-K`
- latest `10-Q`
- latest material `8-K`
- latest `DEF 14A`

## Update
- `filing_index.md`
- `latest_10k.md`
- `latest_10q.md`
- `latest_8k.md`
- `proxy_def14a.md`
- `accounting_notes.md`

## Rules
- Use SEC filings as the primary source of truth.
- Prefer the synced artifacts in `filings/edgar/` over ad hoc browsing.
- Flag any unclear accounting treatment explicitly.
