-- Factory Shop-Floor Execution System - Downtime Logger Schema
-- Case 47 Architecture - SQLite Database

PRAGMA foreign_keys = ON;

-- 1. Machine Table
CREATE TABLE IF NOT EXISTS Machine (
    machine_id TEXT PRIMARY KEY,
    machine_name TEXT NOT NULL,
    description TEXT,
    current_status TEXT NOT NULL CHECK(current_status IN ('RUNNING', 'DOWN')),
    created_at DATETIME NOT NULL
);

-- 2. WorkOrder Table
CREATE TABLE IF NOT EXISTS WorkOrder (
    work_order_id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD')),
    created_at DATETIME NOT NULL
);

-- 3. DowntimeLog Table
CREATE TABLE IF NOT EXISTS DowntimeLog (
    downtime_id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    work_order_id TEXT,
    reason TEXT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_seconds INTEGER,
    estimated_cost REAL,
    event_status TEXT NOT NULL CHECK(event_status IN ('OPEN', 'CLOSED')),
    source TEXT NOT NULL CHECK(source IN ('MANUAL', 'SIMULATOR')),
    event_id TEXT UNIQUE, -- Optional idempotency key for simulator events
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (machine_id) REFERENCES Machine (machine_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (work_order_id) REFERENCES WorkOrder (work_order_id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Indexes for performance and traceability
CREATE INDEX IF NOT EXISTS idx_downtime_machine ON DowntimeLog(machine_id);
CREATE INDEX IF NOT EXISTS idx_downtime_status ON DowntimeLog(event_status);
CREATE INDEX IF NOT EXISTS idx_downtime_start ON DowntimeLog(start_time);
