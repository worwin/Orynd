#!/usr/bin/env python3
"""Extract normalized SEC EDGAR facts from stored ticker artifacts."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
TICKERS_ROOT = REPO_ROOT / "assets" / "equities" / "tickers"
ANNUAL_FORMS = {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}
QUARTERLY_FORMS = {"10-Q", "10-Q/A", "6-K"}
THIRTEEN_F_FORMS = {"13F-HR", "13F-HR/A"}


@dataclass(frozen=True)
class MetricSpec:
    key: str
    label: str
    statement: str
    taxonomy: str
    concepts: tuple[str, ...]
    preferred_units: tuple[str, ...]


METRIC_SPECS: tuple[MetricSpec, ...] = (
    MetricSpec("revenue", "Revenue", "income_statement", "us-gaap", ("RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"), ("USD",)),
    MetricSpec("gross_profit", "Gross Profit", "income_statement", "us-gaap", ("GrossProfit",), ("USD",)),
    MetricSpec("operating_income", "Operating Income", "income_statement", "us-gaap", ("OperatingIncomeLoss",), ("USD",)),
    MetricSpec("net_income", "Net Income", "income_statement", "us-gaap", ("NetIncomeLoss", "ProfitLoss"), ("USD",)),
    MetricSpec("operating_cash_flow", "Operating Cash Flow", "cash_flow_statement", "us-gaap", ("NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"), ("USD",)),
    MetricSpec("capex", "Capital Expenditures", "cash_flow_statement", "us-gaap", ("PaymentsToAcquirePropertyPlantAndEquipment", "PropertyPlantAndEquipmentAdditions", "CapitalExpendituresIncurredButNotYetPaid"), ("USD",)),
    MetricSpec("share_based_compensation", "Share-Based Compensation", "cash_flow_statement", "us-gaap", ("ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"), ("USD",)),
    MetricSpec("dividends_paid", "Dividends Paid", "cash_flow_statement", "us-gaap", ("PaymentsOfDividends", "PaymentsOfDividendsCommonStock", "DividendsCash"), ("USD",)),
    MetricSpec("buybacks", "Common Share Repurchases", "cash_flow_statement", "us-gaap", ("PaymentsForRepurchaseOfCommonStock",), ("USD",)),
    MetricSpec("cash_and_equivalents", "Cash and Equivalents", "balance_sheet", "us-gaap", ("CashAndCashEquivalentsAtCarryingValue",), ("USD",)),
    MetricSpec("current_assets", "Current Assets", "balance_sheet", "us-gaap", ("AssetsCurrent",), ("USD",)),
    MetricSpec("total_assets", "Total Assets", "balance_sheet", "us-gaap", ("Assets",), ("USD",)),
    MetricSpec("current_liabilities", "Current Liabilities", "balance_sheet", "us-gaap", ("LiabilitiesCurrent",), ("USD",)),
    MetricSpec("long_term_debt", "Long-Term Debt", "balance_sheet", "us-gaap", ("LongTermDebtNoncurrent", "LongTermDebt", "LongTermDebtAndFinanceLeaseObligations"), ("USD",)),
    MetricSpec("stockholders_equity", "Stockholders' Equity", "balance_sheet", "us-gaap", ("StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"), ("USD",)),
    MetricSpec("retained_earnings", "Retained Earnings", "balance_sheet", "us-gaap", ("RetainedEarningsAccumulatedDeficit",), ("USD",)),
    MetricSpec("shares_outstanding", "Shares Outstanding", "balance_sheet", "dei", ("EntityCommonStockSharesOutstanding", "EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding"), ("shares",)),
    MetricSpec("diluted_weighted_shares", "Diluted Weighted Average Shares", "income_statement", "us-gaap", ("WeightedAverageNumberOfDilutedSharesOutstanding",), ("shares",)),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", required=True, help="Ticker workspace to read from, e.g. AAPL")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite extracted outputs.")
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pick_companyfacts_path(raw_companyfacts_dir: Path) -> Path | None:
    paths = sorted(raw_companyfacts_dir.glob("*.json"))
    return paths[0] if paths else None


def choose_unit(units: dict[str, list[dict[str, Any]]], preferred_units: tuple[str, ...]) -> tuple[str, list[dict[str, Any]]] | tuple[None, None]:
    for unit in preferred_units:
        if unit in units:
            return unit, units[unit]
    if units:
        first_key = next(iter(units))
        return first_key, units[first_key]
    return None, None


def normalize_facts(entries: list[dict[str, Any]], forms: set[str], period_kind: str) -> list[dict[str, Any]]:
    filtered = [entry for entry in entries if entry.get("form") in forms and entry.get("val") is not None and entry.get("end")]
    if period_kind == "annual":
        filtered = [entry for entry in filtered if entry.get("fp") in ("FY", None, "") ]
    elif period_kind == "quarterly":
        filtered = [entry for entry in filtered if str(entry.get("fp", "")).startswith("Q")]
    chosen: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in filtered:
        key = (entry.get("end", ""), entry.get("fp", ""))
        existing = chosen.get(key)
        if existing is None or (entry.get("filed", "") > existing.get("filed", "")):
            chosen[key] = entry
    return sorted(chosen.values(), key=lambda item: (item.get("end", ""), item.get("filed", "")))


def extract_metric_series(companyfacts: dict[str, Any], spec: MetricSpec, forms: set[str], period_kind: str) -> dict[str, Any] | None:
    taxonomy_facts = companyfacts.get("facts", {}).get(spec.taxonomy, {})
    for concept in spec.concepts:
        concept_payload = taxonomy_facts.get(concept)
        if not concept_payload:
            continue
        unit_key, entries = choose_unit(concept_payload.get("units", {}), spec.preferred_units)
        if not entries:
            continue
        normalized = normalize_facts(entries, forms, period_kind)
        if not normalized:
            continue
        return {
            "metric_key": spec.key,
            "label": spec.label,
            "statement": spec.statement,
            "taxonomy": spec.taxonomy,
            "concept": concept,
            "unit": unit_key,
            "facts": normalized,
        }
    return None




def period_duration_days(fact: dict[str, Any]) -> int | None:
    start = fact.get("start")
    end = fact.get("end")
    if not start or not end:
        return None
    try:
        return (datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days
    except ValueError:
        return None


def fact_matches_anchor_period(fact: dict[str, Any], period_label: str) -> bool:
    duration_days = period_duration_days(fact)
    if duration_days is None:
        return False
    if period_label == "annual":
        return duration_days >= 300
    if period_label == "quarterly":
        return 60 <= duration_days <= 120
    return False


def index_series_by_end(series_list: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    metric_map: dict[str, dict[str, dict[str, Any]]] = {}
    for series in series_list:
        metric_key = series["metric_key"]
        metric_map[metric_key] = {fact["end"]: fact for fact in series["facts"]}
    return metric_map


def build_statement_history(series_list: list[dict[str, Any]], period_label: str, anchor_metric_keys: tuple[str, ...] = ("revenue", "net_income", "operating_cash_flow")) -> dict[str, Any]:
    metric_map = index_series_by_end(series_list)
    anchor_periods = sorted({fact["end"] for series in series_list if series["metric_key"] in anchor_metric_keys for fact in series["facts"] if fact_matches_anchor_period(fact, period_label)})
    period_ends = anchor_periods or sorted({fact["end"] for series in series_list for fact in series["facts"]})
    records: list[dict[str, Any]] = []
    for end in period_ends:
        record: dict[str, Any] = {
            "period_end": end,
            "period_type": period_label,
            "metrics": {},
            "sources": {},
        }
        forms_seen: list[str] = []
        filed_dates: list[str] = []
        for spec in METRIC_SPECS:
            fact = metric_map.get(spec.key, {}).get(end)
            if not fact:
                continue
            record["metrics"][spec.key] = fact.get("val")
            record["sources"][spec.key] = {
                "form": fact.get("form"),
                "filed": fact.get("filed"),
                "fy": fact.get("fy"),
                "fp": fact.get("fp"),
                "frame": fact.get("frame"),
                "accn": fact.get("accn"),
            }
            if fact.get("form"):
                forms_seen.append(fact["form"])
            if fact.get("filed"):
                filed_dates.append(fact["filed"])
        record["forms_seen"] = sorted(set(forms_seen))
        record["latest_filed"] = max(filed_dates) if filed_dates else None
        records.append(record)
    return {
        "period_type": period_label,
        "record_count": len(records),
        "records": records,
    }


def safe_div(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def pct(value: float | None) -> float | None:
    return None if value is None else round(value * 100, 4)


def build_buffett_metrics(statement_history: dict[str, Any]) -> dict[str, Any]:
    records = statement_history["records"]
    output: list[dict[str, Any]] = []
    prior_shares: float | int | None = None
    for record in records:
        metrics = record["metrics"]
        revenue = metrics.get("revenue")
        gross_profit = metrics.get("gross_profit")
        operating_income = metrics.get("operating_income")
        net_income = metrics.get("net_income")
        operating_cash_flow = metrics.get("operating_cash_flow")
        capex = metrics.get("capex")
        equity = metrics.get("stockholders_equity")
        assets = metrics.get("total_assets")
        debt = metrics.get("long_term_debt")
        current_assets = metrics.get("current_assets")
        current_liabilities = metrics.get("current_liabilities")
        shares_outstanding = metrics.get("shares_outstanding")
        sbc = metrics.get("share_based_compensation")
        free_cash_flow = None if operating_cash_flow is None or capex is None else operating_cash_flow - capex
        share_count_yoy_change_pct = None
        if prior_shares not in (None, 0) and shares_outstanding is not None:
            share_count_yoy_change_pct = pct((shares_outstanding - prior_shares) / prior_shares)
        output.append(
            {
                "period_end": record["period_end"],
                "latest_filed": record.get("latest_filed"),
                "gross_margin_pct": pct(safe_div(gross_profit, revenue)),
                "operating_margin_pct": pct(safe_div(operating_income, revenue)),
                "roe_pct": pct(safe_div(net_income, equity)),
                "roa_pct": pct(safe_div(net_income, assets)),
                "fcf_margin_pct": pct(safe_div(free_cash_flow, revenue)),
                "de_ratio": round(safe_div(debt, equity), 6) if safe_div(debt, equity) is not None else None,
                "current_ratio": round(safe_div(current_assets, current_liabilities), 6) if safe_div(current_assets, current_liabilities) is not None else None,
                "share_count_yoy_change_pct": share_count_yoy_change_pct,
                "sbc_as_pct_of_ocf": pct(safe_div(sbc, operating_cash_flow)),
                "free_cash_flow": free_cash_flow,
            }
        )
        if shares_outstanding is not None:
            prior_shares = shares_outstanding
    return {
        "period_type": statement_history["period_type"],
        "record_count": len(output),
        "records": output,
    }


def build_latest_summary(ticker: str, company_name: str, annual_metrics: dict[str, Any], quarterly_history: dict[str, Any]) -> dict[str, Any]:
    latest_annual = annual_metrics["records"][-1] if annual_metrics["records"] else None
    latest_quarter = quarterly_history["records"][-1] if quarterly_history["records"] else None
    return {
        "ticker": ticker,
        "company_name": company_name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "latest_annual_metrics": latest_annual,
        "latest_quarter_snapshot": latest_quarter,
    }


TAG_PATTERNS = {
    "nameOfIssuer": re.compile(r"<nameOfIssuer>(.*?)</nameOfIssuer>", re.I | re.S),
    "titleOfClass": re.compile(r"<titleOfClass>(.*?)</titleOfClass>", re.I | re.S),
    "cusip": re.compile(r"<cusip>(.*?)</cusip>", re.I | re.S),
    "value": re.compile(r"<value>(.*?)</value>", re.I | re.S),
    "sshPrnamt": re.compile(r"<sshPrnamt>(.*?)</sshPrnamt>", re.I | re.S),
    "sshPrnamtType": re.compile(r"<sshPrnamtType>(.*?)</sshPrnamtType>", re.I | re.S),
    "investmentDiscretion": re.compile(r"<investmentDiscretion>(.*?)</investmentDiscretion>", re.I | re.S),
    "otherManager": re.compile(r"<otherManager>(.*?)</otherManager>", re.I | re.S),
    "sole": re.compile(r"<sole>(.*?)</sole>", re.I | re.S),
    "shared": re.compile(r"<shared>(.*?)</shared>", re.I | re.S),
    "none": re.compile(r"<none>(.*?)</none>", re.I | re.S),
}


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"\s+", " ", value).strip()


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    digits = re.sub(r"[^0-9-]", "", value)
    return int(digits) if digits else None


def parse_info_table(block: str) -> dict[str, Any]:
    extracted = {key: clean_text(pattern.search(block).group(1)) if pattern.search(block) else None for key, pattern in TAG_PATTERNS.items()}
    return {
        "name_of_issuer": extracted["nameOfIssuer"],
        "title_of_class": extracted["titleOfClass"],
        "cusip": extracted["cusip"],
        "value_thousands_usd": parse_int(extracted["value"]),
        "share_amount": parse_int(extracted["sshPrnamt"]),
        "share_amount_type": extracted["sshPrnamtType"],
        "investment_discretion": extracted["investmentDiscretion"],
        "other_manager": extracted["otherManager"],
        "voting_authority_sole": parse_int(extracted["sole"]),
        "voting_authority_shared": parse_int(extracted["shared"]),
        "voting_authority_none": parse_int(extracted["none"]),
    }


def parse_13f_submission(text: str) -> list[dict[str, Any]]:
    blocks = re.findall(r"<infoTable>.*?</infoTable>", text, flags=re.I | re.S)
    return [parse_info_table(block) for block in blocks]


def extract_13f_holdings(manifest: dict[str, Any], ticker_root: Path, extracted_root: Path) -> dict[str, Any] | None:
    records = [record for record in manifest.get("records", []) if record.get("form") in THIRTEEN_F_FORMS]
    if not records:
        return None
    by_filing_dir = extracted_root / "13f" / "by_filing"
    filings_output: list[dict[str, Any]] = []
    for record in records:
        relative_txt = record.get("local_paths", {}).get("full_submission_txt")
        if not relative_txt:
            filings_output.append(
                {
                    "accession_number": record["accession_number"],
                    "filing_date": record["filing_date"],
                    "status": "missing_full_submission_txt",
                }
            )
            continue
        txt_path = ticker_root / Path(relative_txt)
        if not txt_path.exists():
            filings_output.append(
                {
                    "accession_number": record["accession_number"],
                    "filing_date": record["filing_date"],
                    "status": "file_not_found",
                    "path": str(txt_path.relative_to(REPO_ROOT)),
                }
            )
            continue
        holdings = parse_13f_submission(txt_path.read_text(encoding="utf-8", errors="ignore"))
        payload = {
            "ticker": manifest["ticker"],
            "accession_number": record["accession_number"],
            "filing_date": record["filing_date"],
            "form": record["form"],
            "source_full_submission_txt": relative_txt,
            "holdings_count": len(holdings),
            "holdings": holdings,
        }
        out_name = f"{record['filing_date']}__{record['accession_number'].replace('-', '')}.json"
        write_json(by_filing_dir / out_name, payload)
        filings_output.append(
            {
                "accession_number": record["accession_number"],
                "filing_date": record["filing_date"],
                "form": record["form"],
                "holdings_count": len(holdings),
                "output_path": str((by_filing_dir / out_name).relative_to(ticker_root)),
                "status": "parsed",
            }
        )
    manifest_payload = {
        "ticker": manifest["ticker"],
        "company_name": manifest["company_name"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "filing_count": len(filings_output),
        "filings": filings_output,
    }
    write_json(extracted_root / "13f" / "holdings_manifest.json", manifest_payload)
    return manifest_payload


def build_summary_markdown(ticker_root: Path, extraction_result: dict[str, Any]) -> str:
    annual = extraction_result.get("annual_statement_history", {})
    quarterly = extraction_result.get("quarterly_statement_history", {})
    thirteen_f = extraction_result.get("thirteen_f_manifest")
    extracted_dir = ticker_root / "filings" / "edgar" / "extracted"
    lines = [
        "# EDGAR Extraction Summary",
        "",
        f"- Generated at (UTC): `{extraction_result['generated_at_utc']}`",
        f"- Ticker: `{extraction_result['ticker']}`",
        f"- Company: `{extraction_result['company_name']}`",
        f"- Annual periods extracted: `{annual.get('record_count', 0)}`",
        f"- Quarterly periods extracted: `{quarterly.get('record_count', 0)}`",
        f"- 13F filings parsed: `{thirteen_f.get('filing_count', 0) if thirteen_f else 0}`",
        "",
        "## Stored outputs",
        f"- `{(extracted_dir / 'companyfacts' / 'annual_statement_history.json').relative_to(ticker_root)}`",
        f"- `{(extracted_dir / 'companyfacts' / 'quarterly_statement_history.json').relative_to(ticker_root)}`",
        f"- `{(extracted_dir / 'companyfacts' / 'buffett_metric_history.json').relative_to(ticker_root)}`",
        f"- `{(extracted_dir / 'companyfacts' / 'latest_summary.json').relative_to(ticker_root)}`",
    ]
    if thirteen_f:
        lines.extend(
            [
                f"- `{(extracted_dir / '13f' / 'holdings_manifest.json').relative_to(ticker_root)}`",
                f"- `{(extracted_dir / '13f' / 'by_filing').relative_to(ticker_root)}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Manual review locations",
            "- Raw submissions: `filings/edgar/raw/submissions/`",
            "- Raw companyfacts: `filings/edgar/raw/companyfacts/`",
            "- Filing folders: `filings/edgar/archive/`",
            "- Extracted outputs: `filings/edgar/extracted/`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    ticker_root = TICKERS_ROOT / args.ticker.upper()
    if not ticker_root.exists():
        raise SystemExit(f"Ticker workspace not found: {ticker_root}")

    edgar_root = ticker_root / "filings" / "edgar"
    manifest_path = edgar_root / "normalized" / "filings_manifest.json"
    companyfacts_path = pick_companyfacts_path(edgar_root / "raw" / "companyfacts")
    if not manifest_path.exists():
        raise SystemExit(f"Missing filings manifest: {manifest_path}")
    if companyfacts_path is None:
        raise SystemExit(f"Missing companyfacts JSON under {edgar_root / 'raw' / 'companyfacts'}")

    manifest = load_json(manifest_path)
    companyfacts = load_json(companyfacts_path)
    extracted_root = edgar_root / "extracted"
    companyfacts_root = extracted_root / "companyfacts"

    annual_series = [series for spec in METRIC_SPECS if (series := extract_metric_series(companyfacts, spec, ANNUAL_FORMS, "annual"))]
    quarterly_series = [series for spec in METRIC_SPECS if (series := extract_metric_series(companyfacts, spec, QUARTERLY_FORMS, "quarterly"))]

    annual_history = build_statement_history(annual_series, "annual")
    quarterly_history = build_statement_history(quarterly_series, "quarterly")
    buffett_metrics = build_buffett_metrics(annual_history)
    latest_summary = build_latest_summary(manifest["ticker"], manifest["company_name"], buffett_metrics, quarterly_history)

    write_json(companyfacts_root / "annual_statement_history.json", annual_history)
    write_json(companyfacts_root / "quarterly_statement_history.json", quarterly_history)
    write_json(companyfacts_root / "annual_metric_series.json", {"series": annual_series})
    write_json(companyfacts_root / "quarterly_metric_series.json", {"series": quarterly_series})
    write_json(companyfacts_root / "buffett_metric_history.json", buffett_metrics)
    write_json(companyfacts_root / "latest_summary.json", latest_summary)

    thirteen_f_manifest = extract_13f_holdings(manifest, ticker_root, extracted_root)

    extraction_result = {
        "ticker": manifest["ticker"],
        "company_name": manifest["company_name"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "annual_statement_history": {"record_count": annual_history["record_count"]},
        "quarterly_statement_history": {"record_count": quarterly_history["record_count"]},
        "thirteen_f_manifest": {"filing_count": thirteen_f_manifest["filing_count"]} if thirteen_f_manifest else None,
        "source_paths": {
            "manifest": str(manifest_path.relative_to(ticker_root)),
            "companyfacts": str(companyfacts_path.relative_to(ticker_root)),
        },
    }
    write_json(extracted_root / "extraction_manifest.json", extraction_result)
    write_text(extracted_root / "extraction_summary.md", build_summary_markdown(ticker_root, extraction_result))

    print(
        json.dumps(
            {
                "ticker": manifest["ticker"],
                "annual_periods": annual_history["record_count"],
                "quarterly_periods": quarterly_history["record_count"],
                "thirteen_f_filings": thirteen_f_manifest["filing_count"] if thirteen_f_manifest else 0,
                "extracted_root": str(extracted_root.relative_to(REPO_ROOT)),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
