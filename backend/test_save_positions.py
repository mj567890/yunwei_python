#!/usr/bin/env python3
"""测试保存位置API的脚本"""

import requests
import json

def test_save_positions():
    """测试保存设备位置"""
    url = "http://localhost:5000/api/network/topology/positions"
    
    # 模拟前端发送的位置数据
    test_data = {
        "positions": [
            {"id": 1, "x": 100, "y": 150, "isLegacy": False},
            {"id": 2, "x": 200, "y": 250, "isLegacy": False},
            {"id": 3, "x": 300, "y": 350, "isLegacy": False}
        ]
    }
    
    print("🧪 测试保存位置API...")
    print(f"📡 发送数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.put(url, json=test_data, timeout=10)
        print(f"📬 响应状态码: {response.status_code}")
        print(f"📋 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 位置保存API测试成功！")
                return True
            else:
                print(f"❌ API返回错误: {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 请求失败: {e}")
        return False

def check_saved_positions():
    """检查保存的位置数据"""
    import sqlite3
    
    try:
        print("\n🔍 检查数据库中的位置数据...")
        conn = sqlite3.connect('it_ops_system.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, category, x_position, y_position 
            FROM it_asset 
            WHERE x_position IS NOT NULL AND y_position IS NOT NULL 
            LIMIT 10
        """)
        
        saved_positions = cursor.fetchall()
        
        print(f"📍 找到 {len(saved_positions)} 个有位置信息的设备:")
        for row in saved_positions:
            asset_id, name, category, x_pos, y_pos = row
            print(f"  ID:{asset_id} {name} ({category}) -> x:{x_pos} y:{y_pos}")
        
        conn.close()
        return len(saved_positions) > 0
        
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 保存位置功能测试")
    print("=" * 60)
    
    # 测试API
    api_success = test_save_positions()
    
    # 检查数据库
    db_success = check_saved_positions()
    
    print("\n" + "=" * 60)
    if api_success and db_success:
        print("🎉 测试通过！保存位置功能正常工作")
    else:
        print("❌ 测试失败！需要进一步调试")
    print("=" * 60)