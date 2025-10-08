#!/usr/bin/env python3
"""
测试资产创建功能的脚本
"""
import requests
import json

# 测试创建资产的API
def test_create_asset():
    url = "http://localhost:5000/api/assets"
    
    # 测试数据
    test_data = {
        "name": "测试服务器",
        "category": "服务器",
        "brand": "Dell",
        "model": "PowerEdge R740",
        "serial_number": "TEST001",
        "specification": "双CPU，64GB内存，2TB存储",
        "supplier": "戴尔科技",
        "purchase_date": "2024-01-15",
        "purchase_price": 45000.00,
        "warranty_start_date": "2024-01-15",
        "warranty_end_date": "2026-01-15",
        "warranty_period": 24,
        "user_name": "张三",
        "user_department": "IT部门",
        "deploy_date": "2024-01-20",
        "status": "在用",
        "ip_address": "192.168.1.100",
        "mac_address": "00:1B:44:11:3A:B7",
        "condition_rating": "优",
        "remark": "核心业务服务器"
    }
    
    print("🔄 测试资产创建API...")
    print(f"📤 请求URL: {url}")
    print(f"📊 测试数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        # 发送POST请求
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"📈 响应状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ 资产创建成功!")
            print(f"📄 响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ 创建失败，状态码: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ 错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"❌ 响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False

# 测试获取资产类别
def test_get_categories():
    url = "http://localhost:5000/api/assets/categories"
    
    print("\n🔄 测试获取资产类别API...")
    print(f"📤 请求URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📈 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取类别成功!")
            print(f"📄 类别数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ 获取失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False

# 测试后端健康检查
def test_backend_health():
    url = "http://localhost:5000/api/health"
    
    print("🔄 测试后端健康状态...")
    print(f"📤 请求URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"📈 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 后端服务正常!")
            print(f"📄 健康数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ 后端异常，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 IT运维系统 - 资产创建功能测试")
    print("=" * 70)
    
    # 执行测试
    health_ok = test_backend_health()
    
    if health_ok:
        categories_ok = test_get_categories()
        create_ok = test_create_asset()
        
        print("\n" + "=" * 70)
        print("📊 测试结果总结:")
        print(f"   🏥 后端健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
        print(f"   📁 获取资产类别: {'✅ 通过' if categories_ok else '❌ 失败'}")
        print(f"   ➕ 创建资产功能: {'✅ 通过' if create_ok else '❌ 失败'}")
        print("=" * 70)
        
        if health_ok and categories_ok and create_ok:
            print("🎉 所有测试通过！资产创建功能正常工作。")
        else:
            print("⚠️ 部分测试失败，请检查后端服务和前端配置。")
    else:
        print("\n❌ 后端服务不可用，无法进行其他测试。")
        print("💡 请确认后端服务已启动在 http://localhost:5000")