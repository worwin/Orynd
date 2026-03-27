#!/usr/bin/env python3
"""Build human-readable filing review files from stored SEC artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
TICKERS_ROOT = REPO_ROOT / "assets" / "equities" / "tickers"

ITEM_LABELS = {
    "1.01": "Entry into a Material Definitive Agreement",
    "1.02": "Termination of a Material Definitive Agreement",
    "2.02": "Results of Operations and Financial Condition",
    "2.05": "Costs Associated with Exit or Disposal Activities",
    "2.06": "Material Impairments",
    "3.01": "Notice of Delisting or Failure to Satisfy Listing Rule",
    "3.02": "Unregistered Sales of Equity Securities",
    "4.02": "Non-Reliance on Previously Issued Financial Statements",
    "5.02": "Departure or Appointment of Directors or Certain Officers",
    "5.03": "Amendments to Articles or Bylaws",
    "5.05": "Amendments to Code of Ethics or Waiver",
    "5.07": "Submission of Matters to a Vote of Security Holders",
    "7.01": "Regulation FD Disclosure",
    "8.01": "Other Events",
    "9.01": "Financial Statements and Exhibits",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", required=True, help="Ticker workspace to update, e.g. AAPL")
    parser.add_argument("--recent-8k-limit", type=int, default=12, help="How many recent 8-K filings to summarize.")
    parser.add_argument("--recent-proxy-limit", type=int, default=8, help="How many recent DEF 14A filings to summarize.")
    parser.add_argument("--recent-13f-limit", type=int, default=8, help="How many recent 13F filings to summarize.")
    parser.add_argument("--top-holdings-limit", type=int, default=15, help="How many top 13F positions to display.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fmt_int(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{int(value):,}"


def fmt_money(value: Any) -> str:
    if value is None:
        return "N/A"
    value = float(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000_000:
        return f"{sign}${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.2f}M"
    return f"{sign}${value:,.0f}"


def fmt_thousands_usd(value: Any) -> str:
    if value is None:
        return "N/A"
    return fmt_money(float(value) * 1000.0)


def fmt_pct(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value):.2f}%"


def fmt_ratio(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value):.2f}x"


def safe_div(a: Any, b: Any) -> float | None:
    if a is None or b in (None, 0):
        return None
    return float(a) / float(b)


def pct_change(current: Any, prior: Any) -> float | None:
    if current is None or prior in (None, 0):
        return None
    return ((float(current) - float(prior)) / float(prior)) * 100.0


def cagr(current: Any, prior: Any, periods: int) -> float | None:
    if current is None or prior in (None, 0) or periods <= 0:
        return None
    if float(current) <= 0 or float(prior) <= 0:
        return None
    return ((float(current) / float(prior)) ** (1.0 / periods) - 1.0) * 100.0


def days_old(date_str: str | None) -> int | None:
    if not date_str:
        return None
    try:
        filed = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (datetime.now(timezone.utc).date() - filed).days


def freshness_label(days: int | None, annual: bool = False) -> str:
    if days is None:
        return "Unknown"
    if annual:
        if days <= 450:
            return "Fresh"
        if days <= 550:
            return "Watch"
        return "Stale"
    if days <= 120:
        return "Fresh"
    if days <= 180:
        return "Watch"
    return "Stale"


def get_recent_records(records: list[dict[str, Any]], form: str, limit: int | None = None) -> list[dict[str, Any]]:
    filtered = [record for record in records if record.get("form") == form]
    filtered.sort(key=lambda r: (r.get("filing_date", ""), r.get("acceptance_datetime", "")), reverse=True)
    return filtered if limit is None else filtered[:limit]


def item_labels(items: str) -> str:
    if not items:
        return "N/A"
    labels = []
    for item in [part.strip() for part in items.split(",") if part.strip()]:
        label = ITEM_LABELS.get(item, "Unknown item")
        labels.append(f"{item} ({label})")
    return "; ".join(labels)


def rel_path(path_str: str | None) -> str:
    return path_str or "N/A"


def latest_full_submission(record: dict[str, Any]) -> str:
    return rel_path(record.get("local_paths", {}).get("full_submission_txt"))


def latest_primary_doc(record: dict[str, Any]) -> str:
    return rel_path(record.get("local_paths", {}).get("primary_document"))




def build_annual_review_table(annual_records: list[dict[str, Any]], buffett_map: dict[str, dict[str, Any]], limit: int) -> str:
    subset = annual_records[-limit:] if len(annual_records) > limit else annual_records
    lines = [
        "| Period End | Revenue | Net income | OCF | FCF | Gross margin | Operating margin |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for record in subset:
        buffett = buffett_map.get(record.get("period_end"), {})
        lines.append(
            "| "
            + " | ".join(
                [
                    record.get("period_end", ""),
                    fmt_money(record.get("metrics", {}).get("revenue")),
                    fmt_money(record.get("metrics", {}).get("net_income")),
                    fmt_money(record.get("metrics", {}).get("operating_cash_flow")),
                    fmt_money(buffett.get("free_cash_flow")),
                    fmt_pct(buffett.get("gross_margin_pct")),
                    fmt_pct(buffett.get("operating_margin_pct")),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def build_trend_table(records: list[dict[str, Any]], fields: list[tuple[str, str, str]], limit: int) -> str:
    subset = records[-limit:] if len(records) > limit else records
    headers = ["Period End"] + [label for label, _, _ in fields]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for record in subset:
        row = [record.get("period_end", "")]
        metrics = record.get("metrics", {})
        for _, key, kind in fields:
            value = metrics.get(key)
            if kind == "money":
                row.append(fmt_money(value))
            elif kind == "pct":
                row.append(fmt_pct(value))
            elif kind == "int":
                row.append(fmt_int(value))
            else:
                row.append(str(value) if value is not None else "N/A")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def annual_metric_lookup(buffett_history: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["period_end"]: record for record in buffett_history.get("records", [])}


def status_label(kind: str, value: float | None) -> str:
    if value is None:
        return "Needs review"
    if kind == "revenue_quality":
        return "Strong" if value >= 0 else "Weak"
    if kind == "cash_conversion":
        return "Strong" if value >= 1.0 else "Mixed"
    if kind == "sbc_pct_ocf":
        return "Strong" if value <= 5 else ("Mixed" if value <= 10 else "Weak")
    if kind == "share_count_change":
        return "Strong" if value < 0 else ("Mixed" if value <= 2 else "Weak")
    if kind == "current_ratio":
        return "Strong" if value >= 1.25 else ("Mixed" if value >= 1.0 else "Weak")
    if kind == "debt_to_ocf":
        return "Strong" if value <= 1.0 else ("Mixed" if value <= 2.0 else "Weak")
    if kind == "capex_ratio":
        return "Strong" if value <= 5 else ("Mixed" if value <= 10 else "Weak")
    return "Needs review"


def build_accounting_notes(latest_annual: dict[str, Any], prior_annual: dict[str, Any] | None, latest_buffett: dict[str, Any]) -> str:
    metrics = latest_annual.get("metrics", {})
    revenue = metrics.get("revenue")
    net_income = metrics.get("net_income")
    ocf = metrics.get("operating_cash_flow")
    capex = metrics.get("capex")
    sbc = metrics.get("share_based_compensation")
    current_assets = metrics.get("current_assets")
    current_liabilities = metrics.get("current_liabilities")
    long_term_debt = metrics.get("long_term_debt")
    diluted_shares = metrics.get("diluted_weighted_shares")
    prior_revenue = prior_annual.get("metrics", {}).get("revenue") if prior_annual else None
    prior_shares = prior_annual.get("metrics", {}).get("diluted_weighted_shares") if prior_annual else None

    revenue_growth = pct_change(revenue, prior_revenue)
    cash_conversion = safe_div(ocf, net_income)
    sbc_pct_ocf = safe_div(sbc, ocf)
    share_change = pct_change(diluted_shares, prior_shares)
    current_ratio = safe_div(current_assets, current_liabilities)
    debt_to_ocf = safe_div(long_term_debt, ocf)
    capex_ratio = safe_div(capex, revenue)

    lines = [
        "# Accounting Notes",
        "",
        "## Revenue quality",
        f"- Status: `{status_label('revenue_quality', revenue_growth)}`",
        f"- Latest annual revenue: `{fmt_money(revenue)}`",
        f"- Year-over-year revenue change: `{fmt_pct(revenue_growth)}`",
        f"- Gross margin: `{fmt_pct(latest_buffett.get('gross_margin_pct'))}`",
        "",
        "## Cash conversion",
        f"- Status: `{status_label('cash_conversion', cash_conversion)}`",
        f"- Operating cash flow: `{fmt_money(ocf)}`",
        f"- Net income: `{fmt_money(net_income)}`",
        f"- OCF / net income: `{fmt_ratio(cash_conversion)}`",
        f"- Free cash flow: `{fmt_money(latest_buffett.get('free_cash_flow'))}`",
        f"- FCF margin: `{fmt_pct(latest_buffett.get('fcf_margin_pct'))}`",
        "",
        "## Stock compensation",
        f"- Status: `{status_label('sbc_pct_ocf', None if sbc_pct_ocf is None else sbc_pct_ocf * 100)}`",
        f"- Share-based compensation: `{fmt_money(sbc)}`",
        f"- SBC as % of operating cash flow: `{fmt_pct(None if sbc_pct_ocf is None else sbc_pct_ocf * 100)}`",
        "",
        "## Share count",
        f"- Status: `{status_label('share_count_change', share_change)}`",
        f"- Diluted weighted shares: `{fmt_int(diluted_shares)}`",
        f"- Year-over-year diluted share change: `{fmt_pct(share_change)}`",
        "",
        "## Working capital",
        f"- Status: `{status_label('current_ratio', current_ratio)}`",
        f"- Current assets: `{fmt_money(current_assets)}`",
        f"- Current liabilities: `{fmt_money(current_liabilities)}`",
        f"- Current ratio: `{fmt_ratio(current_ratio)}`",
        "",
        "## One-time items",
        "- Status: `Needs review`",
        "- Companyfacts does not reliably isolate recurring versus one-time charges.",
        "- Use the latest 10-K and 10-Q text review for adjustments, restructuring, litigation, or tax one-offs.",
        "",
        "## Debt maturity and burden",
        f"- Status: `{status_label('debt_to_ocf', debt_to_ocf)}`",
        f"- Long-term debt: `{fmt_money(long_term_debt)}`",
        f"- Debt / operating cash flow: `{fmt_ratio(debt_to_ocf)}`",
        f"- Debt / equity: `{fmt_ratio(latest_buffett.get('de_ratio'))}`",
        "",
        "## Maintenance versus growth capex",
        f"- Status: `{status_label('capex_ratio', None if capex_ratio is None else capex_ratio * 100)}`",
        f"- Capital expenditures: `{fmt_money(capex)}`",
        f"- Capex as % of revenue: `{fmt_pct(None if capex_ratio is None else capex_ratio * 100)}`",
        f"- Free cash flow remains `{fmt_money(latest_buffett.get('free_cash_flow'))}` after capex.",
        "",
        "## Source base",
        f"- Latest annual period end: `{latest_annual.get('period_end')}`",
        f"- Latest annual filing date: `{latest_annual.get('latest_filed')}`",
        "- Primary source set: `filings/edgar/extracted/companyfacts/` plus latest filing text in `filings/edgar/archive/`.",
    ]
    return "\n".join(lines) + "\n"


def build_10k_review(ticker_root: Path, latest_10k: dict[str, Any], annual_history: dict[str, Any], buffett_history: dict[str, Any]) -> str:
    annual_records = annual_history.get("records", [])
    latest_annual = annual_records[-1]
    prior_annual = annual_records[-2] if len(annual_records) >= 2 else None
    prior3_annual = annual_records[-4] if len(annual_records) >= 4 else None
    buffett_map = annual_metric_lookup(buffett_history)
    latest_buffett = buffett_map.get(latest_annual["period_end"], {})

    revenue_3y_cagr = cagr(latest_annual["metrics"].get("revenue"), prior3_annual["metrics"].get("revenue") if prior3_annual else None, 3)
    share_3y_change = pct_change(latest_annual["metrics"].get("diluted_weighted_shares"), prior3_annual["metrics"].get("diluted_weighted_shares") if prior3_annual else None)
    freshness = freshness_label(days_old(latest_10k.get("filing_date")), annual=True)

    lines = [
        "# Latest 10-K Review",
        "",
        "## Filing",
        f"- Filed date: `{latest_10k.get('filing_date')}`",
        f"- Report period end: `{latest_10k.get('report_date')}`",
        f"- Accession: `{latest_10k.get('accession_number')}`",
        f"- Freshness: `{freshness}`",
        f"- Full submission text: `{latest_full_submission(latest_10k)}`",
        f"- Primary document path: `{latest_primary_doc(latest_10k)}`",
        "",
        "## Facts",
        f"- Revenue: `{fmt_money(latest_annual['metrics'].get('revenue'))}`",
        f"- Gross profit: `{fmt_money(latest_annual['metrics'].get('gross_profit'))}`",
        f"- Operating income: `{fmt_money(latest_annual['metrics'].get('operating_income'))}`",
        f"- Net income: `{fmt_money(latest_annual['metrics'].get('net_income'))}`",
        f"- Operating cash flow: `{fmt_money(latest_annual['metrics'].get('operating_cash_flow'))}`",
        f"- Capital expenditures: `{fmt_money(latest_annual['metrics'].get('capex'))}`",
        f"- Free cash flow: `{fmt_money(latest_buffett.get('free_cash_flow'))}`",
        f"- Gross margin: `{fmt_pct(latest_buffett.get('gross_margin_pct'))}`",
        f"- Operating margin: `{fmt_pct(latest_buffett.get('operating_margin_pct'))}`",
        f"- Return on equity: `{fmt_pct(latest_buffett.get('roe_pct'))}`",
        f"- Return on assets: `{fmt_pct(latest_buffett.get('roa_pct'))}`",
        f"- Cash and equivalents: `{fmt_money(latest_annual['metrics'].get('cash_and_equivalents'))}`",
        f"- Long-term debt: `{fmt_money(latest_annual['metrics'].get('long_term_debt'))}`",
        f"- Stockholders' equity: `{fmt_money(latest_annual['metrics'].get('stockholders_equity'))}`",
        f"- Current ratio: `{fmt_ratio(latest_buffett.get('current_ratio'))}`",
        f"- Debt / equity: `{fmt_ratio(latest_buffett.get('de_ratio'))}`",
        "",
        "## Recent annual trend",
        build_annual_review_table(annual_records, buffett_map, 5),
        "",
        "## Interpretation",
        f"- Three-year revenue CAGR is `{fmt_pct(revenue_3y_cagr)}` across the latest annual base.",
        f"- Three-year diluted share change is `{fmt_pct(share_3y_change)}`, which helps frame buyback versus dilution behavior.",
        f"- Current ratio sits at `{fmt_ratio(latest_buffett.get('current_ratio'))}`; this is workable for Apple but should still be monitored rather than ignored.",
        f"- Debt / equity is `{fmt_ratio(latest_buffett.get('de_ratio'))}` while annual free cash flow is `{fmt_money(latest_buffett.get('free_cash_flow'))}`, so leverage should be read alongside cash generation rather than in isolation.",
        "",
        "## Accounting flags",
        f"- Revenue quality: gross margin `{fmt_pct(latest_buffett.get('gross_margin_pct'))}` and three-year revenue CAGR `{fmt_pct(revenue_3y_cagr)}`.",
        f"- Cash conversion: operating cash flow `{fmt_money(latest_annual['metrics'].get('operating_cash_flow'))}` against net income `{fmt_money(latest_annual['metrics'].get('net_income'))}`.",
        f"- Stock compensation: `{fmt_money(latest_annual['metrics'].get('share_based_compensation'))}` with SBC / OCF `{fmt_pct(latest_buffett.get('sbc_as_pct_of_ocf'))}`.",
        f"- Share count: diluted shares `{fmt_int(latest_annual['metrics'].get('diluted_weighted_shares'))}` in the latest annual period.",
        f"- Working capital: current assets `{fmt_money(latest_annual['metrics'].get('current_assets'))}` versus current liabilities `{fmt_money(latest_annual['metrics'].get('current_liabilities'))}`.",
        "- One-time items and recurring adjustments still need manual text review from the filing body.",
        "",
        "## Missing data or coverage notes",
        "- Full submission text is stored and should be treated as the canonical raw annual filing artifact.",
        "- SEC archive HTML and folder index were not always retrievable; those are optional enrichments, not blockers.",
        "",
        "## Sources used",
        f"- `filings/edgar/extracted/companyfacts/annual_statement_history.json`",
        f"- `filings/edgar/extracted/companyfacts/buffett_metric_history.json`",
        f"- `{latest_full_submission(latest_10k)}`",
    ]
    return "\n".join(lines) + "\n"


def build_10q_review(latest_10q: dict[str, Any], latest_summary: dict[str, Any], quarterly_history: dict[str, Any]) -> str:
    latest_quarter = latest_summary.get("latest_quarter_snapshot", {})
    records = quarterly_history.get("records", [])
    prior_quarter = records[-2] if len(records) >= 2 else None
    metrics = latest_quarter.get("metrics", {})
    freshness = freshness_label(days_old(latest_10q.get("filing_date")), annual=False)

    revenue_change = pct_change(metrics.get("revenue"), prior_quarter.get("metrics", {}).get("revenue") if prior_quarter else None)
    net_income_change = pct_change(metrics.get("net_income"), prior_quarter.get("metrics", {}).get("net_income") if prior_quarter else None)
    ocf_change = pct_change(metrics.get("operating_cash_flow"), prior_quarter.get("metrics", {}).get("operating_cash_flow") if prior_quarter else None)
    fcf = None
    if metrics.get("operating_cash_flow") is not None and metrics.get("capex") is not None:
        fcf = metrics.get("operating_cash_flow") - metrics.get("capex")

    lines = [
        "# Latest 10-Q Review",
        "",
        "## Filing",
        f"- Filed date: `{latest_10q.get('filing_date')}`",
        f"- Report period end: `{latest_10q.get('report_date')}`",
        f"- Accession: `{latest_10q.get('accession_number')}`",
        f"- Freshness: `{freshness}`",
        f"- Full submission text: `{latest_full_submission(latest_10q)}`",
        "",
        "## Facts",
        f"- Revenue: `{fmt_money(metrics.get('revenue'))}`",
        f"- Gross profit: `{fmt_money(metrics.get('gross_profit'))}`",
        f"- Operating income: `{fmt_money(metrics.get('operating_income'))}`",
        f"- Net income: `{fmt_money(metrics.get('net_income'))}`",
        f"- Operating cash flow: `{fmt_money(metrics.get('operating_cash_flow'))}`",
        f"- Capital expenditures: `{fmt_money(metrics.get('capex'))}`",
        f"- Free cash flow: `{fmt_money(fcf)}`",
        f"- Buybacks: `{fmt_money(metrics.get('buybacks'))}`",
        f"- Dividends paid: `{fmt_money(metrics.get('dividends_paid'))}`",
        f"- Cash and equivalents: `{fmt_money(metrics.get('cash_and_equivalents'))}`",
        f"- Long-term debt: `{fmt_money(metrics.get('long_term_debt'))}`",
        f"- Stockholders' equity: `{fmt_money(metrics.get('stockholders_equity'))}`",
        "",
        "## Recent quarterly trend",
        build_trend_table(records, [("Revenue", "revenue", "money"), ("Net income", "net_income", "money"), ("OCF", "operating_cash_flow", "money"), ("Buybacks", "buybacks", "money")], 4),
        "",
        "## Interpretation",
        f"- Revenue change versus the prior extracted quarter in the stored series is `{fmt_pct(revenue_change)}`. Read this with seasonality and quarter alignment in mind.",
        f"- Net income change versus the prior extracted quarter in the stored series is `{fmt_pct(net_income_change)}`.",
        f"- Operating cash flow change versus the prior extracted quarter in the stored series is `{fmt_pct(ocf_change)}`.",
        f"- The quarter still shows positive free cash flow of `{fmt_money(fcf)}` after capex.",
        "",
        "## Accounting flags",
        f"- Cash generation remains positive with operating cash flow `{fmt_money(metrics.get('operating_cash_flow'))}`.",
        f"- Capital returns remain active with buybacks `{fmt_money(metrics.get('buybacks'))}` and dividends `{fmt_money(metrics.get('dividends_paid'))}`.",
        f"- Liquidity snapshot: cash `{fmt_money(metrics.get('cash_and_equivalents'))}`, current assets `{fmt_money(metrics.get('current_assets'))}`, current liabilities `{fmt_money(metrics.get('current_liabilities'))}`.",
        "- Quarter-only views can hide one-time items; pair this file with the annual base and latest 8-K stream.",
        "",
        "## Missing data or coverage notes",
        "- This file is built from extracted statement data plus the stored filing text, not from a full narrative parser.",
        "- Management commentary, segment nuances, and litigation language still require direct text review when they matter.",
        "",
        "## Sources used",
        "- `filings/edgar/extracted/companyfacts/quarterly_statement_history.json`",
        "- `filings/edgar/extracted/companyfacts/latest_summary.json`",
        f"- `{latest_full_submission(latest_10q)}`",
    ]
    return "\n".join(lines) + "\n"


def build_8k_review(records: list[dict[str, Any]], limit: int) -> str:
    latest_8k = records[0]
    table_lines = ["| Filed | Report date | Items | Interpretation cue | Full submission |", "| --- | --- | --- | --- | --- |"]
    for record in records[:limit]:
        items = record.get("items", "")
        table_lines.append(
            "| "
            + " | ".join(
                [
                    record.get("filing_date", "N/A"),
                    record.get("report_date", "N/A"),
                    items or "N/A",
                    item_labels(items),
                    latest_full_submission(record),
                ]
            )
            + " |"
        )

    lines = [
        "# Latest 8-K Review",
        "",
        "## Latest filing",
        f"- Filed date: `{latest_8k.get('filing_date')}`",
        f"- Report date: `{latest_8k.get('report_date')}`",
        f"- Accession: `{latest_8k.get('accession_number')}`",
        f"- Item codes: `{latest_8k.get('items') or 'N/A'}`",
        f"- Item labels: `{item_labels(latest_8k.get('items', ''))}`",
        f"- Full submission text: `{latest_full_submission(latest_8k)}`",
        "",
        "## Recent 8-K timeline",
        "\n".join(table_lines),
        "",
        "## Interpretation",
        f"- The latest 8-K is dominated by `{item_labels(latest_8k.get('items', ''))}`, which should be read as an event update rather than a full annual business refresh.",
        "- 8-K filings matter most when they change leadership, governance, reporting integrity, capital structure, or the operating outlook.",
        f"- The recent 8-K stream is large; this file is meant to reduce noise by surfacing dates, item codes, and the raw text path quickly.",
        "",
        "## Missing data or coverage notes",
        "- Item codes come from SEC submissions metadata and are reliable for triage.",
        "- A narrative event classifier is not yet implemented, so human review still matters for material 8-Ks.",
        "",
        "## Sources used",
        "- `filings/edgar/normalized/filings_manifest.json`",
        f"- `{latest_full_submission(latest_8k)}`",
    ]
    return "\n".join(lines) + "\n"


def build_proxy_review(records: list[dict[str, Any]], limit: int) -> str:
    latest_proxy = records[0]
    table_lines = ["| Filed | SEC report date | Accession | Full submission |", "| --- | --- | --- | --- |"]
    for record in records[:limit]:
        table_lines.append(
            "| "
            + " | ".join(
                [
                    record.get("filing_date", "N/A"),
                    record.get("report_date", "N/A"),
                    record.get("accession_number", "N/A"),
                    latest_full_submission(record),
                ]
            )
            + " |"
        )

    lines = [
        "# Proxy / DEF 14A Review",
        "",
        "## Latest filing",
        f"- Filed date: `{latest_proxy.get('filing_date')}`",
        f"- SEC report date field: `{latest_proxy.get('report_date')}`",
        f"- Accession: `{latest_proxy.get('accession_number')}`",
        f"- Filing description: `{latest_proxy.get('primary_doc_description')}`",
        f"- Full submission text: `{latest_full_submission(latest_proxy)}`",
        "",
        "## What this filing is for",
        "- Board and governance review",
        "- Executive compensation and incentive alignment",
        "- Shareholder meeting matters and vote context",
        "- Equity-plan or proposal changes that can affect dilution or governance quality",
        "",
        "## Recent proxy history",
        "\n".join(table_lines),
        "",
        "## Interpretation",
        "- The proxy should drive management-quality and governance inputs more than any other filing in the set.",
        "- This file is fresh enough to use for current governance review, but detailed compensation-table parsing is still pending.",
        "- When confidence depends on incentives or insider alignment, this filing deserves direct reading even if the rest of the engine is automated.",
        "",
        "## Missing data or coverage notes",
        "- Governance metadata is stored, but a structured parser for pay tables, director refresh, and proposal outcomes is not yet implemented.",
        "- Until that parser exists, the proxy should be treated as a partially structured source rather than a fully normalized one.",
        "",
        "## Sources used",
        "- `filings/edgar/normalized/filings_manifest.json`",
        f"- `{latest_full_submission(latest_proxy)}`",
    ]
    return "\n".join(lines) + "\n"


def load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def get_recent_13f_filings(thirteen_f_manifest: dict[str, Any], limit: int | None = None) -> list[dict[str, Any]]:
    filings = [filing for filing in thirteen_f_manifest.get("filings", []) if filing.get("status") == "parsed"]
    filings.sort(key=lambda filing: filing.get("filing_date", ""), reverse=True)
    return filings if limit is None else filings[:limit]


def load_13f_payload(ticker_root: Path, filing: dict[str, Any]) -> dict[str, Any] | None:
    output_path = filing.get("output_path")
    if not output_path:
        return None
    target = ticker_root / Path(output_path)
    if not target.exists():
        return None
    return load_json(target)


def build_13f_top_holdings_table(holdings: list[dict[str, Any]], total_value_thousands: float, limit: int) -> str:
    ranked = sorted(
        holdings,
        key=lambda holding: (
            holding.get("value_thousands_usd") or 0,
            holding.get("name_of_issuer") or "",
        ),
        reverse=True,
    )[:limit]
    lines = [
        "| Issuer | Class | CUSIP | Reported value | Portfolio weight | Shares | Discretion |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for holding in ranked:
        value = holding.get("value_thousands_usd")
        weight = None if value in (None, 0) or total_value_thousands in (None, 0) else (float(value) / float(total_value_thousands)) * 100.0
        lines.append(
            "| "
            + " | ".join(
                [
                    holding.get("name_of_issuer") or "N/A",
                    holding.get("title_of_class") or "N/A",
                    holding.get("cusip") or "N/A",
                    fmt_thousands_usd(value),
                    fmt_pct(weight),
                    fmt_int(holding.get("share_amount")),
                    holding.get("investment_discretion") or "N/A",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def build_13f_history_table(filings: list[dict[str, Any]]) -> str:
    lines = [
        "| Filed | Form | Holdings | Parsed file |",
        "| --- | --- | --- | --- |",
    ]
    for filing in filings:
        lines.append(
            "| "
            + " | ".join(
                [
                    filing.get("filing_date", "N/A"),
                    filing.get("form", "N/A"),
                    fmt_int(filing.get("holdings_count")),
                    filing.get("output_path", "N/A"),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def build_13f_review(
    latest_13f_record: dict[str, Any] | None,
    ticker_root: Path,
    thirteen_f_manifest: dict[str, Any],
    recent_limit: int,
    top_holdings_limit: int,
) -> str:
    recent_filings = get_recent_13f_filings(thirteen_f_manifest)
    latest_filing = recent_filings[0]
    latest_payload = load_13f_payload(ticker_root, latest_filing)
    if latest_payload is None:
        raise SystemExit("Latest parsed 13F payload could not be loaded.")

    prior_payload = load_13f_payload(ticker_root, recent_filings[1]) if len(recent_filings) >= 2 else None
    holdings = latest_payload.get("holdings", [])
    total_value_thousands = sum((holding.get("value_thousands_usd") or 0) for holding in holdings)
    ranked_holdings = sorted(holdings, key=lambda holding: holding.get("value_thousands_usd") or 0, reverse=True)
    top1_value = ranked_holdings[0].get("value_thousands_usd") if ranked_holdings else None
    top5_value = sum((holding.get("value_thousands_usd") or 0) for holding in ranked_holdings[:5]) if ranked_holdings else 0
    top1_weight = None if top1_value in (None, 0) or total_value_thousands in (None, 0) else (float(top1_value) / float(total_value_thousands)) * 100.0
    top5_weight = None if total_value_thousands in (None, 0) else (float(top5_value) / float(total_value_thousands)) * 100.0

    prior_total_value = None
    prior_holdings_count = None
    if prior_payload is not None:
        prior_holdings = prior_payload.get("holdings", [])
        prior_total_value = sum((holding.get("value_thousands_usd") or 0) for holding in prior_holdings)
        prior_holdings_count = len(prior_holdings)

    holdings_count_change = None
    total_value_change = None
    if prior_holdings_count not in (None, 0):
        holdings_count_change = ((len(holdings) - prior_holdings_count) / prior_holdings_count) * 100.0
    if prior_total_value not in (None, 0):
        total_value_change = ((total_value_thousands - prior_total_value) / prior_total_value) * 100.0

    lines = [
        "# Latest 13F-HR Review",
        "",
        "## Filing",
        f"- Filed date: `{latest_filing.get('filing_date')}`",
        f"- Form: `{latest_filing.get('form')}`",
        f"- Accession: `{latest_filing.get('accession_number')}`",
        f"- Holdings parsed: `{fmt_int(latest_payload.get('holdings_count'))}`",
        f"- Full submission text: `{latest_full_submission(latest_13f_record or {})}`",
        f"- Parsed holdings JSON: `{latest_filing.get('output_path', 'N/A')}`",
        "",
        "## Facts",
        f"- Reported market value: `{fmt_thousands_usd(total_value_thousands)}`",
        f"- Number of line items: `{fmt_int(len(holdings))}`",
        f"- Top holding weight: `{fmt_pct(top1_weight)}`",
        f"- Top 5 holdings weight: `{fmt_pct(top5_weight)}`",
        f"- Change in holdings count versus prior parsed 13F: `{fmt_pct(holdings_count_change)}`",
        f"- Change in reported market value versus prior parsed 13F: `{fmt_pct(total_value_change)}`",
        "",
        "## Top holdings",
        build_13f_top_holdings_table(holdings, total_value_thousands, top_holdings_limit),
        "",
        "## Recent 13F history",
        build_13f_history_table(recent_filings[:recent_limit]),
        "",
        "## Interpretation",
        "- The 13F is Berkshire Hathaway's quarterly U.S. long-equity holdings snapshot, not a full picture of every asset, derivative, or foreign position.",
        f"- The latest parsed filing shows `{fmt_int(len(holdings))}` reported positions with `{fmt_pct(top5_weight)}` of value concentrated in the top five names.",
        "- This file is best used for portfolio concentration, top-position tracking, and change detection across filing dates.",
        "",
        "## Missing data or coverage notes",
        "- 13F values are reported in thousands of dollars and are point-in-time snapshots at quarter end.",
        "- Confidential treatment, omitted securities, non-13F assets, and some manager structure details are not fully captured by this parser.",
        "- This review is holdings-driven and does not yet compute adds, trims, exits, or entry dates by issuer across quarters.",
        "",
        "## Sources used",
        "- `filings/edgar/extracted/13f/holdings_manifest.json`",
        f"- `{latest_filing.get('output_path', 'N/A')}`",
        f"- `{latest_full_submission(latest_13f_record or {})}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    ticker_root = TICKERS_ROOT / args.ticker.upper()
    if not ticker_root.exists():
        raise SystemExit(f"Ticker workspace not found: {ticker_root}")

    filings_dir = ticker_root / "filings"
    edgar_dir = filings_dir / "edgar"
    manifest = load_json(edgar_dir / "normalized" / "filings_manifest.json")
    latest_by_form = load_json(edgar_dir / "normalized" / "latest_by_form.json")
    annual_history = load_json(edgar_dir / "extracted" / "companyfacts" / "annual_statement_history.json")
    quarterly_history = load_json(edgar_dir / "extracted" / "companyfacts" / "quarterly_statement_history.json")
    buffett_history = load_json(edgar_dir / "extracted" / "companyfacts" / "buffett_metric_history.json")
    latest_summary = load_json(edgar_dir / "extracted" / "companyfacts" / "latest_summary.json")
    thirteen_f_manifest = load_optional_json(edgar_dir / "extracted" / "13f" / "holdings_manifest.json")

    records = manifest.get("records", [])
    latest_10k = latest_by_form["records"].get("10-K")
    latest_10q = latest_by_form["records"].get("10-Q")
    latest_13f = latest_by_form["records"].get("13F-HR") or latest_by_form["records"].get("13F-HR/A")
    latest_8ks = get_recent_records(records, "8-K")
    latest_proxies = get_recent_records(records, "DEF 14A")

    files_updated: list[str] = []
    annual_records = annual_history.get("records", [])
    quarterly_records = quarterly_history.get("records", [])

    if latest_10k and latest_10q and latest_8ks and latest_proxies and annual_records and quarterly_records:
        latest_annual = annual_records[-1]
        prior_annual = annual_records[-2] if len(annual_records) >= 2 else None
        buffett_map = annual_metric_lookup(buffett_history)
        latest_buffett = buffett_map.get(latest_annual["period_end"], {})

        write_text(filings_dir / "latest_10k.md", build_10k_review(ticker_root, latest_10k, annual_history, buffett_history))
        write_text(filings_dir / "latest_10q.md", build_10q_review(latest_10q, latest_summary, quarterly_history))
        write_text(filings_dir / "latest_8k.md", build_8k_review(latest_8ks, args.recent_8k_limit))
        write_text(filings_dir / "proxy_def14a.md", build_proxy_review(latest_proxies, args.recent_proxy_limit))
        write_text(filings_dir / "accounting_notes.md", build_accounting_notes(latest_annual, prior_annual, latest_buffett))
        files_updated.extend(
            [
                str((filings_dir / "latest_10k.md").relative_to(REPO_ROOT)),
                str((filings_dir / "latest_10q.md").relative_to(REPO_ROOT)),
                str((filings_dir / "latest_8k.md").relative_to(REPO_ROOT)),
                str((filings_dir / "proxy_def14a.md").relative_to(REPO_ROOT)),
                str((filings_dir / "accounting_notes.md").relative_to(REPO_ROOT)),
            ]
        )

    if thirteen_f_manifest and thirteen_f_manifest.get("filings") and latest_13f:
        write_text(
            filings_dir / "latest_13f.md",
            build_13f_review(
                latest_13f_record=latest_13f,
                ticker_root=ticker_root,
                thirteen_f_manifest=thirteen_f_manifest,
                recent_limit=args.recent_13f_limit,
                top_holdings_limit=args.top_holdings_limit,
            ),
        )
        files_updated.append(str((filings_dir / "latest_13f.md").relative_to(REPO_ROOT)))

    if not files_updated:
        raise SystemExit("No supported filing review outputs could be generated from the stored manifest.")

    print(
        json.dumps(
            {
                "ticker": manifest["ticker"],
                "files_updated": files_updated,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
