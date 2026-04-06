# Part C — Performance Test Suite

## Overview

`performance_test.py` measures **response time**, **CPU utilisation**, and
**available free memory** as the number of pre-existing API objects grows.

Three object types are tested: **todo**, **project**, and **category**.  
Three operations are measured per type: **CREATE**, **UPDATE (amend)**, and **DELETE**.

---

## Prerequisites

1. **Python 3.10+**
2. Install dependencies:

```bash
pip install -r requirements.txt          # project deps
pip install psutil matplotlib            # perf-test extras
```

3. **Start the REST API** (jarfile from Part A) before running:

```bash
java -jar rest-api-todo-list-manager.jar &   # or however your team starts it
```

---

## Running the Tests

### Full suite (all objects, all operations, default sizes)

```bash
python performance_tests/performance_test.py
```

### Custom object and sizes

```bash
python performance_tests/performance_test.py \
    --object todo project \
    --sizes 1 10 50 100 200 500 1000 \
    --repeat 10
```

### Without charts (faster, just CSV output)

```bash
python performance_tests/performance_test.py --no-charts
```

### All flags

| Flag | Default | Description |
|------|---------|-------------|
| `--object` | `todo project category` | Which object types to test |
| `--sizes` | `1 10 50 100 200 500 1000` | Pre-existing object counts to iterate over |
| `--repeat` | `10` | Timed repetitions per (object, operation, size) cell |
| `--no-charts` | off | Skip matplotlib chart generation |
| `--results-dir` | `results/` | Where to write CSV and PNG outputs |

---

## Outputs

After the run, the `results/` directory contains:

```
results/
  raw_results.csv           — every individual timing observation (ms)
  aggregated_results.csv    — mean / median / P95 per group + CPU/memory stats
  charts/
    todo_create_timing.png
    todo_create_cpu.png
    todo_create_memory.png
    ... (one timing + cpu + memory chart per object × operation)
    all_objects_create_timing_overview.png
    all_objects_update_timing_overview.png
    all_objects_delete_timing_overview.png
```

### CSV columns

**`aggregated_results.csv`**

| Column | Description |
|--------|-------------|
| `obj_type` | `todo` / `project` / `category` |
| `operation` | `create` / `update` / `delete` |
| `population_size` | Number of pre-existing objects |
| `repeat` | Number of timed observations |
| `mean_ms` | Arithmetic mean response time (ms) |
| `median_ms` | Median response time (ms) |
| `p95_ms` | 95th-percentile response time (ms) |
| `min_ms` | Minimum response time (ms) |
| `max_ms` | Maximum response time (ms) |
| `cpu_mean` | Mean CPU % sampled during the batch |
| `cpu_max` | Peak CPU % sampled during the batch |
| `mem_avail_mean_mb` | Mean available RAM (MB) during the batch |
| `mem_avail_min_mb` | Minimum available RAM (MB) during the batch |

---

## Methodology

1. **Pre-population** — Before each timed batch the system is populated with
   exactly `population_size` objects of the target type so we can observe how
   response time scales with data set size.
2. **Warm-up** — Five throwaway create/delete requests are sent before any
   measurement begins to prime the JVM JIT compiler and network stack.
3. **Resource sampling** — A background thread samples `psutil.cpu_percent()`
   and `psutil.virtual_memory().available` every 100 ms throughout the timed
   batch.
4. **Cleanup** — All objects created during pre-population and during the
   timed batch are deleted after each cell so the next cell starts clean.

---

## Interpreting Results

* **Flat / near-flat timing curve** — O(1) or O(log n) server behaviour.
  Ideal for all CRUD operations.
* **Rising curve** — Could indicate linear scan of an in-memory list,
  inefficient ID lookup, or growing GC pressure in the Java process.
* **Memory decline** — Persistent memory reduction across population sizes
  may indicate Java heap growth without GC reclaiming, or a memory leak.
* **CPU spikes at large sizes** — May indicate missing indexes or expensive
  serialisation.
