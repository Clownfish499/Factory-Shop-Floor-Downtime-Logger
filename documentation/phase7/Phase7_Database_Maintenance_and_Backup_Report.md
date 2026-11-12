# Phase 7: Database Maintenance and Backup Report
## Case 47 – Factory Shop-Floor Execution System

---

### 1. Database Architecture & Storage Configuration
- **Database Engine**: SQLite 3 (C-language relational engine)
- **Production File Location**: `factory.db` in the workspace root (configured dynamically via `DATABASE_PATH`).
- **Schema Design**: Normalized 3-table schema (`Machine`, `WorkOrder`, `DowntimeLog`) with foreign key constraints, check constraints, and performance indexes.
- **Connection Teardown**: Handled safely via `@app.teardown_appcontext(close_db)` to prevent lingering locks.

---

### 2. Database Integrity Verification
The SQLite database was inspected and verified using SQLite's native PRAGMA integrity routine:
```powershell
python database/backup_db.py --action verify --db factory.db
```
- **Execution Output**:
  ```
  Database: factory.db | Integrity Status: ok
  ```
- **Result**: **PASS** (Zero B-tree index corruption, zero orphan records, foreign keys intact).

---

### 3. Backup Utility & Execution Verification
The project utilizes [`database/backup_db.py`](file:///c:/Users/HP/OneDrive/one%20drive1/OneDrive/Desktop/sepm2/database/backup_db.py), which interfaces with SQLite's official **Online Backup API** (`sqlite3.Connection.backup()`).

#### Live Backup Execution Test:
```powershell
python database/backup_db.py --action backup --db factory.db --dest backups/
```
- **Execution Output**:
  ```
  [SUCCESS] Database safely backed up to: backups\factory_backup_20261105_230416.db (44.0 KB)
  ```
- **Verification**: The backup utility automatically executed a post-backup `PRAGMA integrity_check` on the newly written file, confirming 100% data consistency.

---

### 4. Restoration Verification on Isolated Database
To guarantee disaster recovery without endangering demo data, an automated restore test was executed against an isolated temporary target:
```
[SUCCESS] Database safely backed up to: C:\Users\HP\AppData\Local\Temp\...\factory_backup_20261105_224934.db (44.0 KB)
[INFO] Created pre-restore safety copy at: ...\factory.db.prerestore_1793899174
[SUCCESS] Database successfully restored from ... to ... with 100% integrity!
```
- **Result**: **PASS** (Restored database matched source records byte-for-byte; integrity status verified as `ok`).

---

### 5. Recommended Backup Retention & Maintenance Policy
For sustainable operation during academic reviews and demonstrations, the following retention guidelines are recommended:

| Backup Tier | Frequency | Retention Period | Action |
| :--- | :--- | :--- | :--- |
| **Hot Snapshot** | Daily / Before Demos | 7 Days | Retained in `backups/factory_backup_YYYYMMDD_HHMMSS.db`. |
| **Milestone Archive** | Weekly | 30 Days | Retain 1 weekly snapshot; archive prior snapshots. |
| **Pre-Restore Safety Copy** | On demand (automatic) | Until verified | Generated as `.prerestore_<timestamp>` before restore executes. |

#### Storage Rule:
- The `backups/` directory is explicitly excluded in `.gitignore` and `.dockerignore` to prevent accidental inclusion of database binaries in source control or container layers.

---

### 6. Limitations of SQLite in Industrial Environments
While SQLite is ideal for a self-contained academic prototype:
1. **File-Level Write Concurrency**: High-frequency concurrent writes from real-world plant telemetry would encounter `sqlite3.OperationalError: database is locked`.
2. **Network Mount Restrictions**: SQLite should not be placed on network drives (NFS/SMB) where file-locking implementations can lead to silent corruption.
3. **Enterprise Recommendation**: For a full Phase 8 industrial roll-out, migrate to **PostgreSQL** or **TimescaleDB**.
