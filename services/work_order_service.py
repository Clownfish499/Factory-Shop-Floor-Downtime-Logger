"""
Work Order Service
Handles work order retrieval and validation.
"""
def get_all_work_orders(db):
    """Retrieve all work orders."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT work_order_id, description, status, created_at
        FROM WorkOrder
        ORDER BY work_order_id ASC
    """)
    return [dict(row) for row in cursor.fetchall()]

def get_work_order_by_id(db, work_order_id):
    """Retrieve a work order by ID."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT work_order_id, description, status, created_at
        FROM WorkOrder
        WHERE work_order_id = ?
    """, (work_order_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def validate_work_order_exists(db, work_order_id):
    """Checks if work order exists in database."""
    if not work_order_id:
        return True, ""
    wo = get_work_order_by_id(db, work_order_id)
    if not wo:
        return False, f"Work Order '{work_order_id}' does not exist."
    return True, ""
