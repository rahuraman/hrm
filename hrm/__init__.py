"""HRM onboarding and loss reporting package."""

from hrm.data_layer import ResourceRecord, load_resources
from hrm.report import (
    HOURS_PER_DAY,
    ONBOARDED_STATUS,
    Outcome,
    ReportSummary,
    RowMetrics,
    compute_report,
)
from hrm.report_html import render_html, write_report

__all__ = [
    "HOURS_PER_DAY",
    "ONBOARDED_STATUS",
    "Outcome",
    "ReportSummary",
    "ResourceRecord",
    "RowMetrics",
    "compute_report",
    "load_resources",
    "render_html",
    "write_report",
]
