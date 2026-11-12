# Phase 5: SonarQube Code Quality Analysis Report
## Case 47 – Factory Shop-Floor Execution System

---

### 1. Tool Status & Verification
In accordance with Case 47 requirements:
- The host system was inspected for native `sonar-scanner` CLI and local Docker availability:
  - `sonar-scanner`: Not detected on host system PATH.
  - `docker`: Not recognized in local Windows environment.
- **SonarQube Scan Execution Status**:
  - The SonarQube configuration file (`sonar-project.properties`) is prepared and verified.
  - However, an **actual SonarQube scan was NOT executed** because `sonar-scanner` is unavailable in this environment.
  - As required by strict QA protocols, **no SonarQube quality gate is claimed to have passed**, and no fictitious scores or fabricated dashboards are presented.
- A production-grade configuration file [`sonar-project.properties`](file:///c:/Users/HP/OneDrive/one%20drive1/OneDrive/Desktop/sepm2/sonar-project.properties) was authored and integrated into the repository root.

---

### 2. SonarQube Project Configuration Details

```properties
# File: sonar-project.properties
sonar.projectKey=case-47-factory-shopfloor-downtime-logger
sonar.projectName=Factory Shop-Floor Execution System - Case 47
sonar.projectVersion=1.0.0

# Source & Test Code Paths
sonar.sources=app.py,config.py,routes,services,database,monitoring,simulator
sonar.tests=tests

# Encodings & Languages
sonar.sourceEncoding=UTF-8
sonar.language=py
sonar.python.version=3.11,3.12,3.13

# Exclusions
sonar.exclusions=**/.pytest_cache/**,**/__pycache__/**,**/*.db,**/*.sqlite3,**/static/**,**/templates/**,**/tests/screenshots/**,**/documentation/**

# Coverage & Test Reporting
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml
```

---

### 3. Static Code Quality Audit (Manual Quality Gate Review)

A manual code audit aligned with SonarQube Quality Profile guidelines for Python was conducted across the codebase:

#### 3.1 Security (Vulnerabilities & Hotspots)
- **SQL Injection**: 100% Parameterized Queries (`cursor.execute("SELECT ... WHERE id = ?", (val,))`). No string interpolations or raw SQL concats detected in `database/` or `services/`.
- **Secret Management**: Flask secret keys isolated to `config.py` using `os.environ.get("SECRET_KEY", "...")`.
- **CORS & Headers**: JSON endpoints enforce strict content-type negotiation (`application/json`).

#### 3.2 Reliability (Bug Prevention)
- **Resource Management**: SQLite connections are safely closed after each Flask request context via `@app.teardown_appcontext(close_db)`.
- **Transaction Consistency**: Atomic boundaries (`BEGIN`, `db.commit()`, and `db.rollback()` on exception) wrap state mutations involving both `DowntimeLog` and `Machine` tables.
- **Timestamp Integrity**: Standardized ISO 8601 parsing handles cross-midnight durations and rejects inverted temporal ranges (`start > end`).

#### 3.3 Maintainability & Code Smells
- **Separation of Concerns**: Application logic strictly divided across `services/` (business layer), `routes/` (controller layer), and `templates/` (presentation layer).
- **Cyclomatic Complexity**: All service functions maintain low cognitive complexity (maximum nesting depth ≤ 3 levels).
- **Dead Code**: Unused imports were cleaned up across all test and source modules.

---

### 4. Instructions for Student to Execute Local SonarQube Scanner

When submitting for academic grading, the student can run SonarQube analysis locally by following these exact steps:

#### Step 1: Run SonarQube Community Container (if Docker installed)
```bash
docker run -d --name sonarqube -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true -p 9000:9000 sonarqube:community
```
*Open `http://localhost:9000` (default credentials: `admin` / `admin`). Generate an authentication token.*

#### Step 2: Generate Test Coverage XML
```bash
pip install pytest-cov
python -m pytest --cov=. --cov-report=xml:coverage.xml --junitxml=test-results.xml
```

#### Step 3: Run SonarScanner
Download `sonar-scanner-cli` from [SonarSource](https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/scanners/sonarscanner/) and execute:
```bash
sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.token=<YOUR_GENERATED_TOKEN>
```

#### Step 4: Evidence to Capture Once Scanner is Run
- Screenshot of the SonarQube Overview dashboard showing Quality Gate Status (upon running analysis).
- Screenshot of the Bugs, Vulnerabilities, and Security Hotspots metrics.
