import multiprocessing
import os
from distutils.util import strtobool

bind = f"0.0.0.0:{os.getenv('GUNICORN_BIND_PORT', '8000')}"
accesslog = "-"

workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2))
threads = int(os.getenv("PYTHON_MAX_THREADS", 1))

reload = bool(strtobool(os.getenv("WEB_RELOAD", "false")))
