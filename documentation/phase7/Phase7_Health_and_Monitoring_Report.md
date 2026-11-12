# Phase 7: Application Health and Monitoring Report
## Case 47 – Factory Shop-Floor Execution System

---

### 1. Health Endpoint Verification (`GET /health`)
The lightweight health check diagnostic endpoint was inspected, queried, and verified in accordance with Phase 7 requirements:
- **Endpoint URL**: `http://127.0.0.1:5000/health`
- **Method**: `GET`
- **Authentication**: None required (diagnostic probe)
- **Response Format**: `application/json`

#### Response Verification:
```json
{
  "database": "healthy",
  "service": "Factory Shop-Floor Execution System - Downtime Logger",
  "status": "UP"
}
```
- **HTTP Status Code**: `200 OK`
- **Security Check**: The response reveals no internal directory paths, database connection credentials, or cryptographic secrets.
- **Fault Simulation**: If SQLite is unreadable or missing, the query probe fails safely and returns HTTP `503 Service Unavailable` with `status: "DEGRADED"` and logs an error to the server console.

---

### 2. Monitoring Script Review (`monitoring/monitor_daemon.py`)
The standalone monitoring utility was reviewed and executed:
- **File Location**: [`monitoring/monitor_daemon.py`](file:///c:/Users/HP/OneDrive/one%20drive1/OneDrive/Desktop/sepm2/monitoring/monitor_daemon.py)
- **Parameters**:
  - `--url`: Configurable target server (default: `http://127.0.0.1:5000`)
  - `--interval`: Frequency of health checks in seconds (default: 5s)
  - `--iterations`: Number of probes before cleanly terminating (default: `None` for continuous execution)

#### Live Test Execution Results:
Executed a 3-iteration live health monitoring run against the active application:
```
2026-11-05 23:03:41,705 [INFO] Starting Shop-Floor Health Monitor targeting http://127.0.0.1:5066 (Interval: 1s)
2026-11-05 23:03:41,928 [INFO] [HEALTH CHECK #1] Status: UP | Latency: 221.4ms | DB: healthy
2026-11-05 23:03:42,934 [INFO] [HEALTH CHECK #2] Status: UP | Latency: 5.4ms | DB: healthy
2026-11-05 23:03:43,938 [INFO] [HEALTH CHECK #3] Status: UP | Latency: 3.2ms | DB: healthy
2026-11-05 23:03:43,939 [INFO] Summary: 3/3 successful checks (100.0% availability).
```
- **Total Probes**: 3
- **Successful Probes**: 3 (100.0% availability)
- **Average Post-Warmup Latency**: 4.3 ms
- **Log Destination**: Output simultaneously streamed to terminal and persisted in `app_monitor.log`.

---

### 3. Log Audit & Sanitization Verification
Inspected `app_monitor.log` and Flask application logs:
- **Timestamp Standard**: ISO 8601 timestamps (`YYYY-MM-DD HH:MM:SS,fff`) present on all lines.
- **Sensitive Data Check**: Confirmed that zero database passwords, session secret tokens, or employee personal details are emitted.
- **Process Termination**: The script listens for `KeyboardInterrupt` (`Ctrl+C`) and gracefully prints an availability summary upon exit.

---

### 4. Operational Instructions to Start and Stop Monitoring

#### To Run a 10-Check Pre-Demonstration Audit:
```powershell
python monitoring/monitor_daemon.py --url http://127.0.0.1:5000 --interval 2 --iterations 10
```

#### To Run Continuous Local Monitoring:
```powershell
python monitoring/monitor_daemon.py --url http://127.0.0.1:5000 --interval 5
```
*To stop monitoring, press `Ctrl + C`.*

---

### 5. Monitoring Limitations & Disclaimers
1. **Academic Scope**: This monitoring checks the **software prototype** and its SQLite database connectivity. It does **not** monitor physical factory machinery, electrical power grids, or hardware sensors.
2. **Local Execution**: Availability percentages reflect local test windows; no continuous 24/7 cloud uptime SLA is claimed.
