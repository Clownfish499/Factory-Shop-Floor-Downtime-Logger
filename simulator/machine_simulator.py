"""
Simulated Machine Event Generator
Demonstration script to emit simulated STOP and RESUME events to the Shop-Floor API.
Usage:
    python simulator/machine_simulator.py [--base-url http://127.0.0.1:5000] [--machine M-001]
"""
import sys
import time
import argparse
import random
import requests
from datetime import datetime

DEFAULT_URL = "http://127.0.0.1:5000/api/simulator/events"

SAMPLE_REASONS = [
    "Spindle motor overheating",
    "Hydraulic pressure drop",
    "Emergency stop button pressed",
    "Tool bit wear replacement",
    "Material feed blockage",
    "Coolant leak detected"
]

def emit_event(base_url, payload):
    print(f"\n[SIMULATOR] Sending {payload['event_type']} event for {payload['machine_id']}...")
    try:
        resp = requests.post(base_url, json=payload, headers={"Content-Type": "application/json"}, timeout=5)
        print(f"[SIMULATOR] Response Status Code: {resp.status_code}")
        print(f"[SIMULATOR] Response Body: {resp.text}")
        return resp
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to {base_url}. Ensure the Flask server is running.")
        return None

def run_simulation(base_url, machine_id="M-001", work_order_id="WO-1001", wait_seconds=3):
    print("=" * 65)
    print("  FACTORY SHOP-FLOOR MACHINE EVENT SIMULATOR (Case 47)")
    print("=" * 65)
    print(f"Target URL: {base_url}")
    print(f"Target Machine: {machine_id}")
    print(f"Work Order: {work_order_id}")
    print("-" * 65)

    # 1. STOP Event
    stop_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    reason = random.choice(SAMPLE_REASONS)
    stop_event_id = f"SIM-STOP-{int(time.time())}"

    stop_payload = {
        "machine_id": machine_id,
        "event_type": "STOP",
        "timestamp": stop_timestamp,
        "reason": reason,
        "work_order_id": work_order_id,
        "source": "SIMULATOR",
        "event_id": stop_event_id
    }

    stop_resp = emit_event(base_url, stop_payload)
    if not stop_resp or stop_resp.status_code not in (200, 201):
        print("[SIMULATOR] STOP event was not accepted. Aborting resume cycle.")
        return

    # Simulate machine being down for N seconds
    print(f"\n[SIMULATOR] Machine {machine_id} is now DOWN. Simulating downtime for {wait_seconds} seconds...")
    time.sleep(wait_seconds)

    # 2. RESUME Event
    resume_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    resume_event_id = f"SIM-RESUME-{int(time.time())}"

    resume_payload = {
        "machine_id": machine_id,
        "event_type": "RESUME",
        "timestamp": resume_timestamp,
        "source": "SIMULATOR",
        "event_id": resume_event_id
    }

    resume_resp = emit_event(base_url, resume_payload)
    if resume_resp and resume_resp.status_code == 200:
        print("\n[SIMULATOR] Cycle complete! Machine resumed and downtime cost computed.")
    else:
        print("\n[SIMULATOR] Cycle finished with errors.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Machine Event Simulator CLI")
    parser.add_argument("--url", default=DEFAULT_URL, help="Target API endpoint URL")
    parser.add_argument("--machine", default="M-001", help="Target machine ID (e.g., M-001)")
    parser.add_argument("--wo", default="WO-1001", help="Work Order ID (e.g., WO-1001)")
    parser.add_argument("--duration", type=int, default=3, help="Simulated wait seconds before resume")
    args = parser.parse_args()

    run_simulation(base_url=args.url, machine_id=args.machine, work_order_id=args.wo, wait_seconds=args.duration)
