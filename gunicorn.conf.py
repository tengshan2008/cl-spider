workers = 5  # 定义同时开启的处理请求的进程数量，根据网站流量适当调节
worker_class = "gevent"  # 采用 gevent 库，支持异步处理请求，提高吞吐量
bind = "0.0.0.0:8000"
