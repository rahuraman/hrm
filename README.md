# HRM Resource Onboarding & Loss Report

Python app that reads resource negotiation data from CSV, calculates onboarding loss (8 billable hours/day for resources not **Closed** by the expected closing date), and generates an HTML dashboard.

## Project structure

```
HRM/
├── main.py              # Entry point
├── hrmdata.txt          # Source data (CSV)
├── report.html          # Generated report (run main.py)
└── hrm/
    ├── data_layer.py    # Load and parse CSV
    ├── report.py        # Loss and status analytics
    └── report_html.py   # HTML report renderer
```

## Requirements

- Python 3.10+
- [Git](https://git-scm.com/download/win) (for version control)

## Generate the report

```powershell
cd c:\Lava\project\HRM
python main.py
```

Open `report.html` in a browser.

## Loss rules

| Condition | Outcome |
|-----------|---------|
| Status is **Closed** | Onboarded — no loss |
| Not Closed, before closing date | At risk — no loss yet |
| Not Closed, after closing date | Loss = days overdue × 8 hours × hourly rate |

## GitHub repository

Remote: [https://github.com/rahuraman/hrm](https://github.com/rahuraman/hrm)

Push your local `main` branch (sign in when prompted):

```powershell
cd c:\Lava\project\HRM
git push -u origin main
```

Use a [Personal Access Token](https://github.com/settings/tokens) as the password if Git asks for credentials over HTTPS.

## Initialize Git (first time)

If Git is installed, from this folder:

```powershell
.\init-git.ps1
```

Or manually:

```powershell
git init
git remote add origin https://github.com/rahuraman/hrm.git
git add .
git commit -m "Initial commit: HRM modular report generator"
git branch -M main
git push -u origin main
```

## Data format

`hrmdata.txt` is CSV with header:

`Registration number, grade, open date, key skill, expected closing date, negotiation status, hourly rate`
