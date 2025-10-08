#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试类别API
"""
import requests
import json

def test_categories():
    try:
        # 测试资产类别API
        print("=== 测试 /api/assets/categories ===")
        response = requests.get('http://localhost:5000/api/assets/categories')
        print(f'状态码: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'成功: {data.get("success")}')
            print(f'类别数量: {len(data.get("data", []))}')
            print('类别列表:')
            for item in data.get('data', []):
                print(f'- {item["name"]} (ID: {item["id"]})')
        else:
            print(f'请求失败: {response.text}')
        
        print("\n=== 测试 /api/categories ===\n注意：如果返回404，可能需要重启Flask服务器")
        response2 = requests.get('http://localhost:5000/api/categories')
        print(f'状态码: {response2.status_code}')
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f'成功: {data2.get("status") == "success"}')
            print(f'类别数量: {len(data2.get("data", []))}')
            print('类别列表:')
            for item in data2.get('data', []):
                print(f'- {item["name"]} (ID: {item["id"]}, 网络设备: {item.get("is_network_device", False)})')
        else:
            print(f'请求失败: {response2.text}')
            
    except Exception as e:
        print(f'测试失败: {e}')

if __name__ == '__main__':
    test_categories()