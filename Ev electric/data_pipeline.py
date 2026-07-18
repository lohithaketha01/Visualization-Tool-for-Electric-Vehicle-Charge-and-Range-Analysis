"""Data generation, SQLite persistence, and dashboard analytics."""
from __future__ import annotations

from pathlib import Path
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


MODELS = {
    "Tata Nexon EV": {"battery": 40.5, "efficiency": 6.5, "price": 1450000},
    "MG ZS EV": {"battery": 50.3, "efficiency": 6.0, "price": 1899000},
    "Hyundai Kona": {"battery": 39.2, "efficiency": 6.2, "price": 2371000},
    "BYD Atto 3": {"battery": 60.5, "efficiency": 5.7, "price": 2499000},
    "Mahindra XUV400": {"battery": 39.4, "efficiency": 6.3, "price": 1599000},
}
REGIONS = ["Hyderabad", "Bengaluru", "Chennai", "Mumbai", "Pune"]
STYLES = {"Eco": 1.08, "Normal": 1.0, "Sport": 0.84}


def generate_sample_data(seed: int = 42, records: int = 900) -> pd.DataFrame:
    """Create deterministic, realistic charging and range observations."""
    rng = np.random.default_rng(seed)
    model_names = list(MODELS)
    rows = []
    dates = pd.date_range("2026-01-01", periods=180, freq="D")
    for index in range(records):
        model = str(rng.choice(model_names))
        spec = MODELS[model]
        style = str(rng.choice(list(STYLES), p=[0.30, 0.50, 0.20]))
        soc_start = float(rng.uniform(12, 55))
        soc_end = float(rng.uniform(max(soc_start + 20, 65), 98))
        charged_pct = soc_end - soc_start
        energy = max(4, spec["battery"] * charged_pct / 100 * rng.normal(1, 0.035))
        power = float(rng.choice([3.3, 7.2, 22, 50], p=[0.12, 0.43, 0.25, 0.20]))
        duration = energy / power * 60 + rng.normal(4, 3)
        efficiency = spec["efficiency"] * STYLES[style] * rng.normal(1, 0.045)
        predicted = spec["battery"] * soc_end / 100 * efficiency
        actual = predicted * rng.normal(0.965, 0.055)
        date = pd.Timestamp(rng.choice(dates)) + pd.Timedelta(hours=int(rng.integers(0, 24)), minutes=int(rng.integers(0, 60)))
        rows.append({
            "session_id": f"EV{index + 1:04d}", "charge_date": date.isoformat(), "vehicle_model": model,
            "region": str(rng.choice(REGIONS)), "driving_style": style, "charger_type": "DC Fast" if power >= 50 else "AC",
            "battery_capacity_kwh": spec["battery"], "state_of_charge_start": round(soc_start, 1), "state_of_charge_end": round(soc_end, 1),
            "charging_power_kw": power, "charging_duration_mins": round(max(duration, 10), 1), "energy_consumed_kwh": round(energy, 2),
            "charging_cost_inr_per_kwh": round(float(rng.uniform(7.0, 12.0)), 2), "efficiency_km_per_kwh": round(efficiency, 2),
            "predicted_range_km": round(predicted, 1), "actual_range_km": round(max(actual, 30), 1), "vehicle_price_inr": spec["price"],
        })
    frame = pd.DataFrame(rows)
    frame["cost_inr"] = (frame["energy_consumed_kwh"] * frame["charging_cost_inr_per_kwh"]).round(2)
    return frame


def bootstrap_database(db_path: Path, base_dir: Path) -> None:
    """Persist generated data only when the SQLite table has not yet been created."""
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    db_path.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(db_path)
    exists = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='charging_sessions'").fetchone()
    if not exists:
        frame = generate_sample_data()
        frame.to_csv(data_dir / "ev_charging_sessions.csv", index=False)
        frame.to_sql("charging_sessions", connection, index=False)
        connection.execute("CREATE INDEX idx_sessions_region ON charging_sessions(region)")
        connection.execute("CREATE INDEX idx_sessions_model ON charging_sessions(vehicle_model)")
        connection.commit()
        _save_matplotlib_chart(frame, base_dir)
    connection.close()


def _save_matplotlib_chart(frame: pd.DataFrame, base_dir: Path) -> None:
    image_dir = base_dir / "static" / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    hourly = pd.to_datetime(frame["charge_date"]).dt.hour.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.bar(hourly.index, hourly.values, color="#26c6da")
    ax.set(title="Charging sessions by hour", xlabel="Hour of day", ylabel="Sessions")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(image_dir / "charging_by_hour.png", dpi=140)
    plt.close(fig)


def fetch_filter_values(db_path: Path) -> dict[str, list[str]]:
    connection = sqlite3.connect(db_path)
    values = {column: [row[0] for row in connection.execute(f"SELECT DISTINCT {column} FROM charging_sessions ORDER BY {column}")] for column in ("region", "vehicle_model", "driving_style")}
    connection.close()
    return values


def _load_filtered(db_path: Path, filters: dict[str, str]) -> pd.DataFrame:
    mapping = {"region": "region", "model": "vehicle_model", "driving_style": "driving_style"}
    conditions, params = [], []
    for key, column in mapping.items():
        value = filters.get(key, "All")
        if value != "All":
            conditions.append(f"{column} = ?")
            params.append(value)
    query = "SELECT * FROM charging_sessions" + (" WHERE " + " AND ".join(conditions) if conditions else "")
    connection = sqlite3.connect(db_path)
    data = pd.read_sql_query(query, connection, params=params)
    connection.close()
    return data


def _chart_json(figure: go.Figure) -> str:
    figure.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=35, r=20, t=45, b=35), font=dict(family="Inter, Arial"))
    return figure.to_json()


def build_dashboard_payload(db_path: Path, filters: dict[str, str]) -> dict:
    data = _load_filtered(db_path, filters)
    if data.empty:
        return {"metrics": {}, "charts": {}, "empty": True}
    data["charge_date"] = pd.to_datetime(data["charge_date"])
    data["hour"] = data["charge_date"].dt.hour
    data["day"] = data["charge_date"].dt.date
    daily = data.groupby("day", as_index=False).agg(energy_consumed_kwh=("energy_consumed_kwh", "sum"))
    by_model = data.groupby("vehicle_model", as_index=False).agg(actual_range_km=("actual_range_km", "mean"), efficiency_km_per_kwh=("efficiency_km_per_kwh", "mean"))
    heat = data.groupby(["region", "hour"], as_index=False).size().rename(columns={"size": "sessions"})
    range_scatter = px.scatter(data, x="predicted_range_km", y="actual_range_km", color="vehicle_model", hover_data=["driving_style", "region"], title="Predicted vs. actual driving range")
    return {
        "empty": False,
        "metrics": {
            "sessions": int(len(data)), "energy": round(float(data.energy_consumed_kwh.sum()), 1),
            "range": round(float(data.actual_range_km.mean()), 1), "cost": round(float(data.cost_inr.sum()), 0),
        },
        "charts": {
            "daily": _chart_json(px.line(daily, x="day", y="energy_consumed_kwh", title="Daily charging energy (kWh)", markers=True)),
            "models": _chart_json(px.bar(by_model, x="vehicle_model", y="actual_range_km", color="efficiency_km_per_kwh", color_continuous_scale="Teal", title="Average range by EV model")),
            "heatmap": _chart_json(px.density_heatmap(heat, x="hour", y="region", z="sessions", histfunc="sum", color_continuous_scale="Viridis", title="Charging-demand heatmap")),
            "range": _chart_json(range_scatter),
        },
    }
