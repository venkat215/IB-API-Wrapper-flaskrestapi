from multiprocessing import cpu_count

bind = "10.23.218.102:5000"
workers = cpu_count()*2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 30
keepalive = 2
daemon = False
loglevel = 'info'
accesslog = 'logs/access.log'
errorlog = 'logs/errors.log'
