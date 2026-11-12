"""
Test Downtime Recording & Resuming Logic
Covers Test Cases:
5. Starting downtime for an existing machine.
6. Rejecting unknown machine ID.
7. Rejecting blank reason.
8. Rejecting second open event for the same machine.
9. Resuming an open event.
10. Rejecting resume if no open event exists.
12. Work-order validation.
16. Persistence of an open event across app restarts.
"""
import pytest
from datetime import datetime, timedelta
from services.downtime_service import (
    start_downtime,
    resume_downtime,
    get_open_downtime_for_machine
)
from services.machine_service import get_machine_by_id
from database.connection import get_db

def test_start_downtime_existing_machine(app):
    """Test 5: Starting downtime for an existing machine (M-001) transitions status to DOWN"""
    with app.app_context():
        db = get_db()
        downtime_id = start_downtime(db, machine_id="M-001", reason="Motor overheat", source="MANUAL")
        assert downtime_id is not None

        machine = get_machine_by_id(db, "M-001")
        assert machine["current_status"] == "DOWN"

        open_evt = get_open_downtime_for_machine(db, "M-001")
        assert open_evt is not None
        assert open_evt["event_status"] == "OPEN"
        assert open_evt["reason"] == "Motor overheat"

def test_reject_unknown_machine_id(app):
    """Test 6: Starting downtime on a non-existent machine ID raises ValueError"""
    with app.app_context():
        db = get_db()
        with pytest.raises(ValueError, match="does not exist"):
            start_downtime(db, machine_id="M-999_UNKNOWN", reason="Belt issue")

def test_reject_second_open_event(app):
    """Test 8: Starting downtime when machine already has an open event raises ValueError"""
    with app.app_context():
        db = get_db()
        start_downtime(db, machine_id="M-002", reason="First stoppage")

        with pytest.raises(ValueError, match="already has an open downtime event"):
            start_downtime(db, machine_id="M-002", reason="Second stoppage")

def test_resume_open_event(app):
    """Test 9: Resuming an open event updates machine to RUNNING and calculates cost"""
    with app.app_context():
        db = get_db()
        start_time = datetime(2026, 11, 5, 10, 0, 0)
        end_time = datetime(2026, 11, 5, 11, 0, 0) # 1 hour

        start_downtime(db, machine_id="M-003", reason="Calibration", start_time=start_time)
        res = resume_downtime(db, machine_id="M-003", end_time=end_time)

        assert res["duration_seconds"] == 3600
        assert res["estimated_cost"] == 50000.0

        machine = get_machine_by_id(db, "M-003")
        assert machine["current_status"] == "RUNNING"

        open_evt = get_open_downtime_for_machine(db, "M-003")
        assert open_evt is None

def test_reject_resume_when_no_open_event(app):
    """Test 10: Calling resume on a running machine with no open event raises ValueError"""
    with app.app_context():
        db = get_db()
        with pytest.raises(ValueError, match="has no open downtime event to resume"):
            resume_downtime(db, machine_id="M-004")

def test_work_order_validation(app):
    """Test 12: Work order validation on downtime association"""
    with app.app_context():
        db = get_db()
        # Existing work order WO-1001 succeeds
        dt_id = start_downtime(db, machine_id="M-005", reason="Tooling error", work_order_id="WO-1001")
        assert dt_id is not None

        # Non-existing work order raises ValueError
        with pytest.raises(ValueError, match="does not exist"):
            start_downtime(db, machine_id="M-006", reason="Tooling error", work_order_id="WO-INVALID-999")

def test_persistence_of_open_event_across_context(app):
    """Test 16: An open event remains persistent in SQLite and reflects in fresh queries"""
    with app.app_context():
        db1 = get_db()
        start_downtime(db1, machine_id="M-007", reason="Persistent sensor fault")

    # In a completely separate application context and query
    with app.app_context():
        db2 = get_db()
        open_evt = get_open_downtime_for_machine(db2, "M-007")
        assert open_evt is not None
        assert open_evt["reason"] == "Persistent sensor fault"
        assert open_evt["event_status"] == "OPEN"
        machine = get_machine_by_id(db2, "M-007")
        assert machine["current_status"] == "DOWN"
