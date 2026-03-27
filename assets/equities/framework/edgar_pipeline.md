# EDGAR Pipeline

## Objective
Build a repo-native, agent-friendly SEC filing pipeline for each covered equity ticker.

## Design principles
- Primary source first: raw SEC data lands before any interpretation.
- File-first memory: data lives under the ticker workspace, not in an external database.
- Standard structure: every ticker uses the same folder layout and manifest files.
- Two-stage workflow: ingestion and extraction are separate from analysis and decision.

## Stage 1: Ingestion
Pull filings and XBRL metadata directly from SEC endpoints.

### Sources
- `https://www.sec.gov/files/company_tickers.json`
- `https://data.sec.gov/submissions/CIK##########.json`
- `https://data.sec.gov/submissions/<historical-submissions-file>.json`
- `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`
- `https://www.sec.gov/Archives/edgar/data/<CIK>/<ACCESSION>/index.json`
- `https://www.sec.gov/Archives/edgar/data/<CIK>/<ACCESSION>/<primary document>`
- `https://www.sec.gov/Archives/edgar/data/<CIK>/<ACCESSION>/<accession>.txt`

### Per-ticker layout
- `filings/edgar/raw/submissions/`: SEC submissions payloads
- `filings/edgar/raw/companyfacts/`: raw XBRL companyfacts payload
- `filings/edgar/archive/`: one folder per filing with raw artifacts; `full_submission.txt` is the canonical baseline artifact
- `filings/edgar/normalized/filings_manifest.json`: stable machine-readable manifest
- `filings/edgar/normalized/latest_by_form.json`: quick lookup for downstream tasks

## Stage 2: Extraction
Convert raw SEC artifacts into statement-level, rule-ready data.

### Planned outputs
- normalized annual statement snapshots
- normalized quarterly statement snapshots
- accounting issue register
- Buffett metric history keyed by filing date

### Extraction strategy
- Start from `companyfacts` for consistent XBRL-tagged series.
- Use `full_submission.txt` as the baseline raw filing source when HTML/index fetches are unavailable.
- Use filing HTML and filing folder indexes as optional enrichment when XBRL coverage is incomplete or presentation-specific context matters.
- Keep extracted outputs versioned and filing-linked so agents can trace every metric back to a source filing.

## Stage 3: Review and decision
- `04_review_filings.md` reads the synced artifacts and updates review markdown.
- `05_build_long_term_analysis.md` and `06_run_buffett_entry_exit.md` consume extracted facts, not ad hoc web lookups.

## Why not a database first
- The repo is already the operating system and working memory.
- JSON plus markdown is easier to diff, audit, and use in GitHub.
- A database can still be added later if derived analytics outgrow the file-first model.

## Agentic fit
- A sync task can refresh primary-source memory on demand.
- A later extraction task can be deterministic and repeatable.
- Analysis tasks can stay focused on interpretation, scoring, and decision quality.
