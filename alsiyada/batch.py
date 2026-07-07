from __future__ import annotations

import json
import statistics
import time
import tracemalloc
from pathlib import Path

from .policy import evaluate_manifest


def _p(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))]


def evaluate(path: str | Path, *, repeat: int = 1) -> dict:
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    tp = tn = fp = fn = errors = 0
    latencies = []
    started = time.perf_counter()
    tracemalloc.start()
    for _ in range(repeat):
        for row in rows:
            t0 = time.perf_counter()
            try:
                result = evaluate_manifest(row)
                predicted = result["decision"] == "BLOCK"
                expected = bool(row.get("expected_block"))
            except Exception:
                errors += 1
                predicted = True
                expected = bool(row.get("expected_block"))
            if expected and predicted:
                tp += 1
            elif expected and not predicted:
                fn += 1
            elif not expected and predicted:
                fp += 1
            else:
                tn += 1
            latencies.append((time.perf_counter() - t0) * 1000)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"processed": len(rows) * repeat, "errors": errors, "metrics": {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "tn": tn, "fp": fp, "fn": fn}, "latency_ms": {"mean": statistics.fmean(latencies) if latencies else 0.0, "p99": _p(latencies, 99)}, "memory_mb": {"current": current / 1_000_000, "peak": peak / 1_000_000}, "elapsed_seconds": time.perf_counter() - started, "collapse_check": {"passed": errors == 0, "criteria": "errors == 0"}}

