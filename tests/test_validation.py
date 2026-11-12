"""
Test Input & Payload Validation
Covers Test Cases:
7. Rejecting blank reason.
15. Malformed JSON or missing simulator fields.
"""
import pytest
from services.validation_service import (
    validate_machine_id,
    validate_reason,
    validate_source,
    validate_simulator_payload,
    parse_iso_timestamp
)

def test_reject_blank_reason():
    """Test 7: Rejecting empty or whitespace reason"""
    valid, msg = validate_reason("")
    assert not valid
    assert "mandatory" in msg.lower()

    valid, msg = validate_reason("   ")
    assert not valid
    assert "mandatory" in msg.lower()

    valid, msg = validate_reason("Valid stoppage reason")
    assert valid

def test_validate_machine_id():
    valid, msg = validate_machine_id("")
    assert not valid
    valid, msg = validate_machine_id("M-001")
    assert valid

def test_validate_simulator_payload_missing_fields():
    """Test 15a: Simulator payload missing mandatory fields"""
    # Missing machine_id
    payload = {"event_type": "STOP", "timestamp": "2026-11-05T10:00:00", "reason": "Test"}
    valid, msg, _ = validate_simulator_payload(payload)
    assert not valid
    assert "machine id is required" in msg.lower()

    # Missing event_type
    payload = {"machine_id": "M-001", "timestamp": "2026-11-05T10:00:00"}
    valid, msg, _ = validate_simulator_payload(payload)
    assert not valid
    assert "event_type" in msg

    # Missing timestamp
    payload = {"event_type": "STOP", "machine_id": "M-001", "reason": "Test"}
    valid, msg, _ = validate_simulator_payload(payload)
    assert not valid
    assert "timestamp" in msg

    # STOP event missing reason
    payload = {"event_type": "STOP", "machine_id": "M-001", "timestamp": "2026-11-05T10:00:00"}
    valid, msg, _ = validate_simulator_payload(payload)
    assert not valid
    assert "mandatory" in msg.lower()

def test_validate_simulator_payload_malformed_timestamp():
    """Test 15b: Rejecting malformed timestamp string"""
    payload = {
        "event_type": "STOP",
        "machine_id": "M-001",
        "timestamp": "not-a-valid-timestamp",
        "reason": "Test reason"
    }
    valid, msg, _ = validate_simulator_payload(payload)
    assert not valid
    assert "invalid timestamp" in msg.lower()
