"""
Flask应用配置文件
"""
import os
from datetime import timedelta


class Config:
    """基础配置类"""
    
    # 基础配置 - 生产环境必须设置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise RuntimeError("生产环境必须设置SECRET_KEY环境变量（至少32位）")
        else:
            # 开发环境使用更安全的随机密钥
            import secrets
            SECRET_KEY = 'dev-' + secrets.token_urlsafe(32)
    
    # 数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'password'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'it_ops_system'
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # JWT配置 - 生产环境必须设置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise RuntimeError("生产环境必须设置JWT_SECRET_KEY环境变量（至少32位）")
        else:
            # 开发环境使用更安全的随机密钥
            import secrets
            JWT_SECRET_KEY = 'dev-jwt-' + secrets.token_urlsafe(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # CORS配置
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:3002,http://127.0.0.1:3002,http://localhost:3003,http://127.0.0.1:3003').split(',')
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # 分页配置
    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'false').lower() in ['true', 'on', '1']
    
    # 等保2.0合规配置
    DATA_ENCRYPTION_KEY = os.environ.get('DATA_ENCRYPTION_KEY')  # 数据加密密钥
    API_SECRET_KEY = os.environ.get('API_SECRET_KEY')  # API签名密钥
    ENABLE_API_SIGNATURE = os.environ.get('ENABLE_API_SIGNATURE', 'false').lower() in ['true', 'on', '1']
    ENABLE_SECURE_COMMUNICATION = os.environ.get('ENABLE_SECURE_COMMUNICATION', 'false').lower() in ['true', 'on', '1']
    
    # API签名配置
    API_SIGNATURE_SECRET = os.environ.get('API_SIGNATURE_SECRET', 'default-api-signature-secret-key-change-in-production')
    SIGNATURE_TIMEOUT = int(os.environ.get('SIGNATURE_TIMEOUT', '300'))  # 5分钟
    
    # 异常检测配置
    ENABLE_ANOMALY_DETECTION = os.environ.get('ENABLE_ANOMALY_DETECTION', 'True').lower() == 'true'
    ANOMALY_DETECTION_SENSITIVITY = os.environ.get('ANOMALY_DETECTION_SENSITIVITY', 'medium')
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    ACCOUNT_LOCKOUT_DURATION = int(os.environ.get('ACCOUNT_LOCKOUT_DURATION', '1800'))  # 30分钟
    
    # 安全通信配置
    RSA_PRIVATE_KEY_PATH = os.environ.get('RSA_PRIVATE_KEY_PATH', '')
    RSA_PUBLIC_KEY_PATH = os.environ.get('RSA_PUBLIC_KEY_PATH', '')
    SESSION_KEY_LENGTH = int(os.environ.get('SESSION_KEY_LENGTH', '32'))
    
    # 性能监控配置
    PERFORMANCE_MONITORING = os.environ.get('PERFORMANCE_MONITORING', 'True').lower() == 'true'
    MONITORING_INTERVAL = int(os.environ.get('MONITORING_INTERVAL', '60'))  # 秒
    ALERT_CPU_THRESHOLD = float(os.environ.get('ALERT_CPU_THRESHOLD', '80.0'))
    ALERT_MEMORY_THRESHOLD = float(os.environ.get('ALERT_MEMORY_THRESHOLD', '85.0'))
    ALERT_DISK_THRESHOLD = float(os.environ.get('ALERT_DISK_THRESHOLD', '90.0'))
    
    # 服务器密钥对（用于安全通信）
    SERVER_PRIVATE_KEY = os.environ.get('SERVER_PRIVATE_KEY')
    SERVER_PUBLIC_KEY = os.environ.get('SERVER_PUBLIC_KEY')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}