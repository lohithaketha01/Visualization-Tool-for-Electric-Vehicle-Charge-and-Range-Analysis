"""Flask application for the EV charge and driving-range dashboard."""
from __future__ import annotations

from pathlib import Path
import sqlite3

from flask import Flask, jsonify, render_template, request

from data_pipeline import bootstrap_database, build_dashboard_payload, fetch_filter_values


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "instance" / "ev_analytics.db"


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(DATABASE=str(DB_PATH), TESTING=False)
    if test_config:
        app.config.update(test_config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    bootstrap_database(Path(app.config["DATABASE"]), BASE_DIR)

    @app.route("/")
    def dashboard():
        filters = {
            "region": request.args.get("region", "All"),
            "model": request.args.get("model", "All"),
            "driving_style": request.args.get("driving_style", "All"),
        }
        payload = build_dashboard_payload(Path(app.config["DATABASE"]), filters)
        return render_template(
            "index.html", payload=payload, filter_values=fetch_filter_values(Path(app.config["DATABASE"])), filters=filters
        )

    @app.route("/api/dashboard")
    def dashboard_api():
        filters = {key: request.args.get(key, "All") for key in ("region", "model", "driving_style")}
        return jsonify(build_dashboard_payload(Path(app.config["DATABASE"]), filters))

    @app.route("/api/sessions")
    def sessions_api():
        connection = sqlite3.connect(app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT session_id, charge_date, vehicle_model, region, charging_duration_mins, energy_consumed_kwh, cost_inr FROM charging_sessions ORDER BY charge_date DESC LIMIT 20"
        ).fetchall()
        connection.close()
        return jsonify([dict(row) for row in rows])

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
