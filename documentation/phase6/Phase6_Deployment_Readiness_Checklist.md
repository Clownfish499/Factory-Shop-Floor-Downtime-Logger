# Phase 6: Deployment Readiness Checklist
## Case 47 – Factory Shop-Floor Execution System

Every deployment item is audited and marked with an evidence-based status: **PASS**, **PARTIAL**, **FAIL**, or **NOT VERIFIED**.

---

| Check Category | Inspection Item | Requirement / Criteria | Status | Evidence / Notes |
| :--- | :--- | :--- | :---: | :--- |
| **1. Source Code** | Working code preservation | Existing Flask routes, services, and tests remain intact. | **PASS** | Inspected `app.py`, `routes/`, `services/`, `tests/`. All Phase 5 functionality preserved. |
| | Clean Git state / exclusions | Excludes `.pyc`, `.env`, temporary `.db`, and caches from git. | **PASS** | `.gitignore` verified. |
| **2. Dependencies** | Pinned runtime packages | All runtime requirements defined in `requirements.txt`. | **PASS** | `Flask`, `pytest`, `requests`, `python-dateutil`, `selenium` verified. |
| | Virtual environment support | Standard Python virtualenv creation instructions provided. | **PASS** | Tested in Windows Python 3.13 environment. |
| **3. Configuration** | Environment variable support | Sourcing `SECRET_KEY`, `FLASK_ENV`, `DATABASE_PATH`. | **PASS** | Updated `config.py` with `ProductionConfig`, `DevelopmentConfig`, and `get_config()`. |
| | Safe secrets management | No hardcoded production passwords or secrets committed. | **PASS** | Created `.env.example` with clear placeholders. |
| | Production debug suppression | Debug mode disabled when `FLASK_ENV=production`. | **PASS** | Enforced in `config.py` (`DEBUG = False`). |
| **4. Database** | Persistent SQLite storage | DB stored in persistent location; directory auto-created. | **PASS** | `app.py` auto-creates DB directory and connects persistently to `factory.db`. |
| | Restart persistence | Data remains intact after stopping and restarting app. | **PASS** | Verified via restart script; record `M-015` retained across shutdown. |
| | Backup & restore routines | Hot backup utility and restore verification available. | **PASS** | `database/backup_db.py` tested; 100% integrity check confirmed. |
| | Schema migration limitation | Schema changes documented as fixed academic prototype DDL. | **PASS** | Documented limitation; no breaking migration system introduced. |
| **5. Core Application** | Local startup on port 5000 | App runs and binds to `http://127.0.0.1:5000`. | **PASS** | Verified locally; HTTP 200 responses received. |
| | 40-Machine roster display | All 40 machines seeded with text labels. | **PASS** | Verified in dashboard and `/machines/`. |
| | Downtime start and resume | Transactional state changes and cost calculations (Rs. 50k/hr). | **PASS** | Verified via unit, integration, and Selenium tests. |
| | Simulator API integration | `POST /api/simulator/events` handles STOP and RESUME. | **PASS** | Verified via `test_simulator_api.py` and CLI script. |
| **6. Monitoring** | Health check probe | `/health` endpoint returns JSON status and DB state. | **PASS** | Returns HTTP 200 with `{"status": "UP", "database": "healthy"}`. |
| | Monitoring daemon | Automated periodic availability logging. | **PASS** | Verified `monitoring/monitor_daemon.py` logging to `app_monitor.log`. |
| **7. Security** | Parameterized SQL queries | No string formatting or raw concatenation in SQL. | **PASS** | 100% parameterized queries verified across all services. |
| | Error handling | Suppresses server stack traces on production 500 errors. | **PASS** | Custom error handlers in `app.py`. |
| | Academic scope disclaimers | Clearly states no physical machine connections exist. | **PASS** | Disclaimers embedded in UI footer, README, and docs. |
| **8. Documentation** | Complete Phase 6 docs | All seven Phase 6 reports present in `documentation/phase6/`. | **PASS** | Prepared and verified. |
| | README updated | Setup, run, backup, and test commands match actual project. | **PASS** | Updated root `README.md`. |
| **9. Containerization** | Dockerfile & Compose files | Multi-stage, non-root user, healthcheck, persistent volume. | **PASS** | Authored `Dockerfile`, `.dockerignore`, `docker-compose.yml`. |
| | Docker image build & run | Actual container execution verified on host. | **NOT VERIFIED** | `docker` CLI is not installed on host machine. Documented transparently. |

---

### Readiness Summary
- **Total Audited Items**: 24
- **PASS**: 23 (95.8%)
- **NOT VERIFIED**: 1 (Docker runtime execution due to host environment limitation)
- **FAIL / PARTIAL**: 0
- **Final Verdict**: **READY FOR LOCAL DEMONSTRATION**
