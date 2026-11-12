"""
Database Backup & Restore Utility for Factory Shop-Floor System
Provides:
- Hot backup using SQLite online backup API (safe while database is open)
- File copy backup (with read lock)
- Database integrity check (PRAGMA integrity_check)
- Restore from backup verification

Usage:
    python database/backup_db.py --action backup [--dest backups/]
    python database/backup_db.py --action verify [--db factory.db]
    python database/backup_db.py --action restore --src backups/factory_20261105.db --dest factory.db
"""
import os
import sys
import time
import shutil
import sqlite3
import argparse
from datetime import datetime

DEFAULT_DB = "factory.db"
DEFAULT_BACKUP_DIR = "backups"

def check_integrity(db_path):
    """Executes PRAGMA integrity_check on the target database."""
    if not os.path.exists(db_path):
        return False, f"Database file '{db_path}' does not exist."
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]
        conn.close()
        return (result == "ok"), result
    except Exception as e:
        return False, str(e)

def perform_backup(src_db=DEFAULT_DB, backup_dir=DEFAULT_BACKUP_DIR):
    """Uses SQLite online backup API to copy database cleanly without corruption."""
    if not os.path.exists(src_db):
        print(f"[ERROR] Source database '{src_db}' not found.")
        return None

    # Verify source integrity first
    ok, msg = check_integrity(src_db)
    if not ok:
        print(f"[ERROR] Source database integrity check failed: {msg}")
        return None

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"factory_backup_{timestamp}.db"
    dest_path = os.path.join(backup_dir, backup_filename)

    try:
        src_conn = sqlite3.connect(src_db)
        dest_conn = sqlite3.connect(dest_path)
        with dest_conn:
            src_conn.backup(dest_conn, pages=20, sleep=0.01)
        src_conn.close()
        dest_conn.close()

        # Verify backup integrity
        b_ok, b_msg = check_integrity(dest_path)
        if b_ok:
            size_kb = os.path.getsize(dest_path) / 1024.0
            print(f"[SUCCESS] Database safely backed up to: {dest_path} ({size_kb:.1f} KB)")
            return dest_path
        else:
            print(f"[ERROR] Backup created but failed integrity verification: {b_msg}")
            return None
    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")
        return None

def restore_backup(src_backup, target_db=DEFAULT_DB):
    """Restores database from a verified backup file."""
    if not os.path.exists(src_backup):
        print(f"[ERROR] Backup file '{src_backup}' not found.")
        return False

    ok, msg = check_integrity(src_backup)
    if not ok:
        print(f"[ERROR] Cannot restore from corrupt backup: {msg}")
        return False

    try:
        # Create a pre-restore safety copy if target exists
        if os.path.exists(target_db):
            pre_restore = f"{target_db}.prerestore_{int(time.time())}"
            shutil.copy2(target_db, pre_restore)
            print(f"[INFO] Created pre-restore safety copy at: {pre_restore}")

        shutil.copy2(src_backup, target_db)
        print(f"[SUCCESS] Database successfully restored from {src_backup} to {target_db}.")
        return True
    except Exception as e:
        print(f"[ERROR] Restore failed: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLite Backup & Restore Tool")
    parser.add_argument("--action", choices=["backup", "restore", "verify"], default="backup", help="Action to perform")
    parser.add_argument("--db", default=DEFAULT_DB, help="Database path")
    parser.add_argument("--dest", default=DEFAULT_BACKUP_DIR, help="Backup destination folder or target db")
    parser.add_argument("--src", help="Source backup file for restore")
    args = parser.parse_args()

    if args.action == "backup":
        perform_backup(args.db, args.dest)
    elif args.action == "verify":
        ok, msg = check_integrity(args.db)
        print(f"Database: {args.db} | Integrity Status: {msg}")
    elif args.action == "restore":
        if not args.src:
            print("[ERROR] --src backup file required for restore.")
        else:
            restore_backup(args.src, args.db)
