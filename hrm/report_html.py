"""HTML presentation layer for HRM reports."""

from __future__ import annotations

import html
from datetime import date
from decimal import Decimal
from pathlib import Path

from hrm.report import Outcome, ReportSummary, RowMetrics

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HRM Resource Onboarding &amp; Loss Report</title>
  <style>
    :root {{
      --bg: #f4f6f9;
      --card: #ffffff;
      --text: #1a2332;
      --muted: #5c6b7a;
      --border: #dde3ea;
      --green: #0d7a4a;
      --green-bg: #e6f4ed;
      --amber: #9a6700;
      --amber-bg: #fff8e6;
      --red: #b42318;
      --red-bg: #fdecea;
      --blue: #175cd3;
      --blue-bg: #eff4ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: "Segoe UI", system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 1.5rem;
      line-height: 1.5;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 2px solid var(--border);
    }}
    h1 {{ margin: 0 0 0.25rem; font-size: 1.75rem; }}
    .meta {{ color: var(--muted); font-size: 0.95rem; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem;
    }}
    .card-label {{ font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }}
    .card-value {{ font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem; }}
    .card-value.loss {{ color: var(--red); }}
    .status-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
    }}
    .status-chip {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.35rem 0.75rem;
      font-size: 0.85rem;
    }}
    .table-wrap {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow-x: auto;
    }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th, td {{ padding: 0.65rem 0.85rem; text-align: left; border-bottom: 1px solid var(--border); }}
    th {{ background: #eef1f5; font-weight: 600; white-space: nowrap; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f8fafc; }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .badge {{
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.8rem;
      font-weight: 600;
    }}
    .badge-closed {{ background: var(--green-bg); color: var(--green); }}
    .badge-progress {{ background: var(--blue-bg); color: var(--blue); }}
    .badge-open {{ background: var(--amber-bg); color: var(--amber); }}
    .badge-hold {{ background: #f0f0f0; color: #444; }}
    .badge-default {{ background: #eee; color: #333; }}
    .outcome-onboarded {{ background: var(--green-bg); color: var(--green); }}
    .outcome-risk {{ background: var(--amber-bg); color: var(--amber); }}
    .outcome-loss {{ background: var(--red-bg); color: var(--red); }}
    footer {{
      margin-top: 1.5rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border);
      font-size: 0.85rem;
      color: var(--muted);
    }}
    @media print {{
      body {{ background: white; padding: 0; }}
      .card, .table-wrap {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>HRM Resource Onboarding &amp; Loss Report</h1>
      <p class="meta">As of <strong>{as_of}</strong> &middot; Source: <strong>{source_name}</strong></p>
    </header>

    <section class="cards">
      <div class="card">
        <div class="card-label">Total resources</div>
        <div class="card-value">{total_rows}</div>
      </div>
      <div class="card">
        <div class="card-label">Onboarded</div>
        <div class="card-value">{onboarded_count}</div>
      </div>
      <div class="card">
        <div class="card-label">At risk</div>
        <div class="card-value">{at_risk_count}</div>
      </div>
      <div class="card">
        <div class="card-label">In loss</div>
        <div class="card-value">{in_loss_count}</div>
      </div>
      <div class="card">
        <div class="card-label">Total loss</div>
        <div class="card-value loss">{total_loss}</div>
      </div>
    </section>

    <section class="status-grid">
      {status_chips}
    </section>

    <section class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Registration</th>
            <th>Grade</th>
            <th>Key skill</th>
            <th>Open date</th>
            <th>Closing date</th>
            <th>Status</th>
            <th>Outcome</th>
            <th class="num">Days</th>
            <th class="num">Daily burn</th>
            <th class="num">Loss</th>
          </tr>
        </thead>
        <tbody>
          {table_rows}
        </tbody>
      </table>
    </section>

    <footer>
      <p><strong>How loss is calculated:</strong> A resource is onboarded only when negotiation status is
      <em>Closed</em>. If status is not Closed after the expected closing date, loss accrues at
      <strong>8 billable hours per day</strong> &times; hourly rate for each overdue day.</p>
      <p>Loss figures represent unbilled capacity (opportunity cost), not payroll or other costs.
      Rows marked Closed are assumed fully onboarded with zero loss.</p>
    </footer>
  </div>
</body>
</html>
"""


def _fmt_date(value: date) -> str:
    return value.strftime("%Y-%m-%d")


def _fmt_money(value: Decimal) -> str:
    return f"${value:,.2f}"


def _status_badge_class(status: str) -> str:
    mapping = {
        "Closed": "badge-closed",
        "In Progress": "badge-progress",
        "Open": "badge-open",
        "On Hold": "badge-hold",
    }
    return mapping.get(status, "badge-default")


def _outcome_badge_class(outcome: Outcome) -> str:
    mapping = {
        Outcome.ONBOARDED: "outcome-onboarded",
        Outcome.AT_RISK: "outcome-risk",
        Outcome.LOSS: "outcome-loss",
    }
    return mapping[outcome]


def _days_label(row: RowMetrics) -> str:
    if row.outcome == Outcome.AT_RISK:
        return f"{row.days_until_deadline} until deadline"
    if row.outcome == Outcome.LOSS:
        return f"{row.days_overdue} overdue"
    return "—"


def _render_status_chips(status_counts: dict[str, int]) -> str:
    chips = []
    for status, count in sorted(status_counts.items()):
        chips.append(
            f'<span class="status-chip">'
            f"{html.escape(status)}: <strong>{count}</strong></span>"
        )
    return "\n      ".join(chips)


def _render_table_row(row: RowMetrics) -> str:
    rec = row.record
    status_cls = _status_badge_class(rec.negotiation_status)
    outcome_cls = _outcome_badge_class(row.outcome)
    return f"""<tr>
            <td>{html.escape(rec.registration)}</td>
            <td>{html.escape(rec.grade)}</td>
            <td>{html.escape(rec.key_skill)}</td>
            <td>{_fmt_date(rec.open_date)}</td>
            <td>{_fmt_date(rec.expected_closing_date)}</td>
            <td><span class="badge {status_cls}">{html.escape(rec.negotiation_status)}</span></td>
            <td><span class="badge {outcome_cls}">{html.escape(row.outcome.value)}</span></td>
            <td class="num">{html.escape(_days_label(row))}</td>
            <td class="num">{_fmt_money(row.daily_burn)}</td>
            <td class="num">{_fmt_money(row.loss_amount)}</td>
          </tr>"""


def render_html(summary: ReportSummary, source_name: str) -> str:
    """Render a complete HTML report string."""
    table_rows = "\n          ".join(_render_table_row(r) for r in summary.rows)
    return _HTML_TEMPLATE.format(
        as_of=_fmt_date(summary.as_of),
        source_name=html.escape(source_name),
        total_rows=summary.total_rows,
        onboarded_count=summary.onboarded_count,
        at_risk_count=summary.at_risk_count,
        in_loss_count=summary.in_loss_count,
        total_loss=_fmt_money(summary.total_loss),
        status_chips=_render_status_chips(summary.status_counts),
        table_rows=table_rows,
    )


def write_report(
    summary: ReportSummary,
    output_path: Path,
    source_name: str,
) -> None:
    """Write the HTML report to disk."""
    output_path.write_text(
        render_html(summary, source_name),
        encoding="utf-8",
    )
