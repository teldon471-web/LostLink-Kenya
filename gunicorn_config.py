"""
Gunicorn configuration file for Django
Place in project root alongside manage.py
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'lostlink-kenya'

# Server hooks
def post_fork(server, worker):
    """
    Called just after a worker has been forked.
    """
    pass

def pre_fork(server, worker):
    """
    Called just prior to forking the worker subprocess.
    """
    pass

def pre_exec(server):
    """
    Called just prior to forking off a brand new master process.
    """
    pass

def when_ready(server):
    """
    Called just after the server is started.
    """
    pass

def child_exit(server, worker):
    """
    Called just after a worker has been exited.
    """
    pass

def worker_exit(server, worker):
    """
    Called when a worker is terminated.
    """
    pass

def nworkers_changed(server, new_value, old_value):
    """
    Called just after num_workers has been changed.
    """
    pass

def on_exit(server):
    """
    Called just before exiting Gunicorn.
    """
    pass
