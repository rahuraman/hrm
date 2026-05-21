"""Data layer: load and parse HRM resource records from CSV."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATE_FORMAT = "%Y-%m-%d"

REQUIRED_COLUMNS = {
    "registration number",
    "grade",
    "open date",
    "key skill",
    "expected closing date",
    "negotiation status",
    "hourly rate",
}


@dataclass(frozen=True)
class ResourceRecord:
    registration: str
    grade: str
    open_date: date
    key_skill: str
    expected_closing_date: date
    negotiation_status: str
    hourly_rate: Decimal


def _normalize_header(name: str) -> str:
    return name.strip().lower()


def _parse_date(value: str, field: str, row_num: int) -> date:
    text = value.strip()
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(
            f"Row {row_num}: invalid date '{text}' for {field} (expected YYYY-MM-DD)"
        ) from exc


def _parse_rate(value: str, row_num: int) -> Decimal:
    text = value.strip()
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"Row {row_num}: invalid hourly rate '{text}'") from exc


def load_resources(path: Path) -> list[ResourceRecord]:
    """Load resource records from a CSV file."""
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    records: list[ResourceRecord] = []

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: file is empty or has no header row")

        header_map = {_normalize_header(h): h for h in reader.fieldnames}
        missing = REQUIRED_COLUMNS - set(header_map)
        if missing:
            raise ValueError(f"{path}: missing columns: {', '.join(sorted(missing))}")

        for row_num, row in enumerate(reader, start=2):
            if not any(v and str(v).strip() for v in row.values()):
                continue

            try:
                records.append(
                    ResourceRecord(
                        registration=row[header_map["registration number"]].strip(),
                        grade=row[header_map["grade"]].strip(),
                        open_date=_parse_date(
                            row[header_map["open date"]], "open date", row_num
                        ),
                        key_skill=row[header_map["key skill"]].strip(),
                        expected_closing_date=_parse_date(
                            row[header_map["expected closing date"]],
                            "expected closing date",
                            row_num,
                        ),
                        negotiation_status=row[
                            header_map["negotiation status"]
                        ].strip(),
                        hourly_rate=_parse_rate(
                            row[header_map["hourly rate"]], row_num
                        ),
                    )
                )
            except (KeyError, AttributeError) as exc:
                raise ValueError(f"Row {row_num}: malformed row") from exc

    if not records:
        raise ValueError(f"{path}: no data rows found")

    return records
