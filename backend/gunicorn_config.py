# Gunicorn Configuration File
# Optimizado para VPS con recursos limitados

import multiprocessing
import os

# Directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Bind
bind = "0.0.0.0:8000"

# Workers
# Fórmula: (2 x CPU cores) + 1
# Para VPS pequeño, limitamos a 2-3 workers máximo
workers = min(2, multiprocessing.cpu_count() * 2 + 1)

# Threads por worker
threads = 2

# Worker class
worker_class = "sync"  # Usar 'sync' para requests normales

# Timeout
timeout = 120  # 2 minutos para requests largos

# Keep alive
keepalive = 5

# Max requests antes de reiniciar worker (previene memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "crushme_backend"

# Preload app (carga la app antes de fork, ahorra memoria)
preload_app = True

# Daemon mode (False para systemd)
daemon = False

# PID file
pidfile = None

# User/Group (opcional, comentado por defecto)
# user = "cerrotico"
# group = "cerrotico"

# Environment variables
raw_env = [
    "DJANGO_SETTINGS_MODULE=crushme_project.settings",
]

# Callbacks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 Gunicorn is starting...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("🔄 Gunicorn is reloading...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"✅ Gunicorn is ready. Workers: {workers}, Threads: {threads}")
    print(f"📍 Listening on: {bind}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("👋 Gunicorn is shutting down...")

# Worker lifecycle
def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"👷 Worker {worker.pid} spawned")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"💀 Worker {worker.pid} exited")
