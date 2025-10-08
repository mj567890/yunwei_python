"""
基础系统测试脚本
测试系统的基本功能和安全配置
"""
import os
import sys
import importlib
from datetime import datetime

def test_python_version():
    """测试Python版本"""
    print("🔍 测试Python版本...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"✓ Python版本 {version.major}.{version.minor}.{version.micro} 满足要求")
        return True
    else:
        print(f"✗ Python版本 {version.major}.{version.minor}.{version.micro} 过低，需要3.8+")
        return False

def test_required_modules():
    """测试必需的模块"""
    print("\n🔍 测试必需模块...")
    required_modules = [
        'flask',
        'flask_sqlalchemy', 
        'flask_jwt_extended',
        'marshmallow',
        'datetime',
        'hashlib',
        'hmac',
        'secrets',
        'json',
        'time',
        'threading'
    ]
    
    results = []
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
            results.append(True)
        except ImportError:
            print(f"✗ {module} - 缺失")
            results.append(False)
    
    return all(results)

def test_file_structure():
    """测试文件结构"""
    print("\n🔍 测试项目文件结构...")
    
    required_paths = [
        'app',
        'app/__init__.py',
        'app/models',
        'app/api',
        'app/utils',
        'config',
        'config/config.py'
    ]
    
    results = []
    for path in required_paths:
        if os.path.exists(path):
            print(f"✓ {path}")
            results.append(True)
        else:
            print(f"✗ {path} - 缺失")
            results.append(False)
    
    return all(results)

def test_security_modules():
    """测试安全模块"""
    print("\n🔍 测试安全模块...")
    
    security_files = [
        'app/utils/api_signature.py',
        'app/utils/anomaly_detection.py', 
        'app/utils/communication_security.py',
        'app/utils/compliance_checker.py',
        'app/utils/performance_monitor.py',
        'app/middleware/security_middleware.py'
    ]
    
    results = []
    for file_path in security_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
            results.append(True)
        else:
            print(f"✗ {file_path} - 缺失")
            results.append(False)
    
    return all(results)

def test_configuration():
    """测试配置"""
    print("\n🔍 测试配置...")
    
    try:
        sys.path.insert(0, '.')
        from config.config import Config
        
        # 检查关键配置属性
        config_attrs = [
            'SECRET_KEY',
            'SQLALCHEMY_DATABASE_URI',
            'JWT_SECRET_KEY',
            'API_SIGNATURE_SECRET',
            'ENABLE_API_SIGNATURE',
            'ENABLE_ANOMALY_DETECTION',
            'PERFORMANCE_MONITORING'
        ]
        
        results = []
        for attr in config_attrs:
            if hasattr(Config, attr):
                print(f"✓ {attr}")
                results.append(True)
            else:
                print(f"✗ {attr} - 缺失")
                results.append(False)
        
        return all(results)
        
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False

def test_api_structure():
    """测试API结构"""
    print("\n🔍 测试API结构...")
    
    api_files = [
        'app/api/__init__.py',
        'app/api/auth.py',
        'app/api/user.py',
        'app/api/monitor.py'
    ]
    
    results = []
    for file_path in api_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
            results.append(True)
        else:
            print(f"✗ {file_path} - 缺失")
            results.append(False)
    
    return all(results)

def test_basic_security_features():
    """测试基础安全功能"""
    print("\n🔍 测试基础安全功能...")
    
    try:
        # 测试密码哈希
        import hashlib
        import hmac
        import secrets
        
        # 测试哈希功能
        test_data = "test_password"
        hash_result = hashlib.sha256(test_data.encode()).hexdigest()
        if len(hash_result) == 64:
            print("✓ SHA256哈希功能正常")
        
        # 测试HMAC功能
        secret_key = secrets.token_bytes(32)
        hmac_result = hmac.new(secret_key, test_data.encode(), hashlib.sha256).hexdigest()
        if len(hmac_result) == 64:
            print("✓ HMAC签名功能正常")
        
        # 测试随机数生成
        random_token = secrets.token_urlsafe(32)
        if len(random_token) >= 32:
            print("✓ 安全随机数生成正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 基础安全功能测试失败: {e}")
        return False

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("系统测试报告")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['passed'])
    
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总测试项: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    print("\n详细结果:")
    for result in results:
        status = "✓" if result['passed'] else "✗"
        print(f"{status} {result['name']}")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！系统基础功能正常。")
        return True
    else:
        print(f"\n⚠️  有 {total_tests - passed_tests} 项测试失败，请检查相关问题。")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("IT运维系统基础测试")
    print("="*60)
    
    # 执行各项测试
    test_results = [
        {'name': 'Python版本检查', 'passed': test_python_version()},
        {'name': '必需模块检查', 'passed': test_required_modules()},
        {'name': '文件结构检查', 'passed': test_file_structure()},
        {'name': '安全模块检查', 'passed': test_security_modules()},
        {'name': '配置检查', 'passed': test_configuration()},
        {'name': 'API结构检查', 'passed': test_api_structure()},
        {'name': '基础安全功能检查', 'passed': test_basic_security_features()}
    ]
    
    # 生成报告
    all_passed = generate_test_report(test_results)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)