# Phase 7: Maintenance and Monitoring Plan
## Case 47 – Factory Shop-Floor Execution System (Downtime Logger Prototype)

---

### 1. Document Control
- **Project**: Factory Shop-Floor Execution System – Downtime Logger Prototype
- **Case Reference**: Case 47
- **Lifecycle Phase**: Phase 7 – Maintenance and Monitoring (Final SDLC Phase)
- **Assigned Process Model**: Spiral Model (Continuous risk evaluation & feedback loops)
- **Assigned Agile Method**: Lean Software Development (Elimination of waste, defect prevention)
- **Role**: Senior Python/Flask Maintenance Engineer, Support Engineer & Software Quality Engineer

---

### 2. Phase 7 Objectives & Scope
The objective of Phase 7 is to establish a structured, sustainable maintenance and monitoring regime for the deployed Case 47 academic prototype.

#### In-Scope:
1. **Application Health Monitoring**: Routine execution and logging of the `/health` diagnostic probe.
2. **Shop-Floor Event & Stoppage Tracking**: Real-time review of 40 machines, open stoppage events, closed downtime durations, and estimated financial losses (Rs. 50,000/hr).
3. **Preventive Maintenance Indicators**: Explainable, rule-based indicators identifying repeated equipment stoppages requiring human maintenance technician review.
4. **Defect Tracking & Corrective Maintenance**: Documentation-based defect register capturing bug reproduction, root causes, corrective actions, and verification.
5. **Database Maintenance & Backups**: Verification of SQLite integrity, backup schedules, retention guidelines, and disaster recovery procedures.
6. **Regression & Maintenance Testing**: Full execution of PyTest unit/integration suites and Selenium UI automation to safeguard system integrity after software updates.
7. **Performance & Reliability Monitoring**: Ongoing local benchmarking of response times and batch simulator ingestion.
8. **AI Ethics & Human Oversight**: Safeguarding shop-floor workers against unfair algorithmic blame or automated disciplinary penalties.

#### Out-of-Scope:
- Direct physical PLC, SCADA, or IoT equipment control.
- Automated machine shutdown or remote actuator tripping.
- Commercial 24/7 cloud SLA claims (this is an academic prototype running locally).

---

### 3. Roles and Responsibilities (Proposed Project Assignments)

| Role | Primary Maintenance Responsibilities | Suggested Assignee |
| :--- | :--- | :--- |
| **System Support Engineer** | Monitors application availability via `/health`, reviews error logs, and runs the local monitoring daemon before demonstrations. | Student / Junior Developer |
| **Shop-Floor Supervisor** | Reviews machine downtime history, identifies frequent stoppage trends, and schedules manual mechanical inspections. | Operations Lead (Illustrative) |
| **Maintenance Technician** | Receives human-verified maintenance recommendations, inspects physical tooling, and logs corrective root causes. | Plant Engineering (Illustrative) |
| **QA / Release Engineer** | Executes automated PyTest and Selenium test suites after bug fixes, maintains database backups, and updates the defect register. | QA Specialist |

---

### 4. Structured Maintenance Schedule

| Maintenance Cadence | Activity | Trigger / Method | Expected Evidence / Output |
| :--- | :--- | :--- | :--- |
| **Pre-Demonstration / Daily** | 1. Verify app starts (`python app.py`).<br>2. Check `/health` endpoint.<br>3. Verify database integrity (`backup_db.py --action verify`).<br>4. Test simulator event ingestion. | Manual terminal command or `monitoring/monitor_daemon.py`. | HTTP 200 JSON status; database verified as `ok`. |
| **Weekly** | 1. Review downtime history and repeated stoppage patterns.<br>2. Perform online database backup (`backup_db.py --action backup`).<br>3. Review defect register. | Execute backup utility; inspect `/reports/` Pareto breakdown. | Verified backup file in `backups/`; updated defect log. |
| **After Every Code Change** | 1. Run full PyTest test suite (27 tests).<br>2. Run Selenium UI automation (5 tests).<br>3. Review terminal output for regressions. | `python -m pytest tests/test_*.py -v` | 100% passing test execution report. |
| **Monthly / Milestone Review** | 1. Run local performance benchmark (`python -m monitoring.performance_test`).<br>2. Test backup restoration to an isolated temporary database.<br>3. Review dependencies for security patches. | Execute benchmark script; run test restore. | Benchmarking latency logs; successful restore verification. |

---

### 5. Maintenance Risks and Mitigations

| Identified Risk | Impact | Preventative Mitigation |
| :--- | :---: | :--- |
| **Silent Database Lock or File Corruption** | High | Routine execution of `PRAGMA integrity_check` via `backup_db.py` before and after major operational sessions. |
| **Regression Introduced by Patching** | High | Mandatory execution of all 27 PyTest and 5 Selenium automated test cases before marking any defect CLOSED. |
| **Algorithmic Misattribution of Worker Blame** | High | Clear architectural separation: downtime records store machine state only; human review required before any operational decisions. |
| **Unbounded Log File Growth** | Low | Local application logs (`app_monitor.log`) use standard size bounds; daemon runs for finite configured iterations during testing. |
