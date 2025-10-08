#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试网络拓扑API
"""
import requests
import json

def test_topology_api():
    print("=== 测试网络拓扑API ===")
    
    try:
        # 测试API调用
        response = requests.get('http://localhost:5000/api/network/topology')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            nodes = data.get('data', {}).get('nodes', [])
            edges = data.get('data', {}).get('edges', [])
            
            print(f"✅ API调用成功!")
            print(f"📊 节点数量: {len(nodes)}")
            print(f"🔗 边数量: {len(edges)}")
            
            if nodes:
                print("\n📋 前5个设备:")
                for i, node in enumerate(nodes[:5], 1):
                    name = node.get('name', 'Unknown')
                    node_type = node.get('type', 'Unknown')
                    node_id = node.get('id', 'Unknown')
                    ports = node.get('ports', [])
                    print(f"  {i}. {name} ({node_type}) - ID:{node_id} - 端口:{len(ports)}")
            else:
                print("⚠️  没有找到设备数据")
                
        else:
            print(f"❌ API调用失败")
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == '__main__':
    test_topology_api()