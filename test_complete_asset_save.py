#!/usr/bin/env python3
"""
测试资产创建时所有字段的保存情况
"""
import requests
import json

def test_complete_asset_creation():
    url = "http://localhost:5000/api/assets"
    
    # 包含前端表单所有字段的完整测试数据
    complete_data = {
        # 基本信息
        "asset_code": "",  # 留空让系统自动生成
        "name": "完整测试服务器",
        "brand": "Dell",
        "model": "PowerEdge R750",
        "category": "服务器",
        "specification": "双路Intel Xeon Gold 6330，128GB DDR4，4TB NVMe SSD",
        "serial_number": "FULL_TEST_001",
        
        # 位置信息
        "building_id": None,
        "floor_id": None, 
        "room_id": None,
        "location_detail": "数据中心A区第3机柜",
        
        # 采购信息
        "supplier": "戴尔科技集团",
        "purchase_date": "2024-01-15",
        "purchase_price": 85000.00,
        "purchase_order": "PO-2024-001",
        
        # 保修信息
        "warranty_start_date": "2024-01-15",
        "warranty_end_date": "2027-01-15", 
        "warranty_period": 36,
        
        # 使用信息
        "user_name": "张三",
        "user_department": "IT运维部",
        "deploy_date": "2024-01-20",
        "status": "在用",
        
        # 网络信息
        "ip_address": "192.168.1.200",
        "mac_address": "00:1B:44:11:3A:C8",
        "condition_rating": "优",
        
        # 备注信息
        "remark": "核心业务服务器，用于ERP系统部署，需要24x7监控"
    }
    
    print("=" * 80)
    print("🔍 测试完整资产创建功能")
    print("=" * 80)
    print("📊 提交的完整数据:")
    for key, value in complete_data.items():
        print(f"   {key}: {value}")
    
    try:
        # 发送POST请求
        response = requests.post(url, json=complete_data, timeout=10)
        
        print(f"\n📈 响应状态码: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ 资产创建成功!")
            print(f"📄 响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 获取创建的资产ID，然后查询完整信息验证
            asset_id = result['data']['id']
            return verify_saved_data(asset_id, complete_data)
        else:
            print(f"❌ 创建失败，状态码: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ 错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"❌ 响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def verify_saved_data(asset_id, original_data):
    """验证保存的数据是否完整"""
    print(f"\n🔍 验证已保存的资产数据 (ID: {asset_id})")
    
    # 通过资产列表API获取数据验证
    try:
        response = requests.get(f"http://localhost:5000/api/assets?page=1&pageSize=50", timeout=10)
        if response.status_code == 200:
            result = response.json()
            assets = result['data']['list']
            
            # 找到刚创建的资产
            created_asset = None
            for asset in assets:
                if asset['id'] == asset_id:
                    created_asset = asset
                    break
            
            if not created_asset:
                print(f"❌ 无法找到ID为{asset_id}的资产")
                return False
            
            print("📋 数据库中保存的字段:")
            saved_fields = []
            missing_fields = []
            
            # 检查每个字段是否正确保存
            for field, expected_value in original_data.items():
                if expected_value is None or expected_value == "":
                    continue  # 跳过空值
                
                saved_value = created_asset.get(field)
                if saved_value is not None and saved_value != "":
                    saved_fields.append(field)
                    print(f"   ✅ {field}: {saved_value}")
                else:
                    missing_fields.append(field)
                    print(f"   ❌ {field}: 未保存 (期望: {expected_value})")
            
            print(f"\n📊 保存统计:")
            print(f"   ✅ 成功保存的字段: {len(saved_fields)}")
            print(f"   ❌ 未保存的字段: {len(missing_fields)}")
            
            if missing_fields:
                print(f"\n⚠️  未保存的字段列表:")
                for field in missing_fields:
                    print(f"      - {field}: {original_data[field]}")
                return False
            else:
                print(f"\n🎉 所有字段都已正确保存!")
                return True
                
        else:
            print(f"❌ 获取资产列表失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False

def check_database_schema():
    """检查数据库表结构"""
    print("\n🔍 检查数据库表结构...")
    
    import sqlite3
    try:
        conn = sqlite3.connect('d:/kaifa/yuwei_python/backend/it_ops_system.db')
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(it_asset)')
        columns = cursor.fetchall()
        
        print("📋 数据库中it_asset表的字段:")
        db_fields = []
        for col in columns:
            field_name = col[1]
            field_type = col[2]
            is_required = col[3] == 1
            default_value = col[4]
            db_fields.append(field_name)
            print(f"   {field_name} ({field_type}) - 必填: {is_required}, 默认: {default_value}")
        
        conn.close()
        return db_fields
        
    except Exception as e:
        print(f"❌ 检查数据库结构失败: {e}")
        return []

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 资产创建完整性测试")
    print("=" * 80)
    
    # 1. 检查数据库结构
    db_fields = check_database_schema()
    
    # 2. 测试完整资产创建
    success = test_complete_asset_creation()
    
    print("\n" + "=" * 80)
    print("📊 测试结果总结:")
    if success:
        print("🎉 测试通过：所有填写的字段都能正确保存到数据库！")
    else:
        print("⚠️  测试发现问题：部分字段无法保存，需要修复后端代码。")
    print("=" * 80)