# Gunicorn 生产环境配置文件
# 文件名: gunicorn.conf.py

import os
import multiprocessing

# 服务器地址和端口
bind = "0.0.0.0:5000"

# 工作进程数量
# 推荐配置: (2 * CPU核心数) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类型
# sync: 同步工作进程 (适合CPU密集型应用)
# gevent: 异步工作进程 (适合I/O密集型应用)
worker_class = "sync"

# 每个工作进程的线程数
threads = 2

# 工作进程超时时间 (秒)
timeout = 120

# 客户端连接超时时间 (秒)
keepalive = 5

# 最大连接数
max_requests = 1000

# 最大连接抖动 (避免所有进程同时重启)
max_requests_jitter = 100

# 工作进程预加载应用
preload_app = True

# 日志配置
# 访问日志文件
accesslog = "/var/log/it-ops/gunicorn_access.log"

# 错误日志文件
errorlog = "/var/log/it-ops/gunicorn_error.log"

# 日志级别
loglevel = "info"

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = 'it-ops-system'

# PID 文件
pidfile = "/var/run/it-ops/gunicorn.pid"

# 用户和组 (可选，用于权限控制)
# user = "www-data"
# group = "www-data"

# 临时目录
tmp_upload_dir = "/tmp"

# SSL 配置 (如果需要)
# keyfile = "/path/to/your/keyfile.key"
# certfile = "/path/to/your/certfile.crt"

# 环境变量
raw_env = [
    'FLASK_ENV=production',
]

# 启动前钩子函数
def on_starting(server):
    """服务器启动时执行"""
    server.log.info("IT运维系统服务器正在启动...")

def on_reload(server):
    """服务器重载时执行"""
    server.log.info("IT运维系统服务器正在重载...")

def when_ready(server):
    """服务器就绪时执行"""
    server.log.info("IT运维系统服务器已就绪，正在监听 %s", server.address)

def on_exit(server):
    """服务器退出时执行"""
    server.log.info("IT运维系统服务器正在关闭...")

def worker_int(worker):
    """工作进程中断时执行"""
    worker.log.info("工作进程 %s 被中断", worker.pid)

def pre_fork(server, worker):
    """工作进程创建前执行"""
    server.log.info("正在创建工作进程 %s", worker.pid)

def post_fork(server, worker):
    """工作进程创建后执行"""
    server.log.info("工作进程 %s 已创建", worker.pid)

def post_worker_init(worker):
    """工作进程初始化后执行"""
    worker.log.info("工作进程 %s 初始化完成", worker.pid)

def worker_abort(worker):
    """工作进程异常退出时执行"""
    worker.log.error("工作进程 %s 异常退出", worker.pid)

# 内存和性能优化
# 限制请求体大小 (字节)
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# 开发环境配置 (仅用于开发测试)
if os.environ.get('FLASK_ENV') == 'development':
    bind = "127.0.0.1:5000"
    workers = 1
    reload = True
    accesslog = "-"  # 输出到标准输出
    errorlog = "-"   # 输出到标准错误
    loglevel = "debug"