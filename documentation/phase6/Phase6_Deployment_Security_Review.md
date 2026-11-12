# Phase 6: Deployment Security Review
## Case 47 – Factory Shop-Floor Execution System

---

### 1. Security Review Scope
This review evaluates the security posture of the Case 47 prototype for deployment readiness. The assessment adheres strictly to academic software engineering principles, acknowledging that the application is an educational prototype and not a safety-critical SCADA controller.

---

### 2. Security Audit Checklist & Findings

| Category | Security Check | Current Implementation Status | Risk Assessment |
| :--- | :--- | :--- | :---: |
| **SQL Injection** | Parameterized queries on all SQL operations | **PASS**: 100% of database interactions in `services/` and `database/` use parameter placeholders (`?`). No `eval()`, string interpolation, or raw query concatenation exists. | **LOW (Mitigated)** |
| **Secrets & Keys** | Secret key handling | **PASS**: `SECRET_KEY` is read from environment variables in `config.py`. A local dev fallback is documented, but instructions require a generated token in production. | **LOW (Mitigated)** |
| **Debug Leakage** | Debug mode disabled in production | **PASS**: `ProductionConfig` explicitly enforces `DEBUG = False`. Default 500 error pages return a clean layout without Python stack traces. | **LOW (Mitigated)** |
| **Access Control** | Authentication / Authorization | **NOTE**: Case 47 specifies an open shop-floor tracking module. Authentication is out of scope per academic specification. Role-Based Access Control (RBAC) is documented as an enterprise recommendation. | **INFORMATIONAL** |
| **Input Validation** | Rejection of malformed data | **PASS**: Validation service verifies mandatory reasons, machine IDs, and validates ISO 8601 timestamps using `python-dateutil`. | **LOW (Mitigated)** |
| **Denial of Service** | Idempotency & duplicate events | **PASS**: Unique `event_id` keys prevent replay attacks or duplicate processing of simulated sensor packets. | **LOW (Mitigated)** |
| **Data Privacy** | Collection of sensitive personal data | **PASS**: System collects only machine identifiers, work order numbers, and mechanical stoppage reasons. Zero worker names, payroll data, or biometrics are captured. | **LOW (Mitigated)** |
| **File Permissions** | Database and log file protection | **PASS**: SQLite file permissions match host user rights. The Dockerfile creates a non-root `shopfloor` user (`UID 1000`) rather than running as root. | **LOW (Mitigated)** |

---

### 3. Explicit Boundaries and Limitations

1. **No Physical Machine Control**:
   - The application does **NOT** interface with real-world PLCs, robotics, or electrical switchgear.
   - It cannot actuate physical emergency stops or restart heavy plant equipment.
2. **Simulated Telemetry Only**:
   - All machine events originate from either manual web forms or the HTTP simulator API (`POST /api/simulator/events`).
3. **No Financial Audit Certification**:
   - Financial figures are calculated purely using the assigned academic constant rate of **Rs. 50,000 per hour**. They are labeled in all UI views and reports as **estimates**.
4. **Local Network Deployment Only**:
   - The application is configured to bind to `127.0.0.1` (localhost). It must not be exposed to the public internet without an SSL reverse proxy (e.g., Nginx) and enterprise authentication.
