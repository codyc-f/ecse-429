"""
Part C — Performance Testing Suite
===================================
Measures the time required to CREATE, UPDATE, and DELETE objects
(todos, projects, categories) via the REST API as the number of
pre-existing objects in the system grows.

CPU percent and available free memory are sampled throughout every
experiment using psutil so we can correlate system resource usage
with object-count growth.

Usage
-----
    python performance_test.py              # run all experiments
    python performance_test.py --object todo
    python performance_test.py --object project
    python performance_test.py --object category
    python performance_test.py --sizes 10 50 100 200 500
    python performance_test.py --no-charts   # skip chart generation

Outputs
-------
    results/                    directory created automatically
      raw_results.csv           every individual timing measurement
      aggregated_results.csv    mean/median/p95 per (object, operation, size)
      charts/                   PNG charts (one per object × operation)
"""

import argparse
import csv
import json
import os
import random
import string
import threading
import time
from datetime import datetime
from pathlib import Path

import psutil
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = "http://localhost:4567"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

# Object-count checkpoints for the experiment
DEFAULT_SIZES = [1, 10, 50, 100, 200, 500, 1000]

RESULTS_DIR = Path(__file__).parent / "results"
CHARTS_DIR = RESULTS_DIR / "charts"

# ---------------------------------------------------------------------------
# Random data generators
# ---------------------------------------------------------------------------

def _rand_str(n: int = 12) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def random_todo_body() -> dict:
    return {
        "title": f"Todo-{_rand_str()}",
        "doneStatus": random.choice([True, False]),
        "description": f"Auto-generated todo description {_rand_str(20)}",
    }


def random_project_body() -> dict:
    return {
        "title": f"Project-{_rand_str()}",
        "completed": random.choice([True, False]),
        "active": random.choice([True, False]),
        "description": f"Auto-generated project description {_rand_str(20)}",
    }


def random_category_body() -> dict:
    return {
        "title": f"Category-{_rand_str()}",
        "description": f"Auto-generated category description {_rand_str(20)}",
    }


GENERATORS = {
    "todo": random_todo_body,
    "project": random_project_body,
    "category": random_category_body,
}

ENDPOINTS = {
    "todo": "todos",
    "project": "projects",
    "category": "categories",
}

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def create_object(obj_type: str) -> dict | None:
    """POST a new object; return the parsed response body or None on error."""
    url = f"{BASE_URL}/{ENDPOINTS[obj_type]}"
    body = GENERATORS[obj_type]()
    r = requests.post(url, json=body, headers=HEADERS, timeout=10)
    if r.status_code == 201:
        return r.json()
    return None


def update_object(obj_type: str, obj_id: str) -> bool:
    """POST (amend) an existing object; return True on success."""
    url = f"{BASE_URL}/{ENDPOINTS[obj_type]}/{obj_id}"
    body = GENERATORS[obj_type]()
    r = requests.post(url, json=body, headers=HEADERS, timeout=10)
    return r.status_code == 200


def delete_object(obj_type: str, obj_id: str) -> bool:
    """DELETE an existing object; return True on success."""
    url = f"{BASE_URL}/{ENDPOINTS[obj_type]}/{obj_id}"
    r = requests.delete(url, headers=HEADERS, timeout=10)
    return r.status_code == 200


def get_all_ids(obj_type: str) -> list[str]:
    """Return all IDs currently in the system for obj_type."""
    url = f"{BASE_URL}/{ENDPOINTS[obj_type]}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return []
    items = r.json().get(ENDPOINTS[obj_type], [])
    return [item["id"] for item in items]


def delete_all(obj_type: str) -> None:
    """Remove every object of obj_type (best-effort cleanup)."""
    for oid in get_all_ids(obj_type):
        delete_object(obj_type, oid)


# ---------------------------------------------------------------------------
# Resource monitor (background thread)
# ---------------------------------------------------------------------------

class ResourceMonitor:
    """
    Samples CPU % and available memory (MB) at a fixed interval while
    an experiment is running.  Call start() / stop(); then read .samples.
    """

    def __init__(self, interval_s: float = 0.25):
        self.interval_s = interval_s
        self.samples: list[dict] = []
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._stop_event.clear()
        self.samples.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join(timeout=2)

    def _run(self):
        while not self._stop_event.is_set():
            mem = psutil.virtual_memory()
            self.samples.append({
                "timestamp": time.perf_counter(),
                "cpu_percent": psutil.cpu_percent(interval=None),
                "mem_available_mb": mem.available / (1024 ** 2),
                "mem_used_percent": mem.percent,
            })
            time.sleep(self.interval_s)

    def summary(self) -> dict:
        if not self.samples:
            return {}
        cpu_vals = [s["cpu_percent"] for s in self.samples]
        mem_vals = [s["mem_available_mb"] for s in self.samples]
        return {
            "cpu_mean": sum(cpu_vals) / len(cpu_vals),
            "cpu_max": max(cpu_vals),
            "mem_avail_mean_mb": sum(mem_vals) / len(mem_vals),
            "mem_avail_min_mb": min(mem_vals),
        }


# ---------------------------------------------------------------------------
# Core measurement function
# ---------------------------------------------------------------------------

def measure_operation(
    obj_type: str,
    operation: str,       # "create" | "update" | "delete"
    population_size: int, # number of pre-existing objects before the timed op
    repeat: int = 10,     # how many timed operations to perform
) -> dict:
    """
    1. Pre-populate the system with `population_size` objects.
    2. Start the resource monitor.
    3. Perform `repeat` timed operations of the given type.
    4. Stop the monitor.
    5. Clean up everything this function created.
    6. Return timing and resource statistics.
    """
    print(
        f"  [{obj_type:8s}] op={operation:6s}  population={population_size:5d}  "
        f"repeat={repeat} ... ",
        end="",
        flush=True,
    )

    # -- pre-populate --------------------------------------------------------
    pre_ids: list[str] = []
    for _ in range(population_size):
        obj = create_object(obj_type)
        if obj:
            pre_ids.append(obj["id"])

    # For update/delete we need a pool of fresh objects to act on
    action_ids: list[str] = []
    if operation in ("update", "delete"):
        for _ in range(repeat):
            obj = create_object(obj_type)
            if obj:
                action_ids.append(obj["id"])
        # Trim if API returned fewer than requested
        action_ids = action_ids[:repeat]

    # -- start monitor -------------------------------------------------------
    monitor = ResourceMonitor(interval_s=0.1)
    monitor.start()

    # -- timed operations ----------------------------------------------------
    durations_ms: list[float] = []
    created_in_op: list[str] = []

    for i in range(repeat):
        t0 = time.perf_counter()

        if operation == "create":
            obj = create_object(obj_type)
            t1 = time.perf_counter()
            if obj:
                created_in_op.append(obj["id"])

        elif operation == "update":
            if i < len(action_ids):
                update_object(obj_type, action_ids[i])
            t1 = time.perf_counter()

        elif operation == "delete":
            if i < len(action_ids):
                delete_object(obj_type, action_ids[i])
            t1 = time.perf_counter()

        else:
            t1 = t0  # should not happen

        durations_ms.append((t1 - t0) * 1000)

    # -- stop monitor --------------------------------------------------------
    monitor.stop()
    resource_summary = monitor.summary()

    # -- cleanup -------------------------------------------------------------
    for oid in pre_ids + created_in_op:
        delete_object(obj_type, oid)
    # action_ids that were not deleted (update case or partial delete)
    if operation == "update":
        for oid in action_ids:
            delete_object(obj_type, oid)
    elif operation == "delete":
        # already deleted above; any leftovers from failures
        remaining = set(action_ids) - set(get_all_ids(obj_type))  # noqa: just cleanup
        for oid in action_ids:
            try:
                delete_object(obj_type, oid)
            except Exception:
                pass

    # -- statistics ----------------------------------------------------------
    durations_ms.sort()
    n = len(durations_ms)
    mean_ms = sum(durations_ms) / n if n else 0.0
    median_ms = durations_ms[n // 2] if n else 0.0
    p95_ms = durations_ms[int(n * 0.95)] if n else 0.0
    min_ms = durations_ms[0] if n else 0.0
    max_ms = durations_ms[-1] if n else 0.0

    print(
        f"mean={mean_ms:.1f}ms  cpu={resource_summary.get('cpu_mean', 0):.1f}%  "
        f"memAvail={resource_summary.get('mem_avail_mean_mb', 0):.0f}MB"
    )

    return {
        "obj_type": obj_type,
        "operation": operation,
        "population_size": population_size,
        "repeat": n,
        "mean_ms": round(mean_ms, 3),
        "median_ms": round(median_ms, 3),
        "p95_ms": round(p95_ms, 3),
        "min_ms": round(min_ms, 3),
        "max_ms": round(max_ms, 3),
        "raw_durations_ms": durations_ms,
        **resource_summary,
    }


# ---------------------------------------------------------------------------
# Experiment runner
# ---------------------------------------------------------------------------

def run_experiments(
    obj_types: list[str],
    sizes: list[int],
    repeat: int = 10,
) -> list[dict]:
    operations = ["create", "update", "delete"]
    results = []

    for obj_type in obj_types:
        print(f"\n{'='*60}")
        print(f"  Object type: {obj_type.upper()}")
        print(f"{'='*60}")

        for operation in operations:
            print(f"\n  Operation: {operation.upper()}")
            for size in sizes:
                result = measure_operation(obj_type, operation, size, repeat)
                results.append(result)

    return results


# ---------------------------------------------------------------------------
# Results persistence
# ---------------------------------------------------------------------------

def save_raw_csv(results: list[dict], path: Path) -> None:
    """Write one row per individual timing observation."""
    rows = []
    for r in results:
        for dur in r["raw_durations_ms"]:
            rows.append({
                "obj_type": r["obj_type"],
                "operation": r["operation"],
                "population_size": r["population_size"],
                "duration_ms": round(dur, 3),
                "cpu_mean": r.get("cpu_mean", ""),
                "cpu_max": r.get("cpu_max", ""),
                "mem_avail_mean_mb": r.get("mem_avail_mean_mb", ""),
                "mem_avail_min_mb": r.get("mem_avail_min_mb", ""),
            })
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n[saved] {path}")


def save_aggregated_csv(results: list[dict], path: Path) -> None:
    """Write one row per (obj_type, operation, population_size) group."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "obj_type", "operation", "population_size", "repeat",
        "mean_ms", "median_ms", "p95_ms", "min_ms", "max_ms",
        "cpu_mean", "cpu_max", "mem_avail_mean_mb", "mem_avail_min_mb",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in fields})
    print(f"[saved] {path}")


# ---------------------------------------------------------------------------
# Chart generation (requires matplotlib)
# ---------------------------------------------------------------------------

def generate_charts(results: list[dict], charts_dir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")   # non-interactive backend
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
    except ImportError:
        print("[charts] matplotlib not installed — skipping chart generation.")
        print("         Install with:  pip install matplotlib")
        return

    charts_dir.mkdir(parents=True, exist_ok=True)

    # Group: (obj_type, operation) → list of result dicts sorted by size
    from collections import defaultdict
    groups: dict[tuple, list] = defaultdict(list)
    for r in results:
        groups[(r["obj_type"], r["operation"])].append(r)
    for key in groups:
        groups[key].sort(key=lambda x: x["population_size"])

    # ---- Timing charts (mean + p95) per group ----
    for (obj_type, operation), data in groups.items():
        sizes = [d["population_size"] for d in data]
        means = [d["mean_ms"] for d in data]
        p95s  = [d["p95_ms"]  for d in data]

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(sizes, means, marker="o", label="Mean (ms)", color="#1f77b4")
        ax.plot(sizes, p95s,  marker="s", linestyle="--", label="P95 (ms)", color="#ff7f0e")
        ax.fill_between(sizes, means, p95s, alpha=0.15, color="#1f77b4")
        ax.set_xlabel("Number of Pre-existing Objects", fontsize=11)
        ax.set_ylabel("Response Time (ms)", fontsize=11)
        ax.set_title(
            f"Response Time vs Object Count\n"
            f"Object: {obj_type.capitalize()}  |  Operation: {operation.upper()}",
            fontsize=12,
        )
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        fig.tight_layout()
        fname = charts_dir / f"{obj_type}_{operation}_timing.png"
        fig.savefig(fname, dpi=150)
        plt.close(fig)
        print(f"[chart] {fname}")

    # ---- CPU chart per (obj_type, operation) ----
    for (obj_type, operation), data in groups.items():
        sizes     = [d["population_size"] for d in data]
        cpu_means = [d.get("cpu_mean", 0) for d in data]
        cpu_maxs  = [d.get("cpu_max", 0)  for d in data]

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(sizes, cpu_means, marker="o", label="CPU Mean %", color="#2ca02c")
        ax.plot(sizes, cpu_maxs,  marker="^", linestyle="--", label="CPU Max %", color="#d62728")
        ax.set_xlabel("Number of Pre-existing Objects", fontsize=11)
        ax.set_ylabel("CPU Utilization (%)", fontsize=11)
        ax.set_title(
            f"CPU Usage vs Object Count\n"
            f"Object: {obj_type.capitalize()}  |  Operation: {operation.upper()}",
            fontsize=12,
        )
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_ylim(0, 105)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        fig.tight_layout()
        fname = charts_dir / f"{obj_type}_{operation}_cpu.png"
        fig.savefig(fname, dpi=150)
        plt.close(fig)
        print(f"[chart] {fname}")

    # ---- Memory chart per (obj_type, operation) ----
    for (obj_type, operation), data in groups.items():
        sizes     = [d["population_size"] for d in data]
        mem_means = [d.get("mem_avail_mean_mb", 0) for d in data]
        mem_mins  = [d.get("mem_avail_min_mb", 0)  for d in data]

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(sizes, mem_means, marker="o", label="Avg Free Memory (MB)", color="#9467bd")
        ax.plot(sizes, mem_mins,  marker="v", linestyle="--", label="Min Free Memory (MB)", color="#8c564b")
        ax.fill_between(sizes, mem_mins, mem_means, alpha=0.15, color="#9467bd")
        ax.set_xlabel("Number of Pre-existing Objects", fontsize=11)
        ax.set_ylabel("Available Memory (MB)", fontsize=11)
        ax.set_title(
            f"Free Memory vs Object Count\n"
            f"Object: {obj_type.capitalize()}  |  Operation: {operation.upper()}",
            fontsize=12,
        )
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        fig.tight_layout()
        fname = charts_dir / f"{obj_type}_{operation}_memory.png"
        fig.savefig(fname, dpi=150)
        plt.close(fig)
        print(f"[chart] {fname}")

    # ---- Combined overview: mean response time, all object types, per operation ----
    operations   = sorted({k[1] for k in groups})
    obj_types_all = sorted({k[0] for k in groups})
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for operation in operations:
        fig, ax = plt.subplots(figsize=(10, 5))
        for i, obj_type in enumerate(obj_types_all):
            data = groups.get((obj_type, operation), [])
            if not data:
                continue
            sizes = [d["population_size"] for d in data]
            means = [d["mean_ms"] for d in data]
            ax.plot(sizes, means, marker="o", label=obj_type.capitalize(),
                    color=colors[i % len(colors)])
        ax.set_xlabel("Number of Pre-existing Objects", fontsize=11)
        ax.set_ylabel("Mean Response Time (ms)", fontsize=11)
        ax.set_title(
            f"Mean Response Time vs Object Count — {operation.upper()}",
            fontsize=12,
        )
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        fig.tight_layout()
        fname = charts_dir / f"all_objects_{operation}_timing_overview.png"
        fig.savefig(fname, dpi=150)
        plt.close(fig)
        print(f"[chart] {fname}")


# ---------------------------------------------------------------------------
# Service health check
# ---------------------------------------------------------------------------

def check_service() -> bool:
    try:
        r = requests.get(f"{BASE_URL}/todos", timeout=5)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Part C Performance Test Suite for REST API Todo List Manager"
    )
    parser.add_argument(
        "--object",
        nargs="+",
        choices=["todo", "project", "category"],
        default=["todo", "project", "category"],
        help="Which object types to test (default: all three).",
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=DEFAULT_SIZES,
        help=(
            "Space-separated list of pre-existing object counts to test. "
            f"Default: {DEFAULT_SIZES}"
        ),
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=10,
        help="Number of timed repetitions per (object, operation, size) cell (default: 10).",
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip chart generation.",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default=str(RESULTS_DIR),
        help=f"Directory to write output files. Default: {RESULTS_DIR}",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    charts_dir  = results_dir / "charts"

    print("=" * 60)
    print("  Part C — REST API Performance Test Suite")
    print(f"  Run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"  Object types : {args.object}")
    print(f"  Sizes        : {args.sizes}")
    print(f"  Repeat       : {args.repeat}")
    print(f"  Results dir  : {results_dir}")
    print("=" * 60)

    if not check_service():
        print(
            "\n[ERROR] REST API service is not running at "
            f"{BASE_URL}.\nStart it first, then re-run this script."
        )
        raise SystemExit(1)

    # Warm-up: prime the JVM / framework caches with a few throwaway calls
    print("\n[warm-up] Sending 5 warm-up requests to prime the server...", flush=True)
    for _ in range(5):
        obj = create_object("todo")
        if obj:
            delete_object("todo", obj["id"])
    print("[warm-up] done.\n")

    results = run_experiments(
        obj_types=args.object,
        sizes=args.sizes,
        repeat=args.repeat,
    )

    # Persist results
    save_raw_csv(results, results_dir / "raw_results.csv")
    save_aggregated_csv(results, results_dir / "aggregated_results.csv")

    # Charts
    if not args.no_charts:
        print("\n[charts] Generating charts...")
        generate_charts(results, charts_dir)

    print("\n" + "=" * 60)
    print("  Performance tests complete.")
    print(f"  Results saved to: {results_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
