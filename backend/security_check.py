"""
系统启动时的安全检查脚本
确保系统符合等保2.0要求
"""
import os
import sys
import warnings
from pathlib import Path
from datetime import datetime

def check_production_security():
    """检查生产环境安全配置"""
    issues = []
    
    # 检查必要的环境变量
    required_vars = [
        'SECRET_KEY',
        'JWT_SECRET_KEY', 
        'DATA_ENCRYPTION_KEY',
        'API_SIGNATURE_SECRET'
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            issues.append(f"缺少必要的环境变量: {var}")
        elif len(value) < 32:
            issues.append(f"环境变量 {var} 长度不足32位，当前长度: {len(value)}")
    
    # 检查数据库配置
    db_vars = ['MYSQL_USERNAME', 'MYSQL_PASSWORD', 'MYSQL_HOST', 'MYSQL_DATABASE']
    for var in db_vars:
        if not os.environ.get(var):
            issues.append(f"缺少数据库配置: {var}")
    
    # 检查密码复杂性
    mysql_password = os.environ.get('MYSQL_PASSWORD', '')
    if mysql_password and len(mysql_password) < 8:
        issues.append("数据库密码长度不足8位")
    
    # 检查文件权限
    sensitive_files = [
        '.env',
        '.env.production',
        'config/config.py'
    ]
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            # 检查文件是否对其他用户可读
            if stat.st_mode & 0o044:  # 其他用户可读
                issues.append(f"敏感文件 {file_path} 权限过宽，建议设置为600")
    
    return issues


def check_runtime_security():
    """检查运行时安全配置"""
    issues = []
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        issues.append(f"Python版本 {sys.version} 过低，建议使用3.8以上版本")
    
    # 检查SSL/TLS支持
    try:
        import ssl
        context = ssl.create_default_context()
        if context.protocol < ssl.PROTOCOL_TLSv1_2:
            issues.append("SSL/TLS版本过低，建议使用TLS 1.2以上")
    except ImportError:
        issues.append("SSL模块不可用")
    
    # 检查加密库
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
    except ImportError:
        issues.append("加密库cryptography不可用")
    
    # 检查关键目录
    critical_dirs = ['logs', 'uploads', 'backups']
    for dir_name in critical_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                # 设置目录权限
                os.chmod(dir_name, 0o750)
            except Exception as e:
                issues.append(f"无法创建关键目录 {dir_name}: {str(e)}")
    
    return issues


def generate_security_keys():
    """生成安全密钥"""
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import secrets
        
        keys = {}
        
        # 生成对称加密密钥
        keys['data_encryption_key'] = Fernet.generate_key().decode()
        
        # 生成API签名秘钥
        keys['api_signature_secret'] = secrets.token_urlsafe(64)
        
        # 生成JWT密钥
        keys['jwt_secret_key'] = secrets.token_urlsafe(64)
        
        # 生成系统密钥
        keys['secret_key'] = secrets.token_urlsafe(64)
        
        # 生成RSA密钥对
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        keys['server_private_key'] = private_pem.decode()
        keys['server_public_key'] = public_pem.decode()
        
        return keys
        
    except ImportError as e:
        print(f"生成安全密钥失败，缺少依赖: {e}")
        return None


def create_env_template():
    """创建环境变量模板"""
    keys = generate_security_keys()
    if not keys:
        return False
    
    template_content = f"""# IT运维系统环境变量配置
# 生成时间: {datetime.now().isoformat()}
# 
# 重要: 生产环境必须修改所有密钥和密码！
# 

# Flask应用配置
FLASK_ENV=production
SECRET_KEY={keys['secret_key']}

# JWT配置
JWT_SECRET_KEY={keys['jwt_secret_key']}

# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=it_ops_user
MYSQL_PASSWORD=change_this_strong_password_123!
MYSQL_DATABASE=it_ops_system

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 数据加密
DATA_ENCRYPTION_KEY={keys['data_encryption_key']}

# API签名验证
ENABLE_API_SIGNATURE=true
API_SIGNATURE_SECRET={keys['api_signature_secret']}
SIGNATURE_TIMEOUT=300

# 异常检测
ENABLE_ANOMALY_DETECTION=true
ANOMALY_DETECTION_SENSITIVITY=medium
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=1800

# 安全通信
ENABLE_SECURE_COMMUNICATION=false
RSA_PRIVATE_KEY_PATH=
RSA_PUBLIC_KEY_PATH=
SESSION_KEY_LENGTH=32

# 性能监控
PERFORMANCE_MONITORING=true
MONITORING_INTERVAL=60
ALERT_CPU_THRESHOLD=80.0
ALERT_MEMORY_THRESHOLD=85.0
ALERT_DISK_THRESHOLD=90.0

# 服务器密钥对
SERVER_PRIVATE_KEY="{keys['server_private_key'].replace(chr(10), '\\n')}"
SERVER_PUBLIC_KEY="{keys['server_public_key'].replace(chr(10), '\\n')}"

# 文件上传
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=52428800

# 邮件配置
MAIL_SERVER=
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=

# CORS配置
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# 日志配置
LOG_LEVEL=INFO
LOG_TO_STDOUT=false
"""
    
    try:
        with open('.env.production.new', 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        # 设置文件权限
        os.chmod('.env.production.new', 0o600)
        
        print("✓ 已生成环境变量模板: .env.production.new")
        print("  请检查并修改相关配置，然后重命名为 .env.production")
        return True
        
    except Exception as e:
        print(f"✗ 生成环境变量模板失败: {e}")
        return False


def main():
    """主检查函数"""
    print("=" * 60)
    print("IT运维系统安全检查")
    print("=" * 60)
    
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    # 生产环境安全检查
    if is_production:
        print("🔍 执行生产环境安全检查...")
        prod_issues = check_production_security()
        if prod_issues:
            print("⚠️  发现生产环境安全问题:")
            for issue in prod_issues:
                print(f"   • {issue}")
            print("\n建议修复以上问题后再启动系统")
        else:
            print("✓ 生产环境安全检查通过")
    
    # 运行时安全检查
    print("\n🔍 执行运行时安全检查...")
    runtime_issues = check_runtime_security()
    if runtime_issues:
        print("⚠️  发现运行时安全问题:")
        for issue in runtime_issues:
            print(f"   • {issue}")
    else:
        print("✓ 运行时安全检查通过")
    
    # 检查是否需要生成配置模板
    if not os.path.exists('.env.production') and not os.path.exists('.env'):
        print("\n🔧 检测到缺少环境配置文件")
        response = input("是否生成环境变量模板? (y/N): ")
        if response.lower() in ['y', 'yes']:
            create_env_template()
    
    print("\n" + "=" * 60)
    if is_production and (prod_issues or runtime_issues):
        print("⚠️  检查发现安全问题，建议修复后再启动")
        return False
    else:
        print("✓ 安全检查完成，系统可以安全启动")
        return True


if __name__ == "__main__":
    main()