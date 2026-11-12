# Phase 7: Defect and Corrective Maintenance Register
## Case 47 – Factory Shop-Floor Execution System

---

### 1. Defect Tracking Process & Standard Workflow
All software bugs and maintenance issues identified across the application lifecycle are logged using this standardized documentation-based register.

#### Status Workflow:
$$\text{OPEN} \longrightarrow \text{IN PROGRESS} \longrightarrow \text{FIXED} \longrightarrow \text{VERIFIED} \longrightarrow \text{CLOSED}$$
*(Optional branch: $\text{DEFERRED}$ for out-of-scope future enhancements).*

---

### 2. Defect Register Template

```markdown
- **Defect ID**: DEF-XXX
- **Date Reported**: YYYY-MM-DD
- **Component**: [Routes / Services / Database / UI / Simulator]
- **Description**: Summary of defect behavior.
- **Severity**: [Critical / High / Medium / Low]
- **Steps to Reproduce**: Detailed reproduction sequence.
- **Expected Result**: Expected application behavior.
- **Actual Result**: Observed failure behavior.
- **Status**: [OPEN / IN PROGRESS / FIXED / VERIFIED / CLOSED / DEFERRED]
- **Root Cause**: Technical analysis of why defect occurred.
- **Corrective Action**: Code changes applied to resolve.
- **Verification Evidence**: Automated test case / command confirming resolution.
- **Closure Date**: YYYY-MM-DD
```

---

### 3. Actual Confirmed Defects & Maintenance Log

#### Defect Record 1: Idempotency Key Validation Preempted by Open Event Check
- **Defect ID**: `DEF-001`
- **Date Reported**: 2026-11-05
- **Component**: `services/downtime_service.py`
- **Description**: Duplicate simulator event submission for an already stopped machine returned machine state error rather than idempotency rejection error.
- **Severity**: High
- **Steps to Reproduce**: POST identical `event_id` twice to `/api/simulator/events` for machine `M-013`.
- **Expected Result**: HTTP 400 Bad Request stating `Event ID ... has already been processed`.
- **Actual Result**: HTTP 400 Bad Request stating `Machine M-013 already has an open downtime event`.
- **Status**: **CLOSED**
- **Root Cause**: Machine status check executed prior to inspecting `event_id` uniqueness.
- **Corrective Action**: Reordered validation checks in `start_downtime()` to verify idempotency before state inspection.
- **Verification Evidence**: Automated test `test_duplicate_event_id_rejection` passed.
- **Closure Date**: 2026-11-05

#### Defect Record 2: Missing Database Import in Health Check Probe
- **Defect ID**: `DEF-002`
- **Date Reported**: 2026-11-05
- **Component**: `app.py`
- **Description**: Invoking `GET /health` triggered a 503 error due to an omitted import.
- **Severity**: Medium
- **Steps to Reproduce**: Execute HTTP GET on `/health`.
- **Expected Result**: HTTP 200 with JSON payload `{"status": "UP", "database": "healthy"}`.
- **Actual Result**: HTTP 503 with log message `NameError: name 'get_db' is not defined`.
- **Status**: **CLOSED**
- **Root Cause**: `get_db` was omitted from top-level imports in `app.py`.
- **Corrective Action**: Added `get_db` to `from database.connection import close_db, get_db`.
- **Verification Evidence**: Automated integration test `test_integration_health_endpoint` passed.
- **Closure Date**: 2026-11-05

#### Defect Record 3: In-Memory Database Table Absence in Standalone Performance Benchmark
- **Defect ID**: `DEF-003`
- **Date Reported**: 2026-11-05
- **Component**: `monitoring/performance_test.py`
- **Description**: Standalone performance benchmark script failed with `sqlite3.OperationalError: no such table: Machine`.
- **Severity**: Medium
- **Steps to Reproduce**: Run `python -m monitoring.performance_test`.
- **Expected Result**: Benchmark executes 50 requests per endpoint and reports latency metrics.
- **Actual Result**: Script crashed due to uninitialized `:memory:` SQLite instance.
- **Status**: **CLOSED**
- **Root Cause**: In SQLite, in-memory databases do not persist across multiple request threads without an initialized shared file.
- **Corrective Action**: Updated script to initialize a seeded temporary disk database (`tempfile.mkstemp(suffix=".db")`).
- **Verification Evidence**: Benchmark script ran 50/50 successful requests across all endpoints.
- **Closure Date**: 2026-11-05

---

### 4. Defect Metrics Summary
- **Total Defects Logged**: 3
- **Total Defects Resolved & Verified**: 3 (100%)
- **Active Open Defects**: 0
- **Deferred Defects**: 0
- **Regression Tests Added**: 3 dedicated test assertions maintaining zero recurrence.
