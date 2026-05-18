# SPDX-License-Identifier: FSL-1.1-MIT
import multiprocessing
import os


def _parse_bool(value: str) -> bool:
    normalized = value.lower()
    if normalized in {"y", "yes", "t", "true", "on", "1"}:
        return True
    if normalized in {"n", "no", "f", "false", "off", "0"}:
        return False
    raise ValueError(f"invalid truth value {value!r}")

bind = f"0.0.0.0:{os.getenv('GUNICORN_BIND_PORT', '8000')}"
accesslog = "-"

workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2))
threads = int(os.getenv("PYTHON_MAX_THREADS", 1))

reload = _parse_bool(os.getenv("WEB_RELOAD", "false"))
