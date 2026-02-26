import multiprocessing
import os

# Gunicorn configuration for Render Free Tier (512MB RAM)
bind = "0.0.0.0:" + os.environ.get("PORT", "5000")

# Reduce workers to save memory on 512MB RAM limit
workers = 2
threads = 4

# Use gthread for better memory management than eventlet/gevent on low-RAM
worker_class = "gthread"

# Timeout settings
timeout = 120
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
