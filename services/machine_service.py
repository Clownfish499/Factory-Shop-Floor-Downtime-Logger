"""
Machine Service
Handles machine queries and listings.
"""
def get_all_machines(db):
    """Retrieve all machines ordered by machine_id."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT machine_id, machine_name, description, current_status, created_at
        FROM Machine
        ORDER BY machine_id ASC
    """)
    return [dict(row) for row in cursor.fetchall()]

def get_machine_by_id(db, machine_id):
    """Retrieve a single machine by machine_id."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT machine_id, machine_name, description, current_status, created_at
        FROM Machine
        WHERE machine_id = ?
    """, (machine_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def get_machine_summary_counts(db):
    """Returns total, running, and down machine counts."""
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM Machine")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as running FROM Machine WHERE current_status = 'RUNNING'")
    running = cursor.fetchone()["running"]

    cursor.execute("SELECT COUNT(*) as down FROM Machine WHERE current_status = 'DOWN'")
    down = cursor.fetchone()["down"]

    return {
        "total": total,
        "running": running,
        "down": down
    }
