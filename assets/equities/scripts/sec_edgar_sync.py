#!/usr/bin/env python3
"""Sync SEC EDGAR filings into a ticker workspace.

This script is designed for the file-first Orynd repo layout:
- raw SEC payloads are stored under the ticker workspace
- normalized manifests are generated for downstream analysis
- markdown index files are refreshed so agents can use repo files as memory
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib import error, parse, request


REPO_ROOT = Path(__file__).resolve().parents[3]
TICKERS_ROOT = REPO_ROOT / "assets" / "equities" / "tickers"

SEC_BASE = "https://www.sec.gov"
DATA_SEC_BASE = "https://data.sec.gov"
TICKER_MAP_URL = f"{SEC_BASE}/files/company_tickers.json"
REQUEST_INTERVAL_SECONDS = 0.25


@dataclass(frozen=True)
class FilingRecord:
    accession_number: str
    filing_date: str
    report_date: str
    acceptance_datetime: str
    act: str
    form: str
    file_number: str
    film_number: str
    items: str
    size: int | None
    is_xbrl: int | None
    is_inline_xbrl: int | None
    primary_document: str
    primary_doc_description: str


class EdgarClient:
    def __init__(self, user_agent: str, request_interval_seconds: float) -> None:
        self.user_agent = user_agent
        self.request_interval_seconds = request_interval_seconds
        self._last_request_at = 0.0

    def _throttle(self) -> None:
        if self._last_request_at == 0.0:
            return
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.request_interval_seconds:
            time.sleep(self.request_interval_seconds - elapsed)

    def fetch_bytes(self, url: str) -> bytes:
        self._throttle()
        netloc = parse.urlparse(url).netloc
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "identity",
            "Host": netloc,
        }
        email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+", self.user_agent, re.I)
        if email_match:
            headers["From"] = email_match.group(0)
        req = request.Request(url, headers=headers)
        try:
            with request.urlopen(req, timeout=60) as response:
                payload = response.read()
        except error.HTTPError as exc:
            raise RuntimeError(f"SEC request failed for {url}: HTTP {exc.code}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"SEC request failed for {url}: {exc.reason}") from exc
        self._last_request_at = time.monotonic()
        return payload

    def fetch_json(self, url: str) -> dict:
        return json.loads(self.fetch_bytes(url).decode("utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    parser.add_argument("--cik", help="Optional CIK override, with or without leading zeros.")
    parser.add_argument("--company-name", help="Optional company name override for manual CIK runs.")
    parser.add_argument(
        "--forms",
        default="10-K",
        help="Comma-separated form list, e.g. 10-K,10-Q,8-K,DEF 14A",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum filings per requested form to store after filtering",
    )
    parser.add_argument(
        "--since",
        help="Optional lower bound on filing date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--user-agent",
        default=os.environ.get("SEC_USER_AGENT", ""),
        help=(
            "Declared SEC user agent, e.g. "
            "'Orynd Research ops@example.com'. Can also be set via SEC_USER_AGENT."
        ),
    )
    parser.add_argument(
        "--request-interval-seconds",
        type=float,
        default=REQUEST_INTERVAL_SECONDS,
        help="Delay between SEC requests. Default keeps usage well below 10 req/sec.",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Fetch manifests and metadata without downloading filing documents.",
    )
    parser.add_argument(
        "--skip-companyfacts",
        action="store_true",
        help="Skip the XBRL companyfacts pull.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-download files even when they already exist.",
    )
    return parser.parse_args()


def ensure_user_agent(user_agent: str) -> str:
    clean = user_agent.strip()
    if clean:
        return clean
    raise SystemExit(
        "Missing SEC user agent. Pass --user-agent \"Company Name email@example.com\" "
        "or set SEC_USER_AGENT."
    )


def normalize_forms(forms_arg: str) -> list[str]:
    forms = [part.strip().upper() for part in forms_arg.split(",") if part.strip()]
    if not forms:
        raise SystemExit("No forms supplied.")
    return forms


def sanitize_form(form: str) -> str:
    return form.replace("/", "_").replace(" ", "_")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def should_write(path: Path, overwrite: bool) -> bool:
    return overwrite or not path.exists()


def load_ticker_map(client: EdgarClient) -> list[dict]:
    payload = client.fetch_json(TICKER_MAP_URL)
    if isinstance(payload, dict):
        return list(payload.values())
    raise RuntimeError("Unexpected SEC ticker map payload.")


def resolve_ticker(client: EdgarClient, ticker: str) -> dict:
    ticker_upper = ticker.upper()
    for entry in load_ticker_map(client):
        if entry.get("ticker", "").upper() == ticker_upper:
            cik_int = int(entry["cik_str"])
            return {
                "ticker": ticker_upper,
                "company_name": entry["title"],
                "cik_int": cik_int,
                "cik_padded": f"{cik_int:010d}",
            }
    raise SystemExit(f"Ticker {ticker_upper} was not found in the SEC ticker map.")


def resolve_manual_meta(ticker: str, cik: str, company_name: str | None) -> dict:
    cik_digits = ''.join(ch for ch in cik if ch.isdigit())
    if not cik_digits:
        raise SystemExit('--cik must contain digits.')
    cik_int = int(cik_digits)
    return {
        "ticker": ticker.upper(),
        "company_name": company_name or ticker.upper(),
        "cik_int": cik_int,
        "cik_padded": f"{cik_int:010d}",
    }


def to_records(columnar: dict) -> list[FilingRecord]:
    accessions = columnar.get("accessionNumber", [])
    records: list[FilingRecord] = []
    for idx, accession in enumerate(accessions):
        records.append(
            FilingRecord(
                accession_number=accession,
                filing_date=(columnar.get("filingDate") or [""])[idx],
                report_date=(columnar.get("reportDate") or [""])[idx],
                acceptance_datetime=(columnar.get("acceptanceDateTime") or [""])[idx],
                act=(columnar.get("act") or [""])[idx],
                form=(columnar.get("form") or [""])[idx],
                file_number=(columnar.get("fileNumber") or [""])[idx],
                film_number=(columnar.get("filmNumber") or [""])[idx],
                items=(columnar.get("items") or [""])[idx],
                size=(columnar.get("size") or [None])[idx],
                is_xbrl=(columnar.get("isXBRL") or [None])[idx],
                is_inline_xbrl=(columnar.get("isInlineXBRL") or [None])[idx],
                primary_document=(columnar.get("primaryDocument") or [""])[idx],
                primary_doc_description=(columnar.get("primaryDocDescription") or [""])[idx],
            )
        )
    return records


def load_submissions(client: EdgarClient, cik_padded: str, raw_submissions_dir: Path, overwrite: bool) -> tuple[dict, list[dict]]:
    main_url = f"{DATA_SEC_BASE}/submissions/CIK{cik_padded}.json"
    main_payload = client.fetch_json(main_url)
    if should_write(raw_submissions_dir / f"CIK{cik_padded}.json", overwrite):
        write_json(raw_submissions_dir / f"CIK{cik_padded}.json", main_payload)

    extras: list[dict] = []
    for file_entry in main_payload.get("filings", {}).get("files", []):
        name = file_entry.get("name")
        if not name:
            continue
        extra_url = f"{DATA_SEC_BASE}/submissions/{name}"
        extra_payload = client.fetch_json(extra_url)
        extras.append({"name": name, "payload": extra_payload})
        if should_write(raw_submissions_dir / name, overwrite):
            write_json(raw_submissions_dir / name, extra_payload)

    return main_payload, extras


def collect_records(main_payload: dict, extras: list[dict]) -> list[FilingRecord]:
    records = to_records(main_payload.get("filings", {}).get("recent", {}))
    for extra in extras:
        records.extend(to_records(extra["payload"]))

    deduped: dict[str, FilingRecord] = {}
    for record in records:
        deduped[record.accession_number] = record
    return sorted(deduped.values(), key=lambda item: (item.filing_date, item.accession_number), reverse=True)


def filter_records(records: Iterable[FilingRecord], forms: set[str], since: str | None, limit: int) -> list[FilingRecord]:
    counts: dict[str, int] = {form: 0 for form in forms}
    selected: list[FilingRecord] = []
    for record in records:
        form_upper = record.form.upper()
        if form_upper not in forms:
            continue
        if since and record.filing_date and record.filing_date < since:
            continue
        if counts[form_upper] >= limit:
            continue
        selected.append(record)
        counts[form_upper] += 1
        if all(count >= limit for count in counts.values()):
            break
    return selected


def build_archive_urls(cik_int: int, record: FilingRecord) -> dict[str, str]:
    accession_compact = record.accession_number.replace("-", "")
    base = f"{SEC_BASE}/Archives/edgar/data/{cik_int}/{accession_compact}"
    urls = {
        "directory_index_json": f"{base}/index.json",
        "full_submission_txt": f"{base}/{record.accession_number}.txt",
    }
    if record.primary_document:
        quoted_doc = parse.quote(record.primary_document)
        urls["primary_document"] = f"{base}/{quoted_doc}"
    return urls


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def save_companyfacts(
    client: EdgarClient,
    cik_padded: str,
    raw_companyfacts_dir: Path,
    overwrite: bool,
) -> dict:
    url = f"{DATA_SEC_BASE}/api/xbrl/companyfacts/CIK{cik_padded}.json"
    payload = client.fetch_json(url)
    target = raw_companyfacts_dir / f"CIK{cik_padded}_companyfacts.json"
    if should_write(target, overwrite):
        write_json(target, payload)
    return payload


def build_filing_index_markdown(manifest: dict) -> str:
    lines = [
        "# Filing Index",
        "",
        "## SEC EDGAR Sync",
        f"- Ticker: `{manifest['ticker']}`",
        f"- Company: `{manifest['company_name']}`",
        f"- CIK: `{manifest['cik']}`",
        f"- Synced at (UTC): `{manifest['synced_at_utc']}`",
        f"- Forms requested: `{', '.join(manifest['forms_requested'])}`",
        f"- Filings stored: `{manifest['record_count']}`",
        "",
        "## Review status",
        f"- Download status: `{manifest['download_status']}`",
        "- Normalized manifests have been updated under `filings/edgar/normalized/`.",
    ]

    if manifest["download_status"] == "complete":
        lines.append("- Raw SEC filing artifacts are present under `filings/edgar/archive/`.")
    elif manifest["download_status"] == "metadata_only":
        lines.append("- This run only pulled metadata. Filing documents were not requested.")
    else:
        lines.append("- Some required filing artifacts are missing. Check `download_errors` in the manifest.")

    if manifest.get("enrichment_warning_count", 0):
        lines.append("- Optional SEC archive enrichments were not all available; full submission text remains the canonical raw artifact.")

    lines.extend(
        [
            "- Analytical review files such as `latest_10k.md` still need a human or agent review pass.",
            "",
            "## Stored filings",
        ]
    )

    if not manifest["records"]:
        lines.append("- No filings matched the requested filters.")
        return "\n".join(lines) + "\n"

    for record in manifest["records"]:
        lines.extend(
            [
                f"### {record['form']} filed {record['filing_date']}",
                f"- Accession: `{record['accession_number']}`",
                f"- Primary document: `{record['primary_document'] or 'N/A'}`",
                f"- Filing directory: `{record['local_paths']['filing_dir']}`",
                f"- SEC filing folder: `{record['urls']['directory_index_json']}`",
            ]
        )
        if record["download_errors"]:
            lines.append(f"- Required download issues: `{' ; '.join(record['download_errors'])}`")
        if record["enrichment_warnings"]:
            lines.append(f"- Optional archive warnings: `{' ; '.join(record['enrichment_warnings'])}`")
    return "\n".join(lines) + "\n"


def sync_filings(
    client: EdgarClient,
    ticker_root: Path,
    ticker_meta: dict,
    forms: list[str],
    since: str | None,
    limit: int,
    metadata_only: bool,
    skip_companyfacts: bool,
    overwrite: bool,
) -> dict:
    filings_root = ticker_root / "filings"
    edgar_root = filings_root / "edgar"
    raw_root = edgar_root / "raw"
    raw_submissions_dir = raw_root / "submissions"
    raw_companyfacts_dir = raw_root / "companyfacts"
    archive_root = edgar_root / "archive"
    normalized_root = edgar_root / "normalized"

    main_payload, extras = load_submissions(
        client=client,
        cik_padded=ticker_meta["cik_padded"],
        raw_submissions_dir=raw_submissions_dir,
        overwrite=overwrite,
    )
    records = collect_records(main_payload, extras)
    selected = filter_records(records, set(forms), since, limit)

    companyfacts_payload = None
    if not skip_companyfacts:
        companyfacts_payload = save_companyfacts(
            client=client,
            cik_padded=ticker_meta["cik_padded"],
            raw_companyfacts_dir=raw_companyfacts_dir,
            overwrite=overwrite,
        )

    manifest_records: list[dict] = []
    for record in selected:
        accession_compact = record.accession_number.replace("-", "")
        form_dir = archive_root / sanitize_form(record.form) / f"{record.filing_date}__{accession_compact}"
        urls = build_archive_urls(ticker_meta["cik_int"], record)
        local_paths: dict[str, str | None] = {
            "filing_dir": str(form_dir.relative_to(ticker_root)),
            "metadata_json": str((form_dir / "filing_metadata.json").relative_to(ticker_root)),
            "directory_index_json": None,
            "full_submission_txt": None,
            "primary_document": None,
        }

        metadata = {
            "ticker": ticker_meta["ticker"],
            "company_name": ticker_meta["company_name"],
            "cik": ticker_meta["cik_padded"],
            "record": asdict(record),
            "urls": urls,
            "synced_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        if should_write(form_dir / "filing_metadata.json", overwrite):
            write_json(form_dir / "filing_metadata.json", metadata)

        if not metadata_only:
            if should_write(form_dir / "index.json", overwrite):
                try:
                    write_bytes(form_dir / "index.json", client.fetch_bytes(urls["directory_index_json"]))
                except RuntimeError:
                    pass
            if (form_dir / "index.json").exists():
                local_paths["directory_index_json"] = str((form_dir / "index.json").relative_to(ticker_root))

            if should_write(form_dir / "full_submission.txt", overwrite):
                try:
                    write_bytes(form_dir / "full_submission.txt", client.fetch_bytes(urls["full_submission_txt"]))
                except RuntimeError:
                    pass
            if (form_dir / "full_submission.txt").exists():
                local_paths["full_submission_txt"] = str((form_dir / "full_submission.txt").relative_to(ticker_root))

            primary_document_url = urls.get("primary_document")
            if primary_document_url:
                suffix = Path(parse.urlparse(primary_document_url).path).suffix or ".html"
                primary_target = form_dir / f"primary_document{suffix}"
                if should_write(primary_target, overwrite):
                    try:
                        write_bytes(primary_target, client.fetch_bytes(primary_document_url))
                    except RuntimeError:
                        pass
                if primary_target.exists():
                    local_paths["primary_document"] = str(primary_target.relative_to(ticker_root))

        download_errors: list[str] = []
        enrichment_warnings: list[str] = []
        if not metadata_only:
            if local_paths["full_submission_txt"] is None:
                download_errors.append("full_submission_txt download failed")
            if local_paths["directory_index_json"] is None:
                enrichment_warnings.append("directory_index_json download failed")
            if urls.get("primary_document") and local_paths["primary_document"] is None:
                enrichment_warnings.append("primary_document download failed")

        manifest_records.append(
            {
                "ticker": ticker_meta["ticker"],
                "company_name": ticker_meta["company_name"],
                "cik": ticker_meta["cik_padded"],
                "accession_number": record.accession_number,
                "accession_number_compact": accession_compact,
                "form": record.form,
                "filing_date": record.filing_date,
                "report_date": record.report_date,
                "acceptance_datetime": record.acceptance_datetime,
                "primary_document": record.primary_document,
                "primary_doc_description": record.primary_doc_description,
                "items": record.items,
                "is_xbrl": record.is_xbrl,
                "is_inline_xbrl": record.is_inline_xbrl,
                "urls": urls,
                "local_paths": local_paths,
                "download_errors": download_errors,
                "enrichment_warnings": enrichment_warnings,
            }
        )

    total_download_errors = sum(len(record["download_errors"]) for record in manifest_records)
    total_enrichment_warnings = sum(len(record["enrichment_warnings"]) for record in manifest_records)
    download_status = "metadata_only" if metadata_only else ("complete" if total_download_errors == 0 else "partial")

    manifest = {
        "ticker": ticker_meta["ticker"],
        "company_name": ticker_meta["company_name"],
        "cik": ticker_meta["cik_padded"],
        "forms_requested": forms,
        "limit_per_form": limit,
        "since": since,
        "synced_at_utc": datetime.now(timezone.utc).isoformat(),
        "metadata_only": metadata_only,
        "download_status": download_status,
        "download_error_count": total_download_errors,
        "enrichment_warning_count": total_enrichment_warnings,
        "companyfacts_downloaded": not skip_companyfacts and companyfacts_payload is not None,
        "record_count": len(manifest_records),
        "records": manifest_records,
    }
    write_json(normalized_root / "filings_manifest.json", manifest)

    latest_by_form: dict[str, dict] = {}
    for record in manifest_records:
        latest_by_form.setdefault(record["form"], record)
    write_json(
        normalized_root / "latest_by_form.json",
        {
            "ticker": ticker_meta["ticker"],
            "company_name": ticker_meta["company_name"],
            "cik": ticker_meta["cik_padded"],
            "synced_at_utc": manifest["synced_at_utc"],
            "records": latest_by_form,
        },
    )

    write_text(filings_root / "filing_index.md", build_filing_index_markdown(manifest))
    return manifest


def validate_since(since: str | None) -> str | None:
    if since is None:
        return None
    try:
        datetime.strptime(since, "%Y-%m-%d")
    except ValueError as exc:
        raise SystemExit("--since must be YYYY-MM-DD") from exc
    return since


def main() -> int:
    args = parse_args()
    user_agent = ensure_user_agent(args.user_agent)
    forms = normalize_forms(args.forms)
    since = validate_since(args.since)

    ticker_root = TICKERS_ROOT / args.ticker.upper()
    if not ticker_root.exists():
        raise SystemExit(
            f"Ticker workspace {ticker_root} does not exist. "
            "Create it first with assets/equities/tasks/02_create_company_workspace.md."
        )

    client = EdgarClient(user_agent=user_agent, request_interval_seconds=args.request_interval_seconds)
    ticker_meta = resolve_manual_meta(args.ticker, args.cik, args.company_name) if args.cik else resolve_ticker(client, args.ticker)
    manifest = sync_filings(
        client=client,
        ticker_root=ticker_root,
        ticker_meta=ticker_meta,
        forms=forms,
        since=since,
        limit=args.limit,
        metadata_only=args.metadata_only,
        skip_companyfacts=args.skip_companyfacts,
        overwrite=args.overwrite,
    )

    print(
        json.dumps(
            {
                "ticker": manifest["ticker"],
                "company_name": manifest["company_name"],
                "record_count": manifest["record_count"],
                "forms_requested": manifest["forms_requested"],
                "manifest_path": str(
                    (ticker_root / "filings" / "edgar" / "normalized" / "filings_manifest.json").relative_to(REPO_ROOT)
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
