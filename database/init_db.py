import os
import sqlite3
from datetime import datetime

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

SAMPLE_MACHINES = [
    # 40 machines distributed across shop-floor production lines
    {"id": f"M-{i:03d}", "name": f"CNC Machine {i:02d}" if i <= 10 else
                                  (f"Stamping Press {i-10:02d}" if i <= 20 else
                                  (f"Robotic Welder {i-20:02d}" if i <= 30 else f"Assembly Cell {i-30:02d}")),
     "description": f"Shop-Floor Section {((i-1)//10)+1} Workstation"}
    for i in range(1, 41)
]

SAMPLE_WORK_ORDERS = [
    {"id": "WO-1001", "description": "Automotive Chassis Production Batch A", "status": "IN_PROGRESS"},
    {"id": "WO-1002", "description": "Precision Gear Milling Run #44", "status": "IN_PROGRESS"},
    {"id": "WO-1003", "description": "Sheet Metal Bracket Stamping Lot 12", "status": "PLANNED"},
    {"id": "WO-1004", "description": "Robotic Spot Welding Chassis Run", "status": "IN_PROGRESS"},
    {"id": "WO-1005", "description": "Hydraulic Flange Pressing Order", "status": "PLANNED"},
    {"id": "WO-1006", "description": "Powertrain Engine Mount Assembly", "status": "ON_HOLD"},
    {"id": "WO-1007", "description": "Final Inspection & Calibration Cycle", "status": "COMPLETED"},
    {"id": "WO-1008", "description": "Transmission Case Machining", "status": "IN_PROGRESS"},
]

def init_db(db_path="factory.db", populate_sample_data=True):
    """Initializes the database schema and seeds initial data."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cursor = conn.cursor()

    if populate_sample_data:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Seed 40 machines
        for m in SAMPLE_MACHINES:
            cursor.execute("""
                INSERT OR IGNORE INTO Machine (machine_id, machine_name, description, current_status, created_at)
                VALUES (?, ?, ?, 'RUNNING', ?)
            """, (m["id"], m["name"], m["description"], now))

        # Seed sample work orders
        for wo in SAMPLE_WORK_ORDERS:
            cursor.execute("""
                INSERT OR IGNORE INTO WorkOrder (work_order_id, description, status, created_at)
                VALUES (?, ?, ?, ?)
            """, (wo["id"], wo["description"], wo["status"], now))

    conn.commit()
    conn.close()
    print(f"Database successfully initialized at: {db_path} with 40 machines and sample work orders.")

if __name__ == "__main__":
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "factory.db"))
    init_db(db_file)
