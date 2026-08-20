#!/usr/bin/env python3
"""Validate the live CPU-only translation daemon and its memory headroom."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "backend"))

from crushme_app.services.translation_client import TranslationClient  # noqa: E402

REFERENCE_TRANSLATIONS = (
    (
        "Los regalos convierten momentos especiales en recuerdos inolvidables.",
        "es",
        "en",
        "Gifts turn special moments into unforgettable memories.",
    ),
    (
        "Gifts turn special moments into unforgettable memories.",
        "en",
        "es",
        "Los regalos convierten los momentos especiales en recuerdos inolvidables.",
    ),
)


def _service_memory(service: str) -> tuple[int, int]:
    result = subprocess.run(
        [
            "systemctl",
            "show",
            service,
            "--property=MemoryPeak",
            "--property=MemoryMax",
            "--value",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    values = [int(value) for value in result.stdout.splitlines() if value]
    if len(values) != 2:
        raise RuntimeError(f"Unable to read memory limits for {service}")
    return values[0], values[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--socket",
        type=Path,
        default=Path("/run/crushme-translation/translation.sock"),
    )
    parser.add_argument("--service", default="crushme-translation.service")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--min-headroom", type=float, default=25.0)
    args = parser.parse_args()

    client = TranslationClient(args.socket, args.timeout)
    initial_health = client.health()
    translations = []
    for text, source, target, expected in REFERENCE_TRANSLATIONS:
        actual = client.translate(text, source, target)
        if actual != expected:
            raise RuntimeError(f"Unexpected {source}->{target} translation: {actual!r}")
        translations.append({"pair": f"{source}-{target}", "result": actual})

    final_health = client.health()
    if initial_health.get("torch_loaded") or final_health.get("torch_loaded"):
        raise RuntimeError("Translation daemon loaded Torch")

    memory_peak, memory_max = _service_memory(args.service)
    if memory_max <= 0:
        raise RuntimeError(f"Invalid MemoryMax for {args.service}: {memory_max}")
    headroom = (1 - (memory_peak / memory_max)) * 100
    if headroom < args.min_headroom:
        raise RuntimeError(
            f"Translation memory headroom {headroom:.1f}% is below "
            f"{args.min_headroom:.1f}%"
        )

    print(
        json.dumps(
            {
                "engine": final_health["engine"],
                "torch_loaded": final_health["torch_loaded"],
                "memory_peak_bytes": memory_peak,
                "memory_max_bytes": memory_max,
                "memory_headroom_percent": round(headroom, 1),
                "translations": translations,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
