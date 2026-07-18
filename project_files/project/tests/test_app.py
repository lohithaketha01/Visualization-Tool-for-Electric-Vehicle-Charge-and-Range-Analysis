from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app


def test_dashboard_and_api(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "analytics.db")})
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Charge & range analytics" in response.data
    data = client.get("/api/dashboard").get_json()
    assert data["metrics"]["sessions"] == 900
    sessions = client.get("/api/sessions").get_json()
    assert len(sessions) == 20


def test_filter_returns_data(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "analytics.db")})
    response = app.test_client().get("/api/dashboard?region=Hyderabad&model=Tata%20Nexon%20EV")
    assert response.status_code == 200
    assert response.get_json()["metrics"]["sessions"] > 0
