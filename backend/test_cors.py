"""
测试CORS配置脚本
"""
import requests
import json

def test_cors_from_port(port):
    """测试从指定端口访问后端API的CORS支持"""
    print(f"\n🔍 测试从端口 {port} 访问后端API...")
    
    headers = {
        'Origin': f'http://localhost:{port}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 测试健康检查接口
        print(f"1. 测试健康检查接口...")
        response = requests.get('http://localhost:5000/api/health', headers=headers)
        print(f"   状态码: {response.status_code}")
        print(f"   CORS头: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
        
        if response.status_code == 200:
            print("   ✅ 健康检查成功")
        else:
            print("   ❌ 健康检查失败")
            
        # 测试登录接口
        print(f"2. 测试登录接口...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = requests.post('http://localhost:5000/api/auth/login', 
                               json=login_data, 
                               headers=headers)
        print(f"   状态码: {response.status_code}")
        print(f"   CORS头: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("   ✅ 登录测试成功")
                return True
            else:
                print("   ❌ 登录返回错误")
        else:
            print("   ❌ 登录请求失败")
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False
    
    return False

def main():
    print("=" * 60)
    print("🌐 CORS配置测试")
    print("=" * 60)
    
    # 测试常用端口
    test_ports = [3000, 3001, 3002, 3003]
    
    results = {}
    for port in test_ports:
        results[port] = test_cors_from_port(port)
    
    print(f"\n📊 测试结果汇总:")
    for port, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   端口 {port}: {status}")
    
    if all(results.values()):
        print(f"\n🎉 所有端口的CORS配置都正常！")
    else:
        failed_ports = [port for port, success in results.items() if not success]
        print(f"\n⚠️  以下端口的CORS配置需要检查: {failed_ports}")

if __name__ == '__main__':
    main()