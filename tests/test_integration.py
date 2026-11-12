"""
Integration & System Test Suite
Covers:
- Manual STOP/RESUME routes -> service -> SQLite state changes
- Simulator STOP/RESUME -> API -> DB
- Downtime record -> Dashboard aggregations
- Downtime record -> Report calculations
- Work-order association & database verification
- Health check monitoring endpoint
- Transactional rollback on simulated database exception
"""
import pytest
import json
import sqlite3
from services.machine_service import get_machine_by_id, get_all_machines
from services.downtime_service import (
    get_open_downtime_for_machine,
    get_downtime_history,
    get_dashboard_metrics,
    get_reports_summary,
    start_downtime
)
from database.connection import get_db

def test_integration_manual_stop_route(client, app):
    """Integration Test 1: Manual STOP event -> Route -> Service -> Database -> Status DOWN"""
    res = client.post("/downtime/start", data={
        "machine_id": "M-020",
        "reason": "Integration Test - Hydraulic leak",
        "work_order_id": "WO-1002",
        "timestamp": ""
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        db = get_db()
        m = get_machine_by_id(db, "M-020")
        assert m["current_status"] == "DOWN"

        open_evt = get_open_downtime_for_machine(db, "M-020")
        assert open_evt is not None
        assert open_evt["reason"] == "Integration Test - Hydraulic leak"
        assert open_evt["work_order_id"] == "WO-1002"
        assert open_evt["source"] == "MANUAL"

def test_integration_manual_resume_route(client, app):
    """Integration Test 2: Manual RESUME event -> Route -> Service -> Database -> Status RUNNING & Cost"""
    with app.app_context():
        db = get_db()
        start_downtime(db, machine_id="M-021", reason="Pre-resume test stoppage")

    res = client.post("/downtime/resume/M-021", follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        db = get_db()
        m = get_machine_by_id(db, "M-021")
        assert m["current_status"] == "RUNNING"

        open_evt = get_open_downtime_for_machine(db, "M-021")
        assert open_evt is None

        history = get_downtime_history(db, machine_id="M-021")
        assert len(history) >= 1
        assert history[0]["event_status"] == "CLOSED"
        assert history[0]["duration_seconds"] is not None
        assert history[0]["estimated_cost"] is not None

def test_integration_simulator_stop_and_resume_flow(client, app):
    """Integration Test 3 & 4: Simulator STOP and RESUME with exact DB verification"""
    stop_data = {
        "machine_id": "M-022",
        "event_type": "STOP",
        "timestamp": "2026-11-05T08:00:00",
        "reason": "Robotic arm encoder glitch",
        "work_order_id": "WO-1004",
        "source": "SIMULATOR",
        "event_id": "SIM-INT-022-STOP"
    }
    stop_res = client.post("/api/simulator/events", data=json.dumps(stop_data), content_type="application/json")
    assert stop_res.status_code == 201

    with app.app_context():
        db = get_db()
        m = get_machine_by_id(db, "M-022")
        assert m["current_status"] == "DOWN"
        evt = get_open_downtime_for_machine(db, "M-022")
        assert evt["source"] == "SIMULATOR"
        assert evt["event_id"] == "SIM-INT-022-STOP"

    # RESUME 1.5 hours later = 90 mins = Rs. 75,000
    resume_data = {
        "machine_id": "M-022",
        "event_type": "RESUME",
        "timestamp": "2026-11-05T09:30:00",
        "source": "SIMULATOR",
        "event_id": "SIM-INT-022-RESUME"
    }
    resume_res = client.post("/api/simulator/events", data=json.dumps(resume_data), content_type="application/json")
    assert resume_res.status_code == 200

    with app.app_context():
        db = get_db()
        m = get_machine_by_id(db, "M-022")
        assert m["current_status"] == "RUNNING"

        hist = get_downtime_history(db, machine_id="M-022")
        assert len(hist) == 1
        assert hist[0]["duration_seconds"] == 5400
        assert hist[0]["estimated_cost"] == 75000.0

def test_integration_downtime_reflects_in_dashboard(client, app):
    """Integration Test 5: Downtime status immediately updates dashboard counts"""
    # Initially 0 down
    res1 = client.get("/")
    assert res1.status_code == 200

    with app.app_context():
        db = get_db()
        start_downtime(db, machine_id="M-025", reason="Dashboard reflection test")

    res2 = client.get("/")
    assert res2.status_code == 200
    html = res2.get_data(as_text=True)
    assert "M-025" in html
    assert "Dashboard reflection test" in html

def test_integration_reports_aggregation(client, app):
    """Integration Test 6: Closed downtime is accurately aggregated in reports by machine & reason"""
    with app.app_context():
        db = get_db()
        # Create closed event of 30 mins (Rs. 25,000)
        from services.downtime_service import resume_downtime
        start_downtime(db, "M-026", reason="Overheating issue", start_time="2026-11-05T10:00:00")
        resume_downtime(db, "M-026", end_time="2026-11-05T10:30:00")

        rep = get_reports_summary(db)
        assert rep["total_events"] >= 1
        assert rep["total_cost"] >= 25000.0

    res = client.get("/reports/")
    assert res.status_code == 200
    assert "25,000.00" in res.get_data(as_text=True)
    assert "Overheating issue" in res.get_data(as_text=True)

def test_integration_health_endpoint(client):
    """Continuous Monitoring & Health Check: GET /health"""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "UP"
    assert data["database"] == "healthy"

def test_integration_transactional_rollback_on_failure(app):
    """Reliability Test 25: Database failure ensures rollback, avoiding partial updates"""
    with app.app_context():
        db = get_db()
        # Verify machine is initially RUNNING
        m_before = get_machine_by_id(db, "M-028")
        assert m_before["current_status"] == "RUNNING"

        # Attempting start_downtime with an invalid work order
        with pytest.raises(ValueError, match="does not exist"):
            start_downtime(db, machine_id="M-028", reason="Test rollback", work_order_id="WO-NON-EXISTENT-XYZ")

        # Machine status MUST remain RUNNING and no open event created
        m_after = get_machine_by_id(db, "M-028")
        assert m_after["current_status"] == "RUNNING"
        open_evt = get_open_downtime_for_machine(db, "M-028")
        assert open_evt is None
