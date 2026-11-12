# Phase 6: Software Deployment Plan
## Case 47 – Factory Shop-Floor Execution System (Downtime Logger Prototype)

---

### 1. Document Control
- **Project**: Factory Shop-Floor Execution System – Downtime Logger Prototype
- **Case Reference**: Case 47 (Academic SE Case-Study Assignment)
- **Process Model**: Spiral Model (Risk-driven release preparation)
- **Agile Method**: Lean Software Development (Elimination of deployment waste, reproducible setups)
- **Deployment Target**: Local On-Premises Host / Developer Workstation (Python 3.11 - 3.13)
- **Role**: Senior Python/Flask Deployment Engineer & Software Release Engineer

---

### 2. Deployment Objectives & Scope
The goal of Phase 6 is to package, configure, verify, and document a clean, reproducible, and secure local deployment of the Case 47 web application.

#### In-Scope:
1. **Local Host Setup**: Virtual environment activation, runtime dependency management, environment variable configuration (`.env.example`).
2. **Persistent SQLite Persistence**: Safe initialization, directory auto-creation, restart persistence, and online backup/restore procedures (`database/backup_db.py`).
3. **Application Lifecycle**: Starting, operating, verifying, and cleanly stopping the Flask application on `http://127.0.0.1:5000`.
4. **End-to-End Operational Workflows**: Dashboard KPI monitoring, 40-unit machine roster, manual stoppage logging, machine resumption, Pareto reports, and simulator API calls.
5. **Health & Availability Verification**: Lightweight health endpoint (`/health`) and monitoring script.
6. **Containerization Blueprint**: Non-root production `Dockerfile`, `.dockerignore`, and `docker-compose.yml` with persistent volume bind mounts.
7. **Security & Academic Boundaries**: Disabling production debug mode, parameterized SQL verification, and clear disclaimers regarding simulated industrial machinery.

#### Out-of-Scope:
- Deployment to public cloud hosting or external internet exposure without user credentials.
- Integration with real industrial PLC, SCADA, or factory floor machinery.
- High-concurrency clustering (the prototype utilizes SQLite suitable for local academic evaluation).

---

### 3. Deployment Architecture

```
   [ Local Web Browser ]  -->  http://127.0.0.1:5000 (Chrome / Edge / Firefox)
              │
              ▼
   [ Application Server ] -->  Flask WSGI Application (`app.py`)
                               ├── Config Engine (`config.py`)
                               ├── Controllers (`routes/`)
                               ├── Services (`services/`)
                               └── Health Monitor (`/health`)
              │
              ▼
   [ Persistent Storage ] -->  SQLite Database (`factory.db` / `database/`)
                               └── Hot Backups (`database/backup_db.py` -> `backups/`)
```

---

### 4. Configuration & Environment Strategy
Configuration is managed dynamically via `config.py` and environment variables:
- **`FLASK_ENV`**: Sets `development` (with interactive debug) or `production` (debug disabled).
- **`SECRET_KEY`**: Sourced from environment variable with a documented local development fallback.
- **`DATABASE_PATH`**: Configurable relative or absolute path; defaults to `./factory.db`.
- **`DOWNTIME_HOURLY_RATE`**: Case 47 parameter: Rs. 50,000 per hour.
- **`FLASK_RUN_HOST` / `FLASK_RUN_PORT`**: Binds by default to loopback `127.0.0.1:5000`.

---

### 5. Deployment Risks and Mitigations

| Deployment Risk | Severity | Mitigation Strategy |
| :--- | :---: | :--- |
| **Accidental Database Overwrite** | High | `init_db.py` uses `INSERT OR IGNORE` and checks table existence; `app.py` auto-connects to existing database without re-seeding. |
| **Production Debug Vulnerability** | High | In `ProductionConfig`, `DEBUG = False` is enforced; stack traces are suppressed from client responses. |
| **Data Loss on Container Restart** | Medium | Dockerfile declares `VOLUME ["/app/data"]` and compose mounts `./data:/app/data` to host storage. |
| **Concurrent Write Locks in SQLite** | Medium | Database timeout and connection teardown (`@app.teardown_appcontext(close_db)`) ensure immediate connection disposal. |

---

### 6. Rollback Approach
If a deployment step fails or an unexpected corruption occurs:
1. Terminate the application process (`Ctrl+C`).
2. Run database integrity check: `python database/backup_db.py --action verify`.
3. Restore the last known good backup: `python database/backup_db.py --action restore --src backups/<backup_file>.db --db factory.db`.
4. Restart the application: `python app.py`.
