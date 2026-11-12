# Phase 5: Software Test Plan
## Case 47 – Factory Shop-Floor Execution System (Downtime Logger Prototype)

---

### 1. Document Control
- **Project**: Factory Shop-Floor Execution System – Downtime Logger Prototype
- **Case Reference**: Case 47
- **Development Lifecycle**: Spiral Model (Risk-driven iterative testing)
- **Agile Methodology**: Lean Software Development (Eliminating test redundancy, fast feedback)
- **Target System**: Local Python/Flask Web Application + SQLite Persistence
- **Prepared By**: Senior QA & Test Automation Specialist

---

### 2. Objectives & Scope
The primary objective of Phase 5 testing is to verify that all functional requirements (**FR-01 to FR-24**), non-functional requirements (**NFR-01 to NFR-12**), and business rules (**BR-01 to BR-12**) operate with 100% data integrity, predictable fault recovery, and accurate financial estimations.

#### In-Scope:
1. **Unit Testing**: PyTest validation of cost algorithms (Rs. 50,000/hr), timestamp parsers, schema validations, and transactional state transitions.
2. **Integration Testing**: End-to-end integration across Flask blueprints, transactional services, SQLite database constraints, and REST API controllers.
3. **System Testing**: Complete user journey verification from UI dashboard to downtime reports and machine detail screens.
4. **Selenium UI Automation**: Headless browser testing verifying page rendering, dynamic form submissions, DOM states, and JavaScript alert handling.
5. **Machine Simulator API Integration**: Validation of JSON payloads (`POST /api/simulator/events`), idempotency keys, and error status codes.
6. **Reliability & Performance Testing**: Batch simulation load checks, transaction rollback guarantees, and health monitoring.
7. **Static Code Quality Analysis**: SonarQube configuration and code smell inspection.
8. **AI-Assisted Testing & Worker Ethics Review**: Automated review assessment and human worker protection safeguards.

#### Out-of-Scope:
- Physical PLC/SCADA hardware integration or remote machine shutdown signals.
- Audited enterprise financial accounting (all values labeled as estimates).
- Distributed cloud scalability testing.

---

### 3. Testing Strategy & Spiral/Lean Mapping

#### 3.1 Spiral Model Alignment (Risk-Driven)
Testing is organized in concentric cycles based on technical and business risk:
- **Cycle 1 (Core Financial & Data Integrity Risk)**: Cost calculation engine (Rs. 50,000/hr, midnight crossing), duplicate open stoppage prevention, SQLite foreign keys.
- **Cycle 2 (Integration & API Risk)**: Simulator JSON event receiver, idempotency keys, transactional boundary rollback on failure.
- **Cycle 3 (Presentation & Usability Risk)**: Selenium UI automation, filter bar queries, alert messaging.
- **Cycle 4 (Operational Risk)**: Heartbeat monitoring daemon, continuous error logging, performance benchmarks.

#### 3.2 Lean Software Development Board
| TO DO | DOING | TESTED | FIXED | DONE |
| :--- | :--- | :--- | :--- | :--- |
| Cloud SonarQube Scanner | - | Health check `/health` | Import error in `app.py` | Cost Unit Tests (5/5) |
| Physical SCADA (Out of scope) | - | Batch Simulator Ingestion | Idempotency sequence | Downtime Service Tests (7/7) |
| - | - | SQLite Foreign Keys | Performance test DB config | Validation Tests (4/4) |
| - | - | Headless Chrome Automation | - | Simulator API Tests (4/4) |
| - | - | Reports Pareto Breakdown | - | Integration Tests (7/7) |
| - | - | Midnight crossing | - | Selenium UI Tests (5/5) |

---

### 4. Test Environment & Tooling
- **OS**: Windows (PowerShell / Command Prompt)
- **Runtime**: Python 3.13.2
- **Test Framework**: PyTest 9.2.0
- **Browser Automation**: Selenium WebDriver 4.52.0 (Headless Google Chrome)
- **HTTP Client**: Requests 2.34.2 & urllib.request
- **Database**: SQLite3 (`:memory:` or temporary disk `.db` per test session to guarantee demo data isolation)
- **Static Analysis**: SonarQube configuration (`sonar-project.properties`)

---

### 5. Pass/Fail Criteria
- **Pass Criteria**:
  - 100% of functional requirements (FR-01 to FR-24) mapped to passing automated test cases.
  - Zero unhandled exceptions or data corruption in SQLite database.
  - Test database isolation maintained (no modification of production `factory.db`).
  - Average local response time under 100ms for core endpoints.
- **Suspension Criteria**:
  - SQLite database locking failures or unhandled server 500 errors.
  - Inaccurate cost calculation deviation exceeding Rs. 0.01.
