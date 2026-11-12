"""
Validation Service
Implements FR-13, FR-16, NFR-07, and Business Rules validation.
"""
from datetime import datetime
from dateutil import parser

def parse_iso_timestamp(timestamp_str):
    """
    Parses ISO 8601 or common timestamp formats into a naive or standard datetime object.
    Raises ValueError if invalid format.
    """
    if not timestamp_str or not isinstance(timestamp_str, str):
        raise ValueError("Timestamp must be a non-empty string.")
    try:
        dt = parser.isoparse(timestamp_str)
        # Standardize to naive format for SQLite consistency (YYYY-MM-DD HH:MM:SS)
        return dt.replace(tzinfo=None)
    except Exception as e:
        raise ValueError(f"Invalid timestamp format '{timestamp_str}'. Expected ISO 8601 (e.g., YYYY-MM-DDTHH:MM:SS).")

def validate_machine_id(machine_id):
    """Validates machine ID format."""
    if not machine_id or not isinstance(machine_id, str) or not machine_id.strip():
        return False, "Machine ID is required."
    return True, ""

def validate_reason(reason):
    """Validates downtime reason (mandatory for STOP event)."""
    if not reason or not isinstance(reason, str) or not reason.strip():
        return False, "Downtime reason is mandatory and cannot be empty."
    if len(reason.strip()) > 500:
        return False, "Downtime reason exceeds maximum length of 500 characters."
    return True, ""

def validate_source(source):
    """Validates event source."""
    if source not in ("MANUAL", "SIMULATOR"):
        return False, "Source must be either 'MANUAL' or 'SIMULATOR'."
    return True, ""

def validate_simulator_payload(data):
    """
    Validates JSON payload received from simulator.
    Returns (is_valid, error_message, parsed_data)
    """
    if not isinstance(data, dict):
        return False, "Payload must be a valid JSON object.", None

    event_type = data.get("event_type")
    if event_type not in ("STOP", "RESUME"):
        return False, "event_type must be either 'STOP' or 'RESUME'.", None

    machine_id = data.get("machine_id")
    is_valid_mid, err_mid = validate_machine_id(machine_id)
    if not is_valid_mid:
        return False, err_mid, None

    timestamp_raw = data.get("timestamp")
    if not timestamp_raw:
        return False, "timestamp field is required.", None

    try:
        dt = parse_iso_timestamp(timestamp_raw)
    except ValueError as ve:
        return False, str(ve), None

    source = data.get("source", "SIMULATOR")
    is_valid_src, err_src = validate_source(source)
    if not is_valid_src:
        return False, err_src, None

    reason = data.get("reason", "")
    if event_type == "STOP":
        is_valid_r, err_r = validate_reason(reason)
        if not is_valid_r:
            return False, err_r, None

    work_order_id = data.get("work_order_id")
    if work_order_id and isinstance(work_order_id, str):
        work_order_id = work_order_id.strip()
    else:
        work_order_id = None

    event_id = data.get("event_id")
    if event_id and isinstance(event_id, str):
        event_id = event_id.strip()
    else:
        event_id = None

    parsed = {
        "event_type": event_type,
        "machine_id": machine_id.strip(),
        "timestamp": dt,
        "source": source,
        "reason": reason.strip() if reason else None,
        "work_order_id": work_order_id,
        "event_id": event_id
    }
    return True, "", parsed
