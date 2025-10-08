"""
Flask应用工厂函数
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.utils.rate_limit import create_limiter
from app.middleware import security_middleware

# 全局扩展对象
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()
limiter = create_limiter(None)  # 将在create_app中初始化


def create_app(config_class=None):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置
    if config_class:
        app.config.from_object(config_class)
    else:
        from config.config import config
        config_name = os.environ.get('FLASK_ENV') or 'development'
        app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    
    # CORS配置 - 生产环境应该使用具体域名
    allowed_origins = app.config.get('ALLOWED_ORIGINS', ["http://localhost:3000", "http://127.0.0.1:3000"])
    cors.init_app(app, 
                  origins=allowed_origins,
                  supports_credentials=True,
                  methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                  allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    
    jwt.init_app(app)
    # 初始化频率限制器
    from app.utils.rate_limit import create_limiter
    global limiter
    limiter = create_limiter(app)
    
    # 初始化安全中间件
    security_middleware.init_app(app)
    
    # 启动性能监控
    if app.config.get('PERFORMANCE_MONITORING', True):
        from app.utils.performance_monitor import performance_monitor
        monitoring_interval = app.config.get('MONITORING_INTERVAL', 60)
        performance_monitor.start_monitoring(monitoring_interval)
    
    # 注册蓝图
    from app.api import init_api
    init_api(app)
    
    # 创建上传目录
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
    
    # 配置日志
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/it_ops_system.log',
                                           maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('IT运维系统启动')
    
    return app


# 导入模型以便迁移
from app.models import *