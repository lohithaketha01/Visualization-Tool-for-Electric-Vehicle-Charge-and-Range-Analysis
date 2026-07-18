# VoltScope — Electric Vehicle Charge & Range Analysis

A complete Python 3.11 analytics project for analysing EV charging demand, battery efficiency, driving range, and cost. It implements the requested data pipeline, SQLite persistence, Flask web integration, interactive Plotly dashboard, and a generated Matplotlib report.

## Features

- 900 deterministic sample EV charging sessions generated with Pandas and NumPy
- SQLite `charging_sessions` table with indexes
- Responsive Flask dashboard with Region, Model, and Driving Style filters
- Plotly daily energy trend, range comparison, heatmap, and model ranking
- Saved Matplotlib hourly charging report
- JSON endpoints: `/api/dashboard` and `/api/sessions`
- Automated Flask integration tests

## Run (Python 3.11)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Test

```powershell
python -m pytest -q
```

The database and CSV are created automatically on the first application start.
