import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
# Recommended: (2 * cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'eventlet' # Required for SocketIO
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-" # Stdout
errorlog = "-"  # Stderr
loglevel = "info"

# Process naming
proc_name = "surat_textile_nexus"
