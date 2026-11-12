# Phase 6: Database Backup and Recovery Guide
## Case 47 – Factory Shop-Floor Execution System

---

### 1. Database Architecture & Location
- **Database Engine**: SQLite 3
- **Default Database File**: `factory.db` in the project root directory (configurable via `DATABASE_PATH`).
- **Foreign Keys**: Enforced via `PRAGMA foreign_keys = ON;`.
- **Concurrency Mode**: WAL (Write-Ahead Logging) or standard rollback journal depending on OS filesystem support.

---

### 2. Built-in Backup & Restore Tool
A dedicated utility script is provided in [`database/backup_db.py`](file:///c:/Users/HP/OneDrive/one%20drive1/OneDrive/Desktop/sepm2/database/backup_db.py). It uses SQLite's official **Online Backup API** (`sqlite3.Connection.backup()`), which ensures consistent, non-corrupted snapshots even while the web application is actively receiving requests.

---

### 3. Backup Procedure

#### Step 1: Verify Integrity of Running Database
Before backing up, verify that the database has no structural corruption:
```bash
python database/backup_db.py --action verify --db factory.db
```
*Expected Output: `Database: factory.db | Integrity Status: ok`*

#### Step 2: Execute Online Backup
```bash
python database/backup_db.py --action backup --db factory.db --dest backups/
```
*Output: `[SUCCESS] Database safely backed up to: backups/factory_backup_YYYYMMDD_HHMMSS.db (44.0 KB)`*

The script automatically:
1. Opens a read lock.
2. Streams page blocks incrementally using the SQLite backup API.
3. Automatically verifies `PRAGMA integrity_check` on the newly created backup file.
4. Generates a timestamped `.db` file in the `backups/` directory.

---

### 4. Restore Procedure

If data is accidentally lost or an evaluator wants to reset to a known point:

#### Step 1: Stop the Application
Terminate the running Flask process (`Ctrl+C`).

#### Step 2: Execute Restore Command
```bash
python database/backup_db.py --action restore --src backups/factory_backup_20261105_224934.db --db factory.db
```
The restore utility:
1. Verifies that the source backup passes an integrity check before touching the target.
2. Creates an automated safety copy of the current target (`factory.db.prerestore_<timestamp>`).
3. Replaces `factory.db` with the verified backup snapshot.

#### Step 3: Verify & Restart Application
```bash
python database/backup_db.py --action verify --db factory.db
python app.py
```

---

### 5. SQLite Persistence Guarantees & Industrial Limitations

#### What SQLite Guarantees in this Prototype:
- **ACID Compliance**: Transactions either fully commit or fully roll back (`try ... db.commit() except ... db.rollback()`).
- **Restart Persistence**: All machine statuses, work order assignments, and downtime logs remain intact across application reboots.
- **Portability**: The entire database is a self-contained binary file, requiring zero external database server setup for the evaluator.

#### Limitations of SQLite for Large-Scale Production (Academic Discussion):
1. **Concurrency Bottlenecks**: SQLite uses file-level locking during writes. In a real industrial plant with hundreds of high-frequency automated telemetry sensors submitting data simultaneously, write contention would occur.
2. **Network Storage Latency**: SQLite is not optimized for network-mounted filesystems (NFS/SMB) where file-locking anomalies can risk corruption.
3. **Enterprise Recommendation**: For a full industrial deployment (Phase 7+), SQLite should be replaced with **PostgreSQL** or a dedicated time-series engine such as **TimescaleDB**.
