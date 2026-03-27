# AGENTS.md

## Purpose
This repository is a lightweight trading operating system for discretionary macro analysis.
Supported assets:
- Gold, with `AAAU` as the primary execution vehicle
- Silver, with `SLV` as the primary execution vehicle
- Equities, with per-ticker workspaces under `assets/equities/tickers/`

## Core rules
- Do not invent market facts.
- Use repo files as the working memory.
- If a data file is stale or missing, say so explicitly.
- Keep long term thesis separate from current market state.

## Gold workflow
When asked to update gold:
1. Read `assets/gold/tasks/update_gold.md`
2. Inspect files in `assets/gold/data/`
3. Update `assets/gold/thesis/current_state.md`
4. Evaluate `assets/gold/signals/signal_rules.md`
5. Update `assets/gold/signals/signal_state.md`
6. Update `assets/gold/trades/current_position.md`
7. Add a dated note to `assets/gold/journal/notes.md`

## Silver workflow
When asked to update silver:
1. Read `assets/silver/tasks/update_silver.md`
2. Inspect files in `assets/silver/data/`
3. Update `assets/silver/thesis/current_state.md`
4. Evaluate `assets/silver/signals/signal_rules.md`
5. Update `assets/silver/signals/signal_state.md`
6. Update `assets/silver/trades/current_position.md`
7. Add a dated note to `assets/silver/journal/notes.md`

## Equities workflow
When asked to update a company:
1. Read `assets/equities/tasks/update_company.md`
2. Review the target ticker files under `assets/equities/tickers/`
3. Review the latest filings and company profile files
4. Refresh analysis files
5. Run the Buffett entry/exit decision
6. Update the ticker position file
7. Generate the ticker final report

## File roles
- `core_thesis.md` = slow moving model of how gold works
- `current_state.md` = current regime
- `signal_rules.md` = if then logic
- `signal_state.md` = current rule evaluation
- `current_position.md` = current stance in AAAU
- `trade_log.md` = closed or changed trade history

## Style
Be concise.
Separate facts, interpretation, signal status, and action.
Preserve history when possible.
