import os
import sys

# Configurações básicas
bind = "0.0.0.0:" + os.environ.get("PORT", "10000")
workers = 1
threads = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Configuração específica para Windows
if sys.platform == "win32":
    # No Windows, use configurações mais simples
    preload_app = False
    # Desativa recursos específicos do Unix
else:
    preload_app = False

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None