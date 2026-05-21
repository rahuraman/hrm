"""Report analytics: onboarding outcomes and loss calculations."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from hrm.data_layer import ResourceRecord

HOURS_PER_DAY = 8
ONBOARDED_STATUS = "Closed"


class Outcome(Enum):
    ONBOARDED = "Onboarded"
    AT_RISK = "At risk"
    LOSS = "Loss"


@dataclass(frozen=True)
class RowMetrics:
    record: ResourceRecord
    outcome: Outcome
    days_until_deadline: int
    days_overdue: int
    daily_burn: Decimal
    loss_amount: Decimal


@dataclass(frozen=True)
class ReportSummary:
    as_of: date
    total_rows: int
    status_counts: dict[str, int]
    at_risk_count: int
    in_loss_count: int
    onboarded_count: int
    total_loss: Decimal
    rows: list[RowMetrics]


def _row_metrics(record: ResourceRecord, as_of: date) -> RowMetrics:
    daily_burn = Decimal(HOURS_PER_DAY) * record.hourly_rate

    if record.negotiation_status == ONBOARDED_STATUS:
        return RowMetrics(
            record=record,
            outcome=Outcome.ONBOARDED,
            days_until_deadline=0,
            days_overdue=0,
            daily_burn=daily_burn,
            loss_amount=Decimal("0"),
        )

    if as_of <= record.expected_closing_date:
        days_until = (record.expected_closing_date - as_of).days
        return RowMetrics(
            record=record,
            outcome=Outcome.AT_RISK,
            days_until_deadline=days_until,
            days_overdue=0,
            daily_burn=daily_burn,
            loss_amount=Decimal("0"),
        )

    days_overdue = (as_of - record.expected_closing_date).days
    loss_amount = Decimal(days_overdue) * daily_burn
    return RowMetrics(
        record=record,
        outcome=Outcome.LOSS,
        days_until_deadline=0,
        days_overdue=days_overdue,
        daily_burn=daily_burn,
        loss_amount=loss_amount,
    )


def _sort_key(row: RowMetrics) -> tuple:
    outcome_order = {
        Outcome.LOSS: 0,
        Outcome.AT_RISK: 1,
        Outcome.ONBOARDED: 2,
    }
    return (outcome_order[row.outcome], -row.loss_amount, row.record.registration)


def compute_report(
    records: list[ResourceRecord],
    as_of: date | None = None,
) -> ReportSummary:
    """Compute report metrics for all resources as of the given date."""
    report_date = as_of or date.today()
    rows = [_row_metrics(record, report_date) for record in records]
    rows.sort(key=_sort_key)

    status_counts = dict(Counter(r.record.negotiation_status for r in rows))
    at_risk_count = sum(1 for r in rows if r.outcome == Outcome.AT_RISK)
    in_loss_count = sum(1 for r in rows if r.outcome == Outcome.LOSS)
    onboarded_count = sum(1 for r in rows if r.outcome == Outcome.ONBOARDED)
    total_loss = sum((r.loss_amount for r in rows), Decimal("0"))

    return ReportSummary(
        as_of=report_date,
        total_rows=len(rows),
        status_counts=status_counts,
        at_risk_count=at_risk_count,
        in_loss_count=in_loss_count,
        onboarded_count=onboarded_count,
        total_loss=total_loss,
        rows=rows,
    )
