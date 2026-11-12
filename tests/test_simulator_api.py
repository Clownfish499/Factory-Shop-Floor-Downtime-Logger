"""
Test Simulator API Endpoints
Covers Test Cases:
13. Simulator STOP event.
14. Simulator RESUME event.
15. Malformed JSON or missing simulator fields over HTTP.
Duplicate simulator events & idempotency.
"""
import pytest
import json

def test_simulator_stop_event_api(client):
    """Test 13: Simulator STOP event via API"""
    payload = {
        "machine_id": "M-010",
        "event_type": "STOP",
        "timestamp": "2026-11-05T10:15:00",
        "reason": "Unplanned maintenance",
        "work_order_id": "WO-1001",
        "source": "SIMULATOR",
        "event_id": "SIM-TEST-STOP-01"
    }
    response = client.post(
        "/api/simulator/events",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["status"] == "success"
    assert res_data["data"]["machine_status"] == "DOWN"
    assert res_data["data"]["event_status"] == "OPEN"

def test_simulator_resume_event_api(client):
    """Test 14: Simulator RESUME event via API"""
    # 1. Send STOP first
    stop_payload = {
        "machine_id": "M-011",
        "event_type": "STOP",
        "timestamp": "2026-11-05T10:00:00",
        "reason": "Bearing check",
        "source": "SIMULATOR"
    }
    client.post("/api/simulator/events", data=json.dumps(stop_payload), content_type="application/json")

    # 2. Send RESUME 30 minutes later
    resume_payload = {
        "machine_id": "M-011",
        "event_type": "RESUME",
        "timestamp": "2026-11-05T10:30:00",
        "source": "SIMULATOR"
    }
    response = client.post(
        "/api/simulator/events",
        data=json.dumps(resume_payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["status"] == "success"
    assert res_data["data"]["duration_seconds"] == 1800
    assert res_data["data"]["estimated_cost"] == 25000.0
    assert res_data["data"]["machine_status"] == "RUNNING"
    assert res_data["data"]["event_status"] == "CLOSED"

def test_simulator_api_malformed_json_and_headers(client):
    """Test 15c: Malformed JSON or incorrect content-type headers"""
    # Non-JSON content type
    resp = client.post("/api/simulator/events", data="machine_id=M-001", content_type="text/plain")
    assert resp.status_code == 400
    assert "application/json" in resp.get_json()["message"]

    # Incomplete payload
    incomplete_payload = {
        "machine_id": "M-012"
        # missing event_type and timestamp
    }
    resp = client.post(
        "/api/simulator/events",
        data=json.dumps(incomplete_payload),
        content_type="application/json"
    )
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"

def test_duplicate_event_id_rejection(client):
    """Test idempotency: Same event_id rejected"""
    payload = {
        "machine_id": "M-013",
        "event_type": "STOP",
        "timestamp": "2026-11-05T12:00:00",
        "reason": "Idempotency test",
        "source": "SIMULATOR",
        "event_id": "IDEMPOTENT-EVT-001"
    }
    resp1 = client.post("/api/simulator/events", data=json.dumps(payload), content_type="application/json")
    assert resp1.status_code == 201

    # Same payload with same event_id
    resp2 = client.post("/api/simulator/events", data=json.dumps(payload), content_type="application/json")
    assert resp2.status_code == 400
    assert "already been processed" in resp2.get_json()["message"]
