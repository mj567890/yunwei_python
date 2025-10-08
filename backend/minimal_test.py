#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据拓扑API测试
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/kaifa/yuwei_python/backend/it_ops_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 简化的数据模型
class Asset(db.Model):
    __tablename__ = 'it_asset'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    ip_address = db.Column(db.String(15))
    status = db.Column(db.String(20), default='在用')

class AssetPort(db.Model):
    __tablename__ = 'asset_port'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, nullable=False)
    port_name = db.Column(db.String(100), nullable=False)
    port_type = db.Column(db.String(20), nullable=False)
    port_status = db.Column(db.String(20), default='unused')
    is_connected = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

@app.route('/api/network/topology', methods=['GET'])
def get_topology():
    print("✅ 真实数据拓扑API被调用！")
    try:
        # 获取网络设备
        network_categories = ['交换机', '路由器', '防火墙', 'BRAS', '网关', '负载均衡器', '服务器', '工作站', '台式机', '笔记本']
        assets = Asset.query.filter(Asset.category.in_(network_categories)).all()
        print(f"📋 找到 {len(assets)} 个网络设备")
        
        nodes = []
        for asset in assets:
            print(f"  处理设备: {asset.name} ({asset.category})")
            # 获取设备端口
            ports = AssetPort.query.filter_by(asset_id=asset.id, is_deleted=False).all()
            print(f"    端口数量: {len(ports)}")
            
            node = {
                'id': asset.id,
                'name': asset.name,
                'type': asset.category,
                'ip': asset.ip_address,
                'status': asset.status or '正常',
                'x': 400 + (asset.id % 10) * 80,
                'y': 300 + (asset.id % 8) * 60,
                'ports': [{
                    'id': port.id,
                    'port_name': port.port_name,
                    'port_type': port.port_type,
                    'status': port.port_status,
                    'is_connected': port.is_connected
                } for port in ports],
                'device_category': 'topology' if asset.category in ['交换机', '路由器', '防火墙'] else 'terminal',
                'icon': get_device_icon(asset.category),
                'color': get_device_color(asset.category)
            }
            nodes.append(node)
        
        edges = []  # 暂时空连接
        
        topology_data = {
            'nodes': nodes,
            'edges': edges,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"✅ 成功返回: {len(nodes)}个节点, {len(edges)}个连接")
        return jsonify({
            'success': True,
            'data': topology_data,
            'message': '获取拓扑数据成功'
        })
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': '获取拓扑数据失败'
        }), 500

def get_device_icon(category):
    icon_map = {
        '交换机': '🔀',
        '路由器': '🌐',
        '防火墙': '🛡️',
        'BRAS': '📡',
        '网关': '🚪',
        '负载均衡器': '⚖️',
        '服务器': '🖥️',
        '工作站': '💻',
        '台式机': '🖱️',
        '笔记本': '💾'
    }
    return icon_map.get(category, '📦')

def get_device_color(category):
    color_map = {
        '交换机': '#409eff',
        '路由器': '#67c23a',
        '防火墙': '#e6a23c',
        'BRAS': '#f56c6c',
        '网关': '#909399',
        '负载均衡器': '#7c4dff',
        '服务器': '#606266',
        '工作站': '#909399',
        '台式机': '#c0c4cc',
        '笔记本': '#dcdfe6'
    }
    return color_map.get(category, '#909399')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("🚀 启动最小化测试服务器...")
    print("🌐 URL: http://localhost:5001/api/network/topology")
    app.run(host='0.0.0.0', port=5001, debug=True)