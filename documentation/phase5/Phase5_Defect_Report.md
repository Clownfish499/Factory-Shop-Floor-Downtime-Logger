# Phase 5: Defect Tracking & Resolution Report
## Case 47 – Factory Shop-Floor Execution System

During Phase 5 testing execution, all defects detected across unit, integration, and performance testing runs were formally logged, isolated, root-cause analyzed, resolved, and verified through regression testing.

---

### Defect 1: Idempotency Validation Precedence
- **Defect ID**: `DEF-001`
- **Related Test Case**: `TC-19` (`test_duplicate_event_id_rejection`)
- **Requirement ID**: `FR-16`, `BR-12`
- **Severity**: High
- **Priority**: High
- **Title**: Idempotency Key Duplicate Check Preempted by Open Event Validation
- **Description**:
  When a simulator event with a duplicate `event_id` was received for an already stopped machine, the downtime service threw `Machine M-xxx already has an open downtime event` instead of the required idempotency rejection message: `Duplicate event rejected. Event ID '...' has already been processed.`
- **Steps to Reproduce**:
  1. POST `/api/simulator/events` with machine `M-013`, event `STOP`, and `event_id: "IDEMPOTENT-EVT-001"`. (Returns 201)
  2. POST `/api/simulator/events` with the exact same payload and duplicate `event_id`.
- **Expected Result**:
  Server rejects with message containing `already been processed`.
- **Actual Result**:
  Server responded with `Machine 'M-013' already has an open downtime event (ID: #1)`.
- **Root Cause**:
  In `services/downtime_service.py`, the check for open machine status `get_open_downtime_for_machine()` was executed before inspecting the uniqueness of the `event_id`.
- **Resolution**:
  Reordered validation checks in `start_downtime()` and `resume_downtime()` to verify event idempotency before machine state inspection.
- **Verification**:
  Reran `pytest tests/test_simulator_api.py -v`. Status: **PASS**.

---

### Defect 2: Missing Health Endpoint Database Import
- **Defect ID**: `DEF-002`
- **Related Test Case**: `TC-32` (`test_integration_health_endpoint`)
- **Requirement ID**: `NFR-03`, `NFR-10`
- **Severity**: Medium
- **Priority**: High
- **Title**: `NameError: name 'get_db' is not defined` on `/health` Endpoint
- **Description**:
  Calling `GET /health` resulted in an unhandled exception and 503 error due to an omitted import in `app.py`.
- **Steps to Reproduce**:
  1. Invoke `GET /health` on the Flask application.
- **Expected Result**:
  HTTP 200 with JSON payload `{"status": "UP", "database": "healthy"}`.
- **Actual Result**:
  HTTP 503 with error logged: `Health check DB probe failed: name 'get_db' is not defined`.
- **Root Cause**:
  In `app.py`, `get_db` was not imported from `database.connection`.
- **Resolution**:
  Added `get_db` to the top-level import statement: `from database.connection import close_db, get_db`.
- **Verification**:
  Reran `pytest tests/test_integration.py -v`. Status: **PASS**.

---

### Defect 3: In-Memory Database Table Absence in Standalone Performance Benchmark
- **Defect ID**: `DEF-003`
- **Related Test Case**: `TC-31`
- **Requirement ID**: `NFR-02`
- **Severity**: Medium
- **Priority**: Medium
- **Title**: SQLite OperationalError (`no such table: Machine`) in Standalone Performance Benchmark
- **Description**:
  When executing `python -m monitoring.performance_test`, the test client used `TestConfig` with `:memory:` database without pre-seeding the schema.
- **Steps to Reproduce**:
  1. Run `python -m monitoring.performance_test`.
- **Expected Result**:
  Benchmark executes 50 requests per endpoint and reports latency metrics.
- **Actual Result**:
  Crashed with `sqlite3.OperationalError: no such table: Machine`.
- **Root Cause**:
  In SQLite, `:memory:` databases do not persist across multiple request threads or contexts without a pre-initialized file or shared cache connection.
- **Resolution**:
  Updated `monitoring/performance_test.py` to initialize an isolated temporary file-based SQLite database (`tempfile.mkstemp(suffix=".db")`) and run `init_db(db_path, populate_sample_data=True)`.
- **Verification**:
  Ran benchmark suite: 50/50 requests completed successfully across all endpoints. Status: **PASS**.

---

### Defect Summary
| Metric | Value |
| :--- | :--- |
| **Total Defects Discovered** | 3 |
| **Defects Resolved & Verified** | 3 (100%) |
| **Critical Defects** | 0 |
| **High Severity Defects** | 1 (Resolved) |
| **Medium Severity Defects** | 2 (Resolved) |
| **Open / Unresolved Defects** | 0 |
