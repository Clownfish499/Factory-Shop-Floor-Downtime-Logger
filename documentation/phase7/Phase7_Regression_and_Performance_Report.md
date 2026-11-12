# Phase 7: Regression and Performance Report
## Case 47 – Factory Shop-Floor Execution System

---

### 1. Current Regression Test Execution Results (Phase 7 Independent Run)

All automated regression test suites were re-executed independently on the Windows host workstation (Python 3.13.2) during Phase 7 maintenance verification.

#### Suite 1: PyTest Unit, Integration & Simulator API Tests
- **Command**:
  ```powershell
  python -m pytest tests/test_cost.py tests/test_downtime.py tests/test_validation.py tests/test_simulator_api.py tests/test_integration.py -v
  ```
- **Execution Breakdown**:
  - Unit Tests (`test_cost.py`, `test_downtime.py`, `test_validation.py`): **16 Passed**
  - Integration Tests (`test_integration.py`): **7 Passed**
  - Simulator API Tests (`test_simulator_api.py`): **4 Passed**
- **Outcome**: **27 Passed, 0 Failed, 0 Skipped in 2.60s** (**100% Pass Rate**).

#### Suite 2: Selenium Browser Automation Tests
- **Command**:
  ```powershell
  python -m pytest tests/test_selenium.py -v
  ```
- **Browser**: Headless Google Chrome + ChromeDriver
- **Scenarios Tested**:
  1. `test_selenium_dashboard_and_machine_count`: Verified title and 40 machines card. (**PASS**)
  2. `test_selenium_machine_list_and_details`: Navigated roster to machine `M-001` detail screen. (**PASS**)
  3. `test_selenium_downtime_start_and_resume_cycle`: Logged stoppage on `M-002`, confirmed alert, verified resume banner. (**PASS**)
  4. `test_selenium_downtime_history_filters`: Filtered history records by machine dropdown. (**PASS**)
  5. `test_selenium_reports_and_simulator_pages`: Verified Pareto reports and Simulator Console UI. (**PASS**)
- **Outcome**: **5 Passed, 0 Failed, 0 Skipped in 23.02s** (**100% Pass Rate**).

---

### 2. Current Performance Benchmark Results

Executed local stress and latency benchmark via [`monitoring/performance_test.py`](file:///c:/Users/HP/OneDrive/one%20drive1/OneDrive/Desktop/sepm2/monitoring/performance_test.py):
- **Command**:
  ```powershell
  python -m monitoring.performance_test
  ```

#### Benchmark Summary Table:
| Endpoint / Operation | Workload | Success Rate | Average Latency | Median Latency | Max Latency | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dashboard (`/`)** | 50 GET requests | 50 / 50 (100%) | **6.05 ms** | 4.92 ms | 54.06 ms | **PASS** |
| **Machine Roster (`/machines/`)** | 50 GET requests | 50 / 50 (100%) | **5.75 ms** | 5.38 ms | 13.56 ms | **PASS** |
| **Downtime History (`/downtime/history`)** | 50 GET requests | 50 / 50 (100%) | **4.55 ms** | 3.97 ms | 28.95 ms | **PASS** |
| **Batch Simulator Event Ingestion** | 40 transactional writes (20 cycles) | 40 / 40 (100%) | **18.90 ms** | 16.97 ms | 69.53 ms | **PASS** |

- **Error Rate**: 0.0% across all 190 total benchmark requests.
- **Reliability Finding**: Sequential transactional database operations completed with sub-20ms latency and zero locking contention.

---

### 3. Comparison with Historical Phase 5 & Phase 6 Results

| Verification Metric | Phase 5 Reported Result | Phase 6 Reported Result | Phase 7 Current Live Result | Trend / Consistency |
| :--- | :---: | :---: | :---: | :---: |
| **PyTest Functions Passed** | 27 | 27 | **27** | Stable (100%) |
| **Selenium Browser Tests Passed** | 5 | 5 | **5** | Stable (100%) |
| **Performance Checks Passed** | 4 | 4 | **4** | Stable (100%) |
| **Health Check Passed** | 1 | 1 | **1** | Stable (100%) |
| **Total Verification Checks** | **37 / 37** | **37 / 37** | **37 / 37** | **100% Consistent** |
| **Failed Checks** | 0 | 0 | **0** | Zero Regressions |
| **Skipped Checks** | 0 | 0 | **0** | Complete Execution |
| **Docker Status** | NOT VERIFIED | NOT VERIFIED | **NOT VERIFIED** | Unchanged (Host lacks Docker CLI) |

---

### 4. Environmental Limitations
1. **Docker Execution**: Docker engine is not installed on the local Windows host; container runtime checks remain transparently marked **NOT VERIFIED**.
2. **Local Machine Scope**: Performance latency benchmarks reflect a single-user local prototype workstation. They do not simulate multi-thousand user concurrent industrial traffic.
