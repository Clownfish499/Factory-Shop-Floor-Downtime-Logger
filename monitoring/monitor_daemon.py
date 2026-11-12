"""
Lightweight Continuous Monitoring Daemon for Factory Shop-Floor System
Checks:
- Periodic heartbeat on /health endpoint.
- Availability tracking (uptime percentage).
- Logs health status with timestamps to app_monitor.log.
Usage:
    python monitoring/monitor_daemon.py [--url http://127.0.0.1:5000] [--interval 5] [--iterations 5]
"""
import sys
import time
import argparse
import json
import logging
from datetime import datetime
import urllib.request
import urllib.error

LOG_FILE = "app_monitor.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def check_health(base_url):
    health_url = f"{base_url.rstrip('/')}/health"
    start_t = time.time()
    try:
        req = urllib.request.Request(health_url, headers={"User-Agent": "ShopFloor-Monitor/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            elapsed_ms = (time.time() - start_t) * 1000
            data = json.loads(resp.read().decode("utf-8"))
            status = resp.status
            return True, status, elapsed_ms, data
    except urllib.error.HTTPError as he:
        elapsed_ms = (time.time() - start_t) * 1000
        return False, he.code, elapsed_ms, f"HTTP Error: {he.reason}"
    except Exception as e:
        elapsed_ms = (time.time() - start_t) * 1000
        return False, 0, elapsed_ms, str(e)

def run_monitor(base_url="http://127.0.0.1:5000", interval=5, iterations=None):
    logging.info(f"Starting Shop-Floor Health Monitor targeting {base_url} (Interval: {interval}s)")
    total = 0
    success = 0

    try:
        while True:
            total += 1
            ok, code, ms, details = check_health(base_url)
            if ok and code == 200:
                success += 1
                logging.info(f"[HEALTH CHECK #{total}] Status: UP | Latency: {ms:.1f}ms | DB: {details.get('database')}")
            else:
                logging.warning(f"[HEALTH CHECK #{total}] Status: DOWN/DEGRADED (HTTP {code}) | Latency: {ms:.1f}ms | Details: {details}")

            if iterations and total >= iterations:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Monitoring terminated by user.")

    uptime_pct = (success / total * 100) if total > 0 else 0
    logging.info(f"Summary: {success}/{total} successful checks ({uptime_pct:.1f}% availability).")
    return uptime_pct

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shop-Floor System Monitor Daemon")
    parser.add_argument("--url", default="http://127.0.0.1:5000", help="Base URL of application")
    parser.add_argument("--interval", type=int, default=5, help="Seconds between health probes")
    parser.add_argument("--iterations", type=int, default=None, help="Max iterations (None for continuous)")
    args = parser.parse_args()

    run_monitor(base_url=args.url, interval=args.interval, iterations=args.iterations)
