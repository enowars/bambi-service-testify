import multiprocessing

worker_class = "eventlet"
workers = multiprocessing.cpu_count() * 2 + 1
bind = "0.0.0.0:3031"
keepalive = 3600
timeout = 90
