# Phase 5: Test Case Specifications
## Case 47 – Factory Shop-Floor Execution System

This document specifies the complete test cases (**TC-01 to TC-37**) covering unit, integration, validation, simulator, reliability, performance, and Selenium UI tests. All 37 test cases have been executed and passed.

---

| Test Case ID | Req ID | Test Scenario | Preconditions | Test Inputs | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | FR-02, FR-03 | Display all 40 machines on roster | DB seeded with 40 machines | `GET /machines/` | 40 machine rows rendered with text status labels | 40 machines listed with RUNNING/DOWN text status | **PASS** |
| **TC-02** | FR-02, FR-03 | View individual machine details | Machine `M-001` exists in DB | `GET /machines/M-001` | Displays machine ID, name, section description, status, and history table | Details page rendered with full machine data | **PASS** |
| **TC-03** | FR-04, FR-05, FR-06 | Start downtime for valid running machine | Machine `M-001` is RUNNING | `POST /downtime/start` (`M-001`, reason: "Motor overheat") | Creates OPEN log record; machine status changes to DOWN | Stoppage logged with ID #1; status set to DOWN | **PASS** |
| **TC-04** | FR-13 | Reject unknown machine ID on downtime start | Machine `M-999` does not exist | `POST /downtime/start` (`M-999`, reason: "Motor fail") | Raises `ValueError` ("does not exist"); rejects record | Rejected with exact error message | **PASS** |
| **TC-05** | FR-06, FR-13 | Reject blank or whitespace downtime reason | Machine `M-001` exists | `reason = ""` or `reason = "   "` | Rejection message ("reason is mandatory"); no record created | Validation rejected; error displayed | **PASS** |
| **TC-06** | FR-14, BR-03 | Reject second open downtime event for same machine | Machine `M-002` already has OPEN event | `POST /downtime/start` for `M-002` | Rejects with message ("already has an open downtime event") | Rejection message raised; DB untouched | **PASS** |
| **TC-07** | FR-08, FR-09, FR-10 | Resume open downtime event | Machine `M-003` has OPEN event | `POST /downtime/resume/M-003` | Status becomes RUNNING; duration & cost calculated; log set to CLOSED | Machine RUNNING; duration & cost populated | **PASS** |
| **TC-08** | FR-08, BR-04 | Reject resume without an open event | Machine `M-004` is RUNNING | `POST /downtime/resume/M-004` | Raises `ValueError` ("has no open downtime event") | Rejection raised; machine remains RUNNING | **PASS** |
| **TC-09** | FR-10, BR-11 | Calculate 30-minute downtime cost | Rate = Rs. 50,000/hr | `duration = 1800` seconds | `Cost = (1800 / 3600) * 50,000 = Rs. 25,000.00` | Rs. 25,000.00 | **PASS** |
| **TC-10** | FR-10, BR-11 | Calculate 1-hour downtime cost | Rate = Rs. 50,000/hr | `duration = 3600` seconds | `Cost = (3600 / 3600) * 50,000 = Rs. 50,000.00` | Rs. 50,000.00 | **PASS** |
| **TC-11** | FR-10, BR-11 | Calculate 90-minute downtime cost | Rate = Rs. 50,000/hr | `duration = 5400` seconds | `Cost = (5400 / 3600) * 50,000 = Rs. 75,000.00` | Rs. 75,000.00 | **PASS** |
| **TC-12** | FR-09, BR-11 | Calculate downtime duration crossing midnight | Valid timestamps | `start=23:45`, `end=00:15` (+1 day) | `duration = 1800s`; `cost = Rs. 25,000.00` | Exactly 1800s and Rs. 25,000.00 calculated | **PASS** |
| **TC-13** | FR-09, BR-05 | Reject end time earlier than start time | Valid timestamps | `start=10:00`, `end=09:30` | `ValueError` ("End timestamp cannot be earlier than start timestamp") | Rejection error raised | **PASS** |
| **TC-14** | FR-07, BR-10 | Reject invalid or non-existent work-order ID | Non-existent WO | `work_order_id = "WO-INVALID-999"` | Rejection error ("Work order does not exist") | Rejection error raised | **PASS** |
| **TC-15** | FR-15, FR-20, FR-21 | Receive simulator STOP event via JSON API | Valid JSON payload | `POST /api/simulator/events` with STOP | `201 Created`; status DOWN; event OPEN | `201 Created` with JSON confirmation | **PASS** |
| **TC-16** | FR-15, FR-20, FR-21 | Receive simulator RESUME event via JSON API | Active OPEN event exists | `POST /api/simulator/events` with RESUME | `200 OK`; status RUNNING; duration & cost returned | `200 OK` with JSON confirmation | **PASS** |
| **TC-17** | FR-16, FR-22 | Reject malformed JSON or invalid Content-Type | Invalid headers | `POST /api/simulator/events` as `text/plain` | `400 Bad Request` ("Expected application/json") | `400 Bad Request` | **PASS** |
| **TC-18** | FR-16, FR-22 | Reject missing mandatory simulator fields | Missing `event_type` | `{"machine_id": "M-001"}` | `400 Bad Request` specifying missing attribute | `400 Bad Request` with field name | **PASS** |
| **TC-19** | FR-16, BR-12 | Reject duplicate simulator event (Idempotency key) | Duplicate `event_id` | `event_id = "IDEMPOTENT-EVT-001"` | `400 Bad Request` ("already been processed") | `400 Bad Request` returned | **PASS** |
| **TC-20** | FR-18 | Verify data persistence across context restart | Data inserted in DB | Separate Flask context / query | Record persists intact in SQLite database | Open event persisted accurately | **PASS** |
| **TC-21** | FR-11 | Verify dashboard KPI metrics aggregation | Running & Down machines | `GET /` | Cards display total, running, down, and estimated cost | Metric cards show consistent values | **PASS** |
| **TC-22** | FR-12 | Verify downtime history filters | Multiple downtime logs | `GET /downtime/history?machine_id=M-002&status=CLOSED` | Returns only matching records | Table filtered accurately | **PASS** |
| **TC-23** | FR-24 | Verify Pareto report calculations | Multiple closed events | `GET /reports/` | Summaries grouped by machine and root cause | Pareto breakdown computed accurately | **PASS** |
| **TC-24** | FR-03, FR-08 | Verify machine status consistency | Sequence of STOP and RESUME | STOP then RESUME | Machine transitions from RUNNING -> DOWN -> RUNNING | State transitions verify 100% | **PASS** |
| **TC-25** | NFR-03, NFR-04 | Transactional rollback on database failure | Invalid foreign key during stop | Work order `WO-FAIL-ROLLBACK` | Transaction rolls back; machine remains RUNNING | Rolled back; no partial updates | **PASS** |
| **TC-26** | NFR-01, US-01 | Selenium: Dashboard load & machine count check | Live server active | Driver navigates to `http://127.0.0.1:5088/` | Verifies title and metric card displaying "40" | Assertions passed | **PASS** |
| **TC-27** | NFR-01, US-07 | Selenium: Machine roster navigation to details | Live server active | Click `M-001` link | Verifies navigation to `/machines/M-001` and header | Machine detail page verified | **PASS** |
| **TC-28** | NFR-01, US-02, US-03 | Selenium: Complete downtime start & resume cycle | Live server active | Fill form, submit, click resume alert | Flash banner displayed; machine resumes | Full cycle executed and passed | **PASS** |
| **TC-29** | NFR-01, US-04 | Selenium: History page filter interaction | Live server active | Select `M-002` dropdown, click filter | History table filtered for `M-002` | Filter applied successfully | **PASS** |
| **TC-30** | NFR-01, US-10 | Selenium: Reports & Simulator UI rendering | Live server active | Navigate to `/reports/` and `/simulator` | Verify Pareto card and Simulator response box | Both pages verified | **PASS** |
| **TC-31** | NFR-02 | Performance: Dashboard response time benchmark | Local Flask client | 50 sequential requests to `/` | Average latency < 50ms | 4.88ms avg; 50/50 success | **PASS** |
| **TC-32** | NFR-02 | Performance: Machine list response time benchmark | Local Flask client | 50 sequential requests to `/machines/` | Average latency < 50ms | 4.38ms avg; 50/50 success | **PASS** |
| **TC-33** | NFR-02 | Performance: History response time benchmark | Local Flask client | 50 sequential requests to `/downtime/history` | Average latency < 50ms | 2.86ms avg; 50/50 success | **PASS** |
| **TC-34** | NFR-02 | Performance: Batch simulator event ingestion | Local Flask client | 40 sequential simulator events (20 cycles) | Average latency < 50ms | 20.37ms avg; 40/40 success | **PASS** |
| **TC-35** | NFR-03, NFR-10 | Continuous monitoring: Health endpoint check | Running Flask app | `GET /health` | Returns `200 OK` with JSON `{"status": "UP", "database": "healthy"}` | `200 OK` verified | **PASS** |
| **TC-36** | FR-13 | Validation: Reject whitespace-only machine ID | Input string | `machine_id = ""` | Validation error returned | Rejected with error | **PASS** |
| **TC-37** | FR-16 | Validation: Reject unparseable ISO timestamp | Simulator payload | `timestamp = "not-a-valid-timestamp"` | Validation error returned | Rejected with error | **PASS** |
