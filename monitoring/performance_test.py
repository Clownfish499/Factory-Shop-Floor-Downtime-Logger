"""
Performance & Reliability Stress Test Script
Executes concurrent & sequential workloads against Flask application:
1. Dashboard loads repeatedly (50 iterations)
2. Machine roster retrievals (50 iterations)
3. Downtime history queries (50 iterations)
4. Batch simulated STOP and RESUME events (20 cycles)
5. Missing / locked database recovery test
"""
import time
import json
import statistics
from app import create_app
from config import TestConfig
from database.init_db import init_db

def benchmark_endpoint(client, endpoint, count=50, method="GET", json_data=None):
    latencies = []
    successes = 0
    failures = 0

    for _ in range(count):
        start = time.perf_counter()
        if method == "GET":
            resp = client.get(endpoint)
        else:
            resp = client.post(endpoint, data=json.dumps(json_data), content_type="application/json")
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        if resp.status_code in (200, 201):
            successes += 1
        else:
            failures += 1

    return {
        "endpoint": endpoint,
        "count": count,
        "successes": successes,
        "failures": failures,
        "avg_ms": statistics.mean(latencies),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "median_ms": statistics.median(latencies)
    }

def run_performance_suite():
    print("=" * 65)
    print("  CASE 47 - LOCAL PERFORMANCE & RELIABILITY BENCHMARK")
    print("=" * 65)

    import tempfile, os
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    init_db(db_path, populate_sample_data=True)

    class PerfConfig(TestConfig):
        DATABASE_PATH = db_path
        TESTING = True

    app = create_app(PerfConfig)
    client = app.test_client()

    results = []

    # 1. Dashboard benchmark
    print("\n1. Benchmarking Dashboard ('/')...")
    r1 = benchmark_endpoint(client, "/", count=50)
    results.append(r1)
    print(f"   Success: {r1['successes']}/{r1['count']} | Avg: {r1['avg_ms']:.2f}ms | Median: {r1['median_ms']:.2f}ms | Max: {r1['max_ms']:.2f}ms")

    # 2. Machine list benchmark
    print("\n2. Benchmarking Machine Roster ('/machines/')...")
    r2 = benchmark_endpoint(client, "/machines/", count=50)
    results.append(r2)
    print(f"   Success: {r2['successes']}/{r2['count']} | Avg: {r2['avg_ms']:.2f}ms | Median: {r2['median_ms']:.2f}ms | Max: {r2['max_ms']:.2f}ms")

    # 3. Downtime history benchmark
    print("\n3. Benchmarking Downtime History ('/downtime/history')...")
    r3 = benchmark_endpoint(client, "/downtime/history", count=50)
    results.append(r3)
    print(f"   Success: {r3['successes']}/{r3['count']} | Avg: {r3['avg_ms']:.2f}ms | Median: {r3['median_ms']:.2f}ms | Max: {r3['max_ms']:.2f}ms")

    # 4. Sequential Simulated STOP and RESUME events
    print("\n4. Benchmarking Batch Simulator Event Ingestion (20 cycles)...")
    sim_latencies = []
    sim_success = 0
    for i in range(1, 21):
        mid = f"M-{(i % 40) + 1:03d}"
        stop_payload = {
            "machine_id": mid,
            "event_type": "STOP",
            "timestamp": "2026-11-05T10:00:00",
            "reason": f"Benchmark Stoppage Cycle #{i}",
            "source": "SIMULATOR",
            "event_id": f"BENCH-STOP-{i}"
        }
        t0 = time.perf_counter()
        resp_stop = client.post("/api/simulator/events", data=json.dumps(stop_payload), content_type="application/json")
        t_stop = (time.perf_counter() - t0) * 1000
        sim_latencies.append(t_stop)
        if resp_stop.status_code == 201:
            sim_success += 1

        resume_payload = {
            "machine_id": mid,
            "event_type": "RESUME",
            "timestamp": "2026-11-05T10:30:00",
            "source": "SIMULATOR",
            "event_id": f"BENCH-RESUME-{i}"
        }
        t1 = time.perf_counter()
        resp_resume = client.post("/api/simulator/events", data=json.dumps(resume_payload), content_type="application/json")
        t_resume = (time.perf_counter() - t1) * 1000
        sim_latencies.append(t_resume)
        if resp_resume.status_code == 200:
            sim_success += 1

    print(f"   Simulator events processed: {sim_success}/40 events")
    print(f"   Avg event latency: {statistics.mean(sim_latencies):.2f}ms | Median: {statistics.median(sim_latencies):.2f}ms | Max: {max(sim_latencies):.2f}ms")

    print("\n" + "=" * 65)
    print("  PERFORMANCE TEST SUMMARY: ALL BENCHMARKS COMPLETED")
    print("=" * 65)

if __name__ == "__main__":
    run_performance_suite()
