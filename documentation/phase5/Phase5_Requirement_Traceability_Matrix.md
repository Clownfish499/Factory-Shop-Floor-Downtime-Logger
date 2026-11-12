# Phase 5: Requirement Traceability Matrix (RTM)
## Case 47 – Factory Shop-Floor Execution System

This matrix traces every Phase 2 requirement (**FR-01 to FR-24** and non-functional requirements) directly to specific test cases and execution outcomes.

---

| Requirement ID | Requirement Description | Test Case ID | Test Implementation File | Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Store and register machine records | TC-01, TC-20 | `test_downtime.py`, `init_db.py` | Unit / Database Query | **PASS** |
| **FR-02** | Display the 40-unit machine list | TC-01, TC-26 | `test_selenium.py`, `test_integration.py` | Selenium UI / HTTP GET | **PASS** |
| **FR-03** | Display each machine's current status (text label) | TC-01, TC-03, TC-24 | `test_downtime.py`, `test_selenium.py` | Unit / UI DOM check | **PASS** |
| **FR-04** | Start a downtime event for a machine | TC-03, TC-28 | `test_downtime.py`, `test_integration.py` | Transactional Service / Route | **PASS** |
| **FR-05** | Record downtime start timestamp | TC-03, TC-15 | `test_downtime.py`, `test_simulator_api.py` | Database validation | **PASS** |
| **FR-06** | Record mandatory downtime reason | TC-03, TC-05 | `test_validation.py`, `test_downtime.py` | Input validator check | **PASS** |
| **FR-07** | Associate optional work order with downtime | TC-14 | `test_downtime.py`, `test_integration.py` | Foreign key validation | **PASS** |
| **FR-08** | Resume and close open downtime event | TC-07, TC-24, TC-28 | `test_downtime.py`, `test_integration.py` | Transactional service / UI | **PASS** |
| **FR-09** | Calculate elapsed downtime duration | TC-09, TC-10, TC-11, TC-12 | `test_cost.py` | Unit mathematical test | **PASS** |
| **FR-10** | Calculate estimated downtime cost (Rs. 50k/hr) | TC-09, TC-10, TC-11 | `test_cost.py`, `test_integration.py` | Unit & Integration test | **PASS** |
| **FR-11** | Display executive dashboard summaries | TC-21, TC-26 | `test_integration.py`, `test_selenium.py` | Integration & Browser test | **PASS** |
| **FR-12** | Filter and review downtime history | TC-22, TC-29 | `test_integration.py`, `test_selenium.py` | Query params & Browser test | **PASS** |
| **FR-13** | Validate machine identifiers and input | TC-04, TC-05, TC-36 | `test_validation.py`, `test_downtime.py` | Unit validator | **PASS** |
| **FR-14** | Prevent duplicate open downtime events | TC-06 | `test_downtime.py` | Negative test assertion | **PASS** |
| **FR-15** | Support simulated machine events | TC-15, TC-16 | `test_simulator_api.py`, `machine_simulator.py` | API client test | **PASS** |
| **FR-16** | Validate simulator payloads and reject invalid data | TC-17, TC-18, TC-19, TC-37 | `test_simulator_api.py`, `test_validation.py` | API schema validator | **PASS** |
| **FR-17** | Store and display work orders | TC-14 | `test_integration.py` | SQLite inspection | **PASS** |
| **FR-18** | Persist application data in SQLite database | TC-20 | `test_downtime.py` | Context teardown test | **PASS** |
| **FR-19** | Store relevant timestamps and source info | TC-03, TC-15 | `test_downtime.py`, `test_simulator_api.py` | Database inspection | **PASS** |
| **FR-20** | Receive simulator events through REST API | TC-15, TC-16 | `test_simulator_api.py` | HTTP POST test | **PASS** |
| **FR-21** | Process JSON simulator events | TC-15, TC-16 | `test_simulator_api.py` | JSON payload serialization | **PASS** |
| **FR-22** | Return clear success and error responses | TC-15, TC-17, TC-18 | `test_simulator_api.py` | HTTP 200/201/400 assertions | **PASS** |
| **FR-23** | Keep event/source info for audit traceability | TC-15, TC-20 | `test_simulator_api.py` | DB column verification | **PASS** |
| **FR-24** | Produce consistent downtime summaries & reports | TC-23, TC-30 | `test_integration.py`, `test_selenium.py` | Pareto query & DOM check | **PASS** |
| **NFR-01** | Usability: Clean desktop interface & feedback | TC-26, TC-28 | `test_selenium.py` | Headless Chrome verification | **PASS** |
| **NFR-02** | Performance: Responsive local prototype (<100ms) | TC-31, TC-32, TC-33, TC-34 | `monitoring/performance_test.py` | Micro-benchmarks | **PASS** |
| **NFR-03** | Reliability: Transaction rollback without corruption | TC-25, TC-35 | `test_integration.py` | Rollback test | **PASS** |
| **NFR-04** | Data Integrity: SQLite primary and foreign keys | TC-14, TC-25 | `test_integration.py` | Constraint checks | **PASS** |
| **NFR-05** | Maintainability: Layered architecture separation | All tests | Project source inspection | Architectural review | **PASS** |
| **NFR-06** | Testability: Isolated tests with temporary DB | TC-01 to TC-37 | `conftest.py`, `test_selenium.py` | Fixture isolation | **PASS** |
| **NFR-07** | Security: Parameterized SQL against injection | All services | `downtime_service.py` etc. | Code audit | **PASS** |
| **NFR-10** | Availability: Persistent SQLite across restarts | TC-20, TC-35 | `test_downtime.py`, `test_integration.py` | Reconnect & Health query | **PASS** |

---

### Verification Summary
- **Total Functional Requirements (FR-01 to FR-24)**: 24
- **Total Functional Requirements Verified**: 24 (100%)
- **Total Non-Functional Requirements Sampled**: 8 (100% Passed)
- **Deficiencies Identified**: 0 remaining.
