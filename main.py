"""Generate HRM HTML loss report from hrmdata.txt."""

from pathlib import Path

from hrm.data_layer import load_resources
from hrm.report import compute_report
from hrm.report_html import write_report

DATA_FILE = Path(__file__).parent / "hrmdata.txt"
OUTPUT_FILE = Path(__file__).parent / "report.html"


def main() -> None:
    records = load_resources(DATA_FILE)
    summary = compute_report(records)
    write_report(summary, OUTPUT_FILE, source_name=DATA_FILE.name)
    print(f"Wrote {OUTPUT_FILE}")
    print(f"  Resources: {summary.total_rows}")
    print(f"  Onboarded: {summary.onboarded_count}")
    print(f"  At risk:   {summary.at_risk_count}")
    print(f"  In loss:   {summary.in_loss_count}")
    print(f"  Total loss: ${summary.total_loss:,.2f}")


if __name__ == "__main__":
    main()
