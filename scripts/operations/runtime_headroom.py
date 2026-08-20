#!/usr/bin/env python3
"""Apply a read-only production load and enforce the CrushMe capacity gate."""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DEFAULT_PATHS = (
    "/api/health/",
    "/es/",
    "/api/products/woocommerce/products/?page=1&page_size=12",
    "/api/products/woocommerce/categories/organized/",
)


def _read_int(path: Path) -> int | None:
    try:
        value = path.read_text(encoding="ascii").strip()
    except (OSError, ValueError):
        return None
    if value == "max":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _control_group(service: str) -> Path:
    result = subprocess.run(
        ["systemctl", "show", service, "--property=ControlGroup", "--value"],
        check=True,
        capture_output=True,
        text=True,
    )
    group = result.stdout.strip().lstrip("/")
    if not group:
        raise RuntimeError(f"{service} does not expose a systemd control group")
    return Path("/sys/fs/cgroup") / group


def _cpu_usage_usec(group: Path) -> int:
    for line in (group / "cpu.stat").read_text(encoding="ascii").splitlines():
        key, value = line.split()
        if key == "usage_usec":
            return int(value)
    raise RuntimeError(f"usage_usec is missing from {group / 'cpu.stat'}")


def _cpu_capacity(group: Path) -> float:
    quota, period = (group / "cpu.max").read_text(encoding="ascii").split()
    if quota == "max":
        return float(os.cpu_count() or 1)
    return int(quota) / int(period)


def _host_available_percent() -> float:
    values = {}
    for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
        key, raw_value, *_unit = line.replace(":", "").split()
        values[key] = int(raw_value)
    return values["MemAvailable"] * 100 / values["MemTotal"]


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


def _validate_base_url(base_url: str) -> None:
    parsed_base = urllib.parse.urlsplit(base_url)
    if parsed_base.scheme not in {"http", "https"} or not parsed_base.netloc:
        raise ValueError("base URL must use HTTP(S) and include a host")


def _request(base_url: str, path: str, timeout: float) -> dict[str, object]:
    _validate_base_url(base_url)
    url = urllib.parse.urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))
    request = urllib.request.Request(
        url,
        headers={
            "Accept-Language": "es",
            "User-Agent": "CrushMe-Wave5-Capacity-Probe/1.0",
        },
        method="GET",
    )
    started = time.monotonic()
    try:
        # The base URL scheme and host are validated immediately above.
        with urllib.request.urlopen(  # nosec B310
            request,
            timeout=timeout,
        ) as response:
            response.read()
            status = response.status
    except urllib.error.HTTPError as error:
        error.read()
        status = error.code
    except (OSError, TimeoutError) as error:
        return {
            "path": path,
            "status": 0,
            "seconds": time.monotonic() - started,
            "error": type(error).__name__,
        }
    return {
        "path": path,
        "status": status,
        "seconds": time.monotonic() - started,
    }


def _paced_request(
    base_url: str,
    path: str,
    timeout: float,
    interval: float,
) -> dict[str, object]:
    result = _request(base_url, path, timeout)
    if interval:
        time.sleep(interval)
    return result


def _memory_sampler(group: Path, samples: list[int], stop: threading.Event) -> None:
    while not stop.wait(0.05):
        current = _read_int(group / "memory.current")
        if current is not None:
            samples.append(current)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://crushme.com.co")
    parser.add_argument("--service", default="crushme_project.service")
    parser.add_argument("--requests", type=int, default=32)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--interval", type=float, default=0.15)
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--min-headroom", type=float, default=30.0)
    parser.add_argument("--max-p95", type=float, default=2.0)
    parser.add_argument("--json-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    if args.requests < 1 or args.concurrency < 1 or args.interval < 0:
        raise SystemExit(
            "--requests/concurrency must be positive; interval cannot be negative"
        )
    if args.concurrency > 4:
        raise SystemExit("production guard: concurrency cannot exceed 4")
    try:
        _validate_base_url(args.base_url)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    group = _control_group(args.service)
    memory_limit = _read_int(group / "memory.max")
    if memory_limit is None:
        raise SystemExit(f"{args.service} must have a finite MemoryMax")

    cpu_before = _cpu_usage_usec(group)
    cpu_capacity = _cpu_capacity(group)
    memory_samples = [_read_int(group / "memory.current") or 0]
    stop = threading.Event()
    sampler = threading.Thread(
        target=_memory_sampler,
        args=(group, memory_samples, stop),
        daemon=True,
    )
    sampler.start()

    paths = [
        DEFAULT_PATHS[index % len(DEFAULT_PATHS)] for index in range(args.requests)
    ]
    started = time.monotonic()
    try:
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            results = list(
                executor.map(
                    lambda path: _paced_request(
                        args.base_url,
                        path,
                        args.timeout,
                        args.interval,
                    ),
                    paths,
                )
            )
    finally:
        elapsed = time.monotonic() - started
        stop.set()
        sampler.join()

    cpu_delta = _cpu_usage_usec(group) - cpu_before
    cpu_utilization = cpu_delta / (elapsed * 1_000_000 * cpu_capacity) * 100
    cpu_headroom = max(0.0, 100 - cpu_utilization)
    memory_peak = max(memory_samples)
    memory_headroom = max(0.0, 100 - memory_peak * 100 / memory_limit)
    host_headroom = _host_available_percent()
    durations = [float(result["seconds"]) for result in results]
    failures = [result for result in results if not 200 <= int(result["status"]) < 400]
    p95 = _percentile(durations, 0.95)
    throughput = len(results) / elapsed

    checks = {
        "http": not failures,
        "latency": p95 <= args.max_p95,
        "memory_headroom": memory_headroom >= args.min_headroom,
        "cpu_headroom": cpu_headroom >= args.min_headroom,
        "host_memory": host_headroom >= 20.0,
    }
    report = {
        "base_url": args.base_url,
        "service": args.service,
        "requests": len(results),
        "concurrency": args.concurrency,
        "interval_seconds": args.interval,
        "failures": len(failures),
        "elapsed_seconds": round(elapsed, 3),
        "throughput_rps": round(throughput, 3),
        "latency_median_ms": round(statistics.median(durations) * 1000, 1),
        "latency_p95_ms": round(p95 * 1000, 1),
        "memory_peak_mib": round(memory_peak / 1024 / 1024, 1),
        "memory_limit_mib": round(memory_limit / 1024 / 1024, 1),
        "memory_headroom_percent": round(memory_headroom, 1),
        "cpu_quota_cores": round(cpu_capacity, 2),
        "cpu_headroom_percent": round(cpu_headroom, 1),
        "host_memory_available_percent": round(host_headroom, 1),
        "checks": checks,
        "passed": all(checks.values()),
    }

    if args.json_output:
        args.json_output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
