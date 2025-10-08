"""
简化的依赖安装验证脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_core_dependencies():
    """测试核心依赖"""
    print("🔍 测试核心Python依赖...")
    
    core_modules = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_jwt_extended', 'Flask-JWT-Extended'),
        ('flask_migrate', 'Flask-Migrate'),
        ('flask_cors', 'Flask-CORS'),
        ('flask_limiter', 'Flask-Limiter'),
        ('marshmallow', 'Marshmallow'),
        ('marshmallow_sqlalchemy', 'Marshmallow-SQLAlchemy'),
        ('pymysql', 'PyMySQL'),
        ('dotenv', 'python-dotenv'),
        ('cryptography', 'Cryptography'),
        ('requests', 'Requests'),
        ('redis', 'Redis'),
        ('psutil', 'psutil'),
        ('bleach', 'Bleach')
    ]
    
    success_count = 0
    total_count = len(core_modules)
    
    for module_name, display_name in core_modules:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
            success_count += 1
        except ImportError as e:
            print(f"✗ {display_name} - {str(e)}")
    
    print(f"\n依赖安装完成度: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    return success_count == total_count

def test_security_functionality():
    """测试基础安全功能"""
    print("\n🔍 测试基础安全功能...")
    
    try:
        # 测试加密功能
        import hashlib
        import hmac
        import secrets
        from cryptography.fernet import Fernet
        
        # 测试哈希
        test_data = "test_password_123"
        hash_result = hashlib.sha256(test_data.encode()).hexdigest()
        assert len(hash_result) == 64
        print("✓ SHA256哈希功能")
        
        # 测试HMAC
        secret_key = secrets.token_bytes(32)
        hmac_result = hmac.new(secret_key, test_data.encode(), hashlib.sha256).hexdigest()
        assert len(hmac_result) == 64
        print("✓ HMAC签名功能")
        
        # 测试对称加密
        encryption_key = Fernet.generate_key()
        cipher = Fernet(encryption_key)
        encrypted = cipher.encrypt(test_data.encode())
        decrypted = cipher.decrypt(encrypted).decode()
        assert decrypted == test_data
        print("✓ AES对称加密功能")
        
        # 测试随机数生成
        random_token = secrets.token_urlsafe(32)
        assert len(random_token) >= 32
        print("✓ 安全随机数生成")
        
        print("✓ 所有安全功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 安全功能测试失败: {str(e)}")
        return False

def test_web_framework():
    """测试Web框架功能"""
    print("\n🔍 测试Web框架功能...")
    
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_jwt_extended import JWTManager
        from flask_cors import CORS
        from flask_limiter import Limiter
        
        # 创建简单的Flask应用
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
        
        # 初始化扩展
        db = SQLAlchemy(app)
        jwt = JWTManager(app)
        cors = CORS(app)
        
        print("✓ Flask应用创建")
        print("✓ SQLAlchemy集成")
        print("✓ JWT集成")
        print("✓ CORS集成")
        
        # 测试应用上下文
        with app.app_context():
            print("✓ 应用上下文工作正常")
        
        print("✓ Web框架功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ Web框架测试失败: {str(e)}")
        return False

def test_database_connectivity():
    """测试数据库连接能力"""
    print("\n🔍 测试数据库连接能力...")
    
    try:
        import pymysql
        from sqlalchemy import create_engine, text
        
        # 测试内存数据库
        engine = create_engine('sqlite:///:memory:', echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            assert result.fetchone()[0] == 1
        
        print("✓ SQLite内存数据库连接")
        print("✓ PyMySQL驱动可用")
        print("✓ 数据库连接能力测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接测试失败: {str(e)}")
        return False

def test_monitoring_capabilities():
    """测试监控能力"""
    print("\n🔍 测试系统监控能力...")
    
    try:
        import psutil
        import time
        
        # 测试系统监控
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.' if sys.platform != 'win32' else 'C:')
        
        print(f"✓ CPU使用率监控: {cpu_percent:.1f}%")
        print(f"✓ 内存使用率监控: {memory.percent:.1f}%")
        print(f"✓ 磁盘使用率监控: {disk.used/disk.total*100:.1f}%")
        
        # 测试进程监控
        current_process = psutil.Process()
        process_info = {
            'pid': current_process.pid,
            'memory_percent': current_process.memory_percent(),
            'cpu_percent': current_process.cpu_percent()
        }
        print(f"✓ 进程监控: PID={process_info['pid']}")
        
        print("✓ 系统监控能力测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 监控能力测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("IT运维系统依赖安装验证")
    print("="*60)
    
    tests = [
        ("核心依赖测试", test_core_dependencies),
        ("安全功能测试", test_security_functionality),
        ("Web框架测试", test_web_framework),
        ("数据库连接测试", test_database_connectivity),
        ("监控能力测试", test_monitoring_capabilities)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 执行异常: {str(e)}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("依赖安装验证结果")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")
    
    print(f"\n验证通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有依赖安装成功！系统已准备就绪！")
        print("\n接下来可以：")
        print("1. 配置环境变量（复制.env.production.template为.env）")
        print("2. 初始化数据库（flask db upgrade）")
        print("3. 启动系统（python run.py）")
        return True
    else:
        print(f"\n⚠️  有 {total-passed} 项测试失败，请安装缺失的依赖。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)