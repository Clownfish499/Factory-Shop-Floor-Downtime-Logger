"""
Downtime Service
Core business logic for recording and resuming downtime events.
Implements FR-04, FR-05, FR-06, FR-07, FR-08, FR-09, FR-10, FR-14, FR-18, FR-19, BR-01 to BR-12.
"""
from datetime import datetime
from services.cost_service import calculate_duration_seconds, calculate_estimated_cost
from services.validation_service import parse_iso_timestamp

def get_open_downtime_for_machine(db, machine_id):
    """Finds currently active/open downtime record for a specific machine."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM DowntimeLog
        WHERE machine_id = ? AND event_status = 'OPEN'
        LIMIT 1
    """, (machine_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def start_downtime(db, machine_id, reason, start_time=None, work_order_id=None, source="MANUAL", event_id=None):
    """
    Starts a downtime event transactionally.
    - Validates machine exists.
    - Validates machine has no current open downtime event.
    - Validates work order if provided.
    - Inserts DowntimeLog record with status 'OPEN'.
    - Updates Machine status to 'DOWN'.
    """
    cursor = db.cursor()

    # 1. Verify machine exists
    cursor.execute("SELECT machine_id, current_status FROM Machine WHERE machine_id = ?", (machine_id,))
    machine = cursor.fetchone()
    if not machine:
        raise ValueError(f"Machine '{machine_id}' does not exist in the system.")

    # 2. Check idempotency if event_id provided (BR-12) FIRST
    if event_id:
        cursor.execute("SELECT downtime_id FROM DowntimeLog WHERE event_id = ?", (event_id,))
        if cursor.fetchone():
            raise ValueError(f"Duplicate event rejected. Event ID '{event_id}' has already been processed.")

    # 3. Check for duplicate open event (FR-14, BR-03)
    open_event = get_open_downtime_for_machine(db, machine_id)
    if open_event:
        raise ValueError(f"Machine '{machine_id}' already has an open downtime event (ID: #{open_event['downtime_id']}).")

    # 4. Verify work order if supplied
    if work_order_id:
        cursor.execute("SELECT work_order_id FROM WorkOrder WHERE work_order_id = ?", (work_order_id,))
        if not cursor.fetchone():
            raise ValueError(f"Work order '{work_order_id}' does not exist.")

    # 5. Format timestamps
    if start_time is None:
        start_dt = datetime.now()
    elif isinstance(start_time, str):
        start_dt = parse_iso_timestamp(start_time)
    else:
        start_dt = start_time

    start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 6. Perform Transactional Insert & Update
    try:
        cursor.execute("""
            INSERT INTO DowntimeLog (
                machine_id, work_order_id, reason, start_time,
                event_status, source, event_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'OPEN', ?, ?, ?, ?)
        """, (machine_id, work_order_id, reason, start_str, source, event_id, now_str, now_str))

        downtime_id = cursor.lastrowid

        cursor.execute("""
            UPDATE Machine
            SET current_status = 'DOWN'
            WHERE machine_id = ?
        """, (machine_id,))

        db.commit()
        return downtime_id
    except Exception as e:
        db.rollback()
        raise e

def resume_downtime(db, machine_id, end_time=None, source="MANUAL", event_id=None):
    """
    Resumes machine and closes the open downtime event transactionally.
    - Validates machine exists.
    - Validates machine has an open downtime event.
    - Computes duration_seconds and estimated_cost.
    - Updates DowntimeLog record to 'CLOSED'.
    - Updates Machine status to 'RUNNING'.
    """
    cursor = db.cursor()

    # 1. Verify machine exists
    cursor.execute("SELECT machine_id, current_status FROM Machine WHERE machine_id = ?", (machine_id,))
    machine = cursor.fetchone()
    if not machine:
        raise ValueError(f"Machine '{machine_id}' does not exist.")

    # 2. Check for open event (FR-08, BR-04)
    open_event = get_open_downtime_for_machine(db, machine_id)
    if not open_event:
        raise ValueError(f"Machine '{machine_id}' has no open downtime event to resume.")

    # 3. Check idempotency if event_id provided (BR-12)
    if event_id:
        cursor.execute("SELECT downtime_id FROM DowntimeLog WHERE event_id = ?", (event_id,))
        if cursor.fetchone():
            raise ValueError(f"Duplicate event rejected. Event ID '{event_id}' has already been processed.")

    # 4. Resolve timestamps
    if end_time is None:
        end_dt = datetime.now()
    elif isinstance(end_time, str):
        end_dt = parse_iso_timestamp(end_time)
    else:
        end_dt = end_time

    start_str = open_event["start_time"]
    start_dt = parse_iso_timestamp(start_str)

    # 5. Calculate duration & cost (BR-05, BR-11)
    if end_dt < start_dt:
        raise ValueError(f"End time ({end_dt}) cannot be earlier than start time ({start_dt}).")

    duration_seconds = calculate_duration_seconds(start_dt, end_dt)
    estimated_cost = calculate_estimated_cost(duration_seconds)

    end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 6. Transactional Close and Machine Update
    try:
        cursor.execute("""
            UPDATE DowntimeLog
            SET end_time = ?,
                duration_seconds = ?,
                estimated_cost = ?,
                event_status = 'CLOSED',
                updated_at = ?
            WHERE downtime_id = ?
        """, (end_str, duration_seconds, estimated_cost, now_str, open_event["downtime_id"]))

        cursor.execute("""
            UPDATE Machine
            SET current_status = 'RUNNING'
            WHERE machine_id = ?
        """, (machine_id,))

        db.commit()
        return {
            "downtime_id": open_event["downtime_id"],
            "machine_id": machine_id,
            "duration_seconds": duration_seconds,
            "estimated_cost": estimated_cost,
            "start_time": start_str,
            "end_time": end_str
        }
    except Exception as e:
        db.rollback()
        raise e

def get_downtime_history(db, machine_id=None, status=None, start_date=None, end_date=None):
    """
    Retrieves filtered downtime log entries with machine and work order details.
    """
    cursor = db.cursor()
    query = """
        SELECT d.*, m.machine_name, w.description as work_order_description
        FROM DowntimeLog d
        JOIN Machine m ON d.machine_id = m.machine_id
        LEFT JOIN WorkOrder w ON d.work_order_id = w.work_order_id
        WHERE 1=1
    """
    params = []

    if machine_id:
        query += " AND d.machine_id = ?"
        params.append(machine_id)
    if status:
        query += " AND d.event_status = ?"
        params.append(status)
    if start_date:
        query += " AND d.start_time >= ?"
        params.append(f"{start_date} 00:00:00")
    if end_date:
        query += " AND d.start_time <= ?"
        params.append(f"{end_date} 23:59:59")

    query += " ORDER BY d.downtime_id DESC"
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

def get_downtime_by_id(db, downtime_id):
    """Fetch single downtime log by ID."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT d.*, m.machine_name, w.description as work_order_description
        FROM DowntimeLog d
        JOIN Machine m ON d.machine_id = m.machine_id
        LEFT JOIN WorkOrder w ON d.work_order_id = w.work_order_id
        WHERE d.downtime_id = ?
    """, (downtime_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def get_dashboard_metrics(db):
    """
    Returns aggregated metrics for dashboard:
    - total machines, running, down
    - open downtime count
    - total closed downtime seconds
    - total estimated cost for closed events
    - 5 recent downtime events
    """
    cursor = db.cursor()

    # Machine counts
    cursor.execute("SELECT COUNT(*) as cnt FROM Machine")
    total_machines = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM Machine WHERE current_status = 'RUNNING'")
    running_machines = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM Machine WHERE current_status = 'DOWN'")
    down_machines = cursor.fetchone()["cnt"]

    # Downtime metrics
    cursor.execute("SELECT COUNT(*) as cnt FROM DowntimeLog WHERE event_status = 'OPEN'")
    open_events_count = cursor.fetchone()["cnt"]

    cursor.execute("""
        SELECT COALESCE(SUM(duration_seconds), 0) as total_duration,
               COALESCE(SUM(estimated_cost), 0.0) as total_cost,
               COUNT(*) as closed_count
        FROM DowntimeLog
        WHERE event_status = 'CLOSED'
    """)
    closed_summary = cursor.fetchone()

    # Recent 5 events
    cursor.execute("""
        SELECT d.*, m.machine_name
        FROM DowntimeLog d
        JOIN Machine m ON d.machine_id = m.machine_id
        ORDER BY d.downtime_id DESC
        LIMIT 5
    """)
    recent_events = [dict(row) for row in cursor.fetchall()]

    return {
        "total_machines": total_machines,
        "running_machines": running_machines,
        "down_machines": down_machines,
        "open_events_count": open_events_count,
        "total_duration_seconds": closed_summary["total_duration"],
        "total_estimated_cost": closed_summary["total_cost"],
        "closed_events_count": closed_summary["closed_count"],
        "recent_events": recent_events
    }

def get_reports_summary(db, start_date=None, end_date=None):
    """
    Aggregated downtime statistics grouped by machine and by reason.
    """
    cursor = db.cursor()

    where_clause = "WHERE d.event_status = 'CLOSED'"
    params = []
    if start_date:
        where_clause += " AND d.start_time >= ?"
        params.append(f"{start_date} 00:00:00")
    if end_date:
        where_clause += " AND d.start_time <= ?"
        params.append(f"{end_date} 23:59:59")

    # Group by machine
    query_machine = f"""
        SELECT d.machine_id, m.machine_name,
               COUNT(d.downtime_id) as event_count,
               COALESCE(SUM(d.duration_seconds), 0) as total_duration_seconds,
               COALESCE(SUM(d.estimated_cost), 0.0) as total_cost
        FROM DowntimeLog d
        JOIN Machine m ON d.machine_id = m.machine_id
        {where_clause}
        GROUP BY d.machine_id, m.machine_name
        ORDER BY total_cost DESC
    """
    cursor.execute(query_machine, params)
    by_machine = [dict(row) for row in cursor.fetchall()]

    # Group by reason
    query_reason = f"""
        SELECT d.reason,
               COUNT(d.downtime_id) as event_count,
               COALESCE(SUM(d.duration_seconds), 0) as total_duration_seconds,
               COALESCE(SUM(d.estimated_cost), 0.0) as total_cost
        FROM DowntimeLog d
        {where_clause}
        GROUP BY d.reason
        ORDER BY total_cost DESC
    """
    cursor.execute(query_reason, params)
    by_reason = [dict(row) for row in cursor.fetchall()]

    # Totals
    total_duration = sum(item["total_duration_seconds"] for item in by_machine)
    total_cost = sum(item["total_cost"] for item in by_machine)
    total_events = sum(item["event_count"] for item in by_machine)

    return {
        "by_machine": by_machine,
        "by_reason": by_reason,
        "total_duration_seconds": total_duration,
        "total_cost": total_cost,
        "total_events": total_events
    }
