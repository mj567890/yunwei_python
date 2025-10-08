"""
系统启动测试脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'development')

def test_app_creation():
    """测试应用创建"""
    try:
        print("🔍 测试应用创建...")
        from app import create_app
        app = create_app()
        print("✓ Flask应用创建成功")
        
        # 测试应用配置
        print("🔍 测试应用配置...")
        with app.app_context():
            print(f"✓ 应用名称: {app.name}")
            print(f"✓ 调试模式: {app.debug}")
            print(f"✓ 配置类: {app.config.__class__.__name__}")
        
        return True
        
    except Exception as e:
        print(f"✗ 应用创建失败: {str(e)}")
        return False

def test_security_modules():
    """测试安全模块导入"""
    print("\n🔍 测试安全模块导入...")
    modules = [
        'app.utils.api_signature',
        'app.utils.anomaly_detection', 
        'app.utils.communication_security',
        'app.utils.compliance_checker',
        'app.utils.performance_monitor',
        'app.middleware.security_middleware'
    ]
    
    success_count = 0
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
            success_count += 1
        except Exception as e:
            print(f"✗ {module} - {str(e)}")
    
    return success_count == len(modules)

def test_database_models():
    """测试数据库模型"""
    print("\n🔍 测试数据库模型...")
    try:
        from app.models.user import User
        from app.models.role import Role
        print("✓ 用户和角色模型导入成功")
        return True
    except Exception as e:
        print(f"✗ 数据库模型导入失败: {str(e)}")
        return False

def test_api_blueprints():
    """测试API蓝图"""
    print("\n🔍 测试API蓝图...")
    blueprints = [
        'app.api.auth',
        'app.api.user', 
        'app.api.monitor'
    ]
    
    success_count = 0
    for blueprint in blueprints:
        try:
            __import__(blueprint)
            print(f"✓ {blueprint}")
            success_count += 1
        except Exception as e:
            print(f"✗ {blueprint} - {str(e)}")
    
    return success_count == len(blueprints)

def main():
    """主测试函数"""
    print("="*60)
    print("IT运维系统启动测试")
    print("="*60)
    
    tests = [
        ("应用创建测试", test_app_creation),
        ("安全模块测试", test_security_modules),
        ("数据库模型测试", test_database_models),
        ("API蓝图测试", test_api_blueprints)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 执行失败: {str(e)}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以正常启动！")
        return True
    else:
        print(f"\n⚠️  有 {total-passed} 项测试失败。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)