# Factory Shop-Floor Execution System – Downtime Logger Prototype (Case 47)

An academic Software Engineering prototype tracking work orders, machine operations, and downtime costs across a 40-workstation manufacturing plant.

---

## 📌 Project Overview & Case Facts (Case 47)
- **Scenario**: Tracks manufacturing work orders and machine downtime across 40 shop-floor machines.
- **Downtime Financial Rate**: Estimated at **Rs. 50,000 per hour** (`Cost = (duration_seconds / 3600) * 50,000`).
- **Software Engineering Process Model**: Spiral Model (Iterative risk-driven increments).
- **Agile Methodology**: Lean Software Development (Eliminating waste, rapid feedback, fast iterations).
- **Architecture**: 3-Tier Layered Architecture (Presentation, Application Services, SQLite Persistence).

> **Important Boundary & Academic Disclaimer**:
> This prototype is developed strictly for educational/academic evaluation. It does **NOT** connect to physical PLCs, SCADA systems, or real industrial hardware. It does **NOT** execute remote machine commands. Financial values are labeled and calculated as estimates based on Case 47 parameters.

---

## ⚙️ Architecture & Tech Stack

```
   [ Presentation Layer ]  -->  HTML5, CSS3, JavaScript, Jinja2 Templates
            │
   [ Application Layer ]   -->  Python 3 + Flask (Routes, Services, Validation, Cost Engine)
            │
   [ Persistence Layer ]   -->  SQLite with foreign keys & transaction boundaries
```

### Directory Structure
```
sepm2/
├── app.py                      # Flask Application Factory & Server entry point
├── config.py                   # App Configuration (Production, Development, Testing classes)
├── .env.example                # Sample environment configuration template
├── Dockerfile                  # Non-root production container specification
├── docker-compose.yml          # Container compose with persistent volume mount
├── requirements.txt            # Python dependencies (Flask, Pytest, requests, selenium)
├── .gitignore                  # Git ignore rules (.env, .db, pycache, backups)
├── .dockerignore               # Docker context exclusion rules
├── README.md                   # Complete architectural, installation, and usage manual
├── database/
│   ├── schema.sql              # DDL for Machine, WorkOrder, DowntimeLog tables
│   ├── connection.py           # DB connection management per request context
│   ├── init_db.py              # Schema initializer & 40-machine sample seeder
│   └── backup_db.py            # SQLite online backup & restore verification utility
├── services/
│   ├── machine_service.py      # Machine retrieval and status aggregations
│   ├── work_order_service.py   # Work order queries and existence validation
│   ├── downtime_service.py     # Transactional STOP/RESUME and reporting queries
│   ├── cost_service.py         # Rs. 50,000/hr duration & cost calculations
│   └── validation_service.py   # ISO timestamps, input rules, and payload verification
├── routes/
│   ├── dashboard_routes.py     # Executive KPI overview & active stoppage alerts
│   ├── machine_routes.py       # 40-machine roster & individual machine history
│   ├── downtime_routes.py      # Manual downtime logging, resume, and filters
│   ├── work_order_routes.py    # Work order roster
│   ├── report_routes.py        # Downtime Pareto analysis by machine and reason
│   └── simulator_routes.py     # JSON event API receiver and simulator web console
├── static/
│   ├── css/style.css           # Clean, responsive CSS styling
│   └── js/main.js              # Client-side UI utilities & confirmations
├── templates/
│   ├── base.html               # Shared navigation & layout shell
│   ├── dashboard.html          # Executive summary dashboard
│   ├── machines.html           # 40-unit machine table
│   ├── machine_details.html    # Single machine status & incident log
│   ├── downtime_form.html      # Manual stoppage entry form
│   ├── downtime_history.html   # Filterable audit trail of downtime events
│   ├── work_orders.html        # Production work order roster
│   ├── reports.html            # Downtime Pareto analysis and financial loss
│   └── simulator.html          # Interactive Simulator UI testbench
├── simulator/
│   └── machine_simulator.py    # Python CLI script for automated event simulation
├── monitoring/
│   ├── monitor_daemon.py       # Continuous availability heartbeat monitor
│   └── performance_test.py     # Local micro-benchmark test script
├── documentation/
│   ├── phase5/                 # Phase 5 Testing deliverables (Plans, Cases, Reports)
│   └── phase6/                 # Phase 6 Deployment deliverables (Plan, Checklist, Guides)
└── tests/
    ├── conftest.py             # Pytest fixtures & isolated temporary test DB
    ├── test_cost.py            # Cost calculation & midnight transition tests
    ├── test_downtime.py        # Transactional STOP/RESUME and duplicate checks
    ├── test_validation.py      # Input validation & malformed payload rejection
    ├── test_simulator_api.py   # API integration tests & idempotency tests
    ├── test_integration.py     # Blueprint, route, and rollback integration tests
    └── test_selenium.py        # Automated headless Chrome browser test suite
```

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.9+ (Python 3.11, 3.12, and 3.13 tested and verified)
- Google Chrome browser (for running optional Selenium UI tests)

### 2. Virtual Environment Setup (Recommended)
#### Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize / Reset the Database
Initializes the SQLite schema and seeds 40 shop-floor machines (`M-001` to `M-040`) and production work orders (`WO-1001` to `WO-1008`):
```bash
python database/init_db.py
```

### 5. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

To stop the application at any time, press `Ctrl + C` in the terminal.

---

## 💾 Database Backup & Recovery

A dedicated hot-backup and restore utility is provided in `database/backup_db.py`:

```powershell
# 1. Verify database integrity
python database/backup_db.py --action verify --db factory.db

# 2. Create a timestamped online backup
python database/backup_db.py --action backup --db factory.db --dest backups/

# 3. Restore from a backup (creates an automatic safety copy first)
python database/backup_db.py --action restore --src backups/factory_backup_YYYYMMDD_HHMMSS.db --db factory.db
```

---

## 🤖 Running the Machine Event Simulator

### Option A: Via Web UI Console
Navigate to the **Simulator** tab in the navigation bar (`http://127.0.0.1:5000/simulator`). You can transmit simulated `STOP` and `RESUME` JSON payloads to `/api/simulator/events` interactively and inspect the live JSON response.

### Option B: Via Python CLI Script
While the Flask server is running in one terminal, run the simulator script in another terminal:
```bash
python simulator/machine_simulator.py --machine M-001 --wo WO-1001 --duration 5
```

---

## 🧪 Running Automated Tests

Run the full automated test suite containing unit, integration, and API tests against an isolated temporary database:
```powershell
python -m pytest tests/test_cost.py tests/test_downtime.py tests/test_validation.py tests/test_simulator_api.py tests/test_integration.py -v
```

To run the automated Selenium browser tests (requires Google Chrome):
```powershell
python -m pytest tests/test_selenium.py -v
```

---

## 🐳 Docker Deployment (Academic Blueprint)

A production-grade, non-root container configuration with persistent volume mounting is provided.
*(Note: Docker execution status on host is marked NOT VERIFIED as Docker is not installed on the local environment).*

```powershell
# Build image
docker build -t factory-shopfloor-system .

# Run container with persistent data bind mount
docker run -p 5000:5000 -v ${PWD}/data:/app/data factory-shopfloor-system

# Or using Docker Compose
docker compose up -d
```
Access at `http://localhost:5000`.
