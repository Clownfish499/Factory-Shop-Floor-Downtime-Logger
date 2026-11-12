# Phase 7: Downtime and Preventive Maintenance Analysis
## Case 47 – Factory Shop-Floor Execution System

---

### 1. Shop-Floor Machine Status Overview
The factory shop-floor system manages **40 simulated workstations** (`M-001` through `M-040`) across 4 production sections:
- **Section 1**: CNC Machining Stations (`M-001` to `M-010`)
- **Section 2**: Stamping Presses (`M-011` to `M-020`)
- **Section 3**: Robotic Welders (`M-021` to `M-030`)
- **Section 4**: Assembly Cells (`M-031` to `M-040`)

Current baseline query (`services/machine_service.py`):
- **Total Workstations**: 40
- **Running Workstations**: 40 (All operating normally in clean demo state)
- **Down Workstations**: 0
- **Active Open Stoppages**: 0

---

### 2. Downtime & Cost Calculation Model
All downtime cost calculations follow **Case 47 Business Rule BR-11**:
- **Rate**: **Rs. 50,000 per hour**
- **Calculation Engine**: [`services/cost_service.py`](file:///c:/Users/HP/OneDrive/one%20drive1/OneDrive/Desktop/sepm2/services/cost_service.py)
  $$\text{Estimated Cost (Rs.)} = \left(\frac{\text{duration\_seconds}}{3600.0}\right) \times 50000.0$$
- **Verification Examples**:
  - 30 minutes (1800s) $\rightarrow$ Rs. 25,000.00
  - 1 hour (3600s) $\rightarrow$ Rs. 50,000.00
  - 90 minutes (5400s) $\rightarrow$ Rs. 75,000.00
- **Disclaimer**: All financial figures are explicitly labeled across dashboard and report screens as **estimates** based on Case 47 case-study parameters.

---

### 3. Repeated Stoppage Analysis (Pareto Breakdown)
The system aggregates historical downtime data using the Reports engine (`routes/report_routes.py` and `services/downtime_service.py`):
1. **Breakdown by Machine**: Aggregates incident counts, total elapsed duration, and cumulative financial loss per workstation.
2. **Breakdown by Root Cause Reason**: Groups stoppages by failure type (e.g., *Spindle motor overheating*, *Hydraulic pressure drop*, *Tool bit wear replacement*).
3. **Filtering**: Allows plant managers to filter records across custom date ranges.

---

### 4. Preventive Maintenance Support & Indicators

#### 4.1 Feature Status: RULE-BASED INDICATORS IMPLEMENTED IN REPORTS
Rather than introducing risky automated machine control or claiming unvalidated AI models, the application implements **transparent, rule-based preventive maintenance indicators**:
- **Indicator Condition**: When a machine accumulates $\ge 3$ closed downtime incidents within a 30-day reporting window, or exceeds 2.0 cumulative hours of downtime (Rs. 100,000 financial impact).
- **Advisory Output**: Flagged on machine detail views as:
  > **"⚠️ Recommended Action: Schedule Preventive Maintenance Review"**
  > *Reason: 3 or more historical stoppage events recorded. Inspect mechanical bearings, hydraulic lines, and lubrication levels.*
- **Data Sufficiency Check**: If a machine has fewer than 2 logged stoppages, the system displays:
  > *"Normal Operating Pattern: Insufficient historical stoppage frequency to warrant early maintenance intervention."*

#### 4.2 Rules of Engagement:
1. **Zero Automated Machine Actuation**: The system **never** automatically trips, shuts down, or throttles physical equipment.
2. **No Automatic Work Order Generation**: Maintenance advisories are presented as informational recommendations requiring human supervisor confirmation before dispatching maintenance staff.
3. **Illustrative Thresholds**: Thresholds are configurable operational heuristics, not mandatory industrial standards.

---

### 5. Ethical Considerations & Human Oversight
- **Non-Attribution to Workers**: High downtime counts on a machine indicate equipment wear, lubrication breakdown, or tooling age. They must **never** be used to assess operator incompetence or penalize shift workers.
- **Human Authority**: The maintenance engineer and shop-floor supervisor retain complete discretion over scheduling mechanical maintenance.
- **AI Disclaimer**: The prototype employs deterministic relational SQL aggregations and heuristic business rules; **no machine learning or predictive artificial intelligence is claimed or utilized**.
