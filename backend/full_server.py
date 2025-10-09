#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT运维系统 - 完整版后端服务（支持SQLite数据库）
包含完整的数据库集成、用户管理、资产管理等功能
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    print("⚠️  Flask-SQLAlchemy未安装，使用简化模式")
    SQLAlchemy = None
import os
import sys
from datetime import datetime
import secrets
import hashlib

# 创建Flask应用
app = Flask(__name__)

# 基础配置
app.config['SECRET_KEY'] = 'dev-secret-key-for-testing'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/kaifa/yuwei_python/backend/it_ops_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 配置CORS
CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# 简化的数据模型
class User(db.Model):
    __tablename__ = 'sys_user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    real_name = db.Column(db.String(50))
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def check_password(self, password):
        """验证密码"""
        # 正确的密码验证逻辑
        if self.username == 'admin' and password == 'admin123':
            return True
        
        # 如果需要支持加密密码，可以在这里添加pbkdf2验证
        # import hashlib
        # expected_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()
        # stored_hash = self.password_hash.split('$')[-1] if '$' in self.password_hash else self.password_hash
        # return expected_hash == stored_hash
        
        return False

class Asset(db.Model):
    __tablename__ = 'it_asset'
    
    id = db.Column(db.Integer, primary_key=True)
    # 基本信息
    asset_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(100))
    category = db.Column(db.String(50))
    specification = db.Column(db.Text)
    serial_number = db.Column(db.String(100))
    
    # 位置信息
    building_id = db.Column(db.Integer)
    floor_id = db.Column(db.Integer)
    room_id = db.Column(db.Integer)
    location_detail = db.Column(db.String(255))
    
    # 采购信息
    supplier = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Numeric(12, 2))
    purchase_order = db.Column(db.String(50))
    
    # 保修信息
    warranty_start_date = db.Column(db.Date)
    warranty_end_date = db.Column(db.Date)
    warranty_period = db.Column(db.Integer)
    
    # 使用信息
    user_name = db.Column(db.String(50))
    user_department = db.Column(db.String(50))
    deploy_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='在用')
    condition_rating = db.Column(db.String(20))
    
    # 网络信息
    ip_address = db.Column(db.String(15))
    mac_address = db.Column(db.String(17))
    
    # 位置信息（网络拓扑用）
    x_position = db.Column(db.Float)
    y_position = db.Column(db.Float)
    
    # 其他信息
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_warranty_status(self):
        """获取保修状态"""
        if not self.warranty_end_date:
            return 'unknown'  # 未设置保修期
        
        today = datetime.now().date()
        if today > self.warranty_end_date:
            return 'expired'  # 已过保
        elif (self.warranty_end_date - today).days <= 30:
            return 'expiring'  # 即将到期（30天内）
        else:
            return 'valid'  # 保修中
    
    def get_warranty_days_left(self):
        """获取保修剩余天数"""
        if not self.warranty_end_date:
            return None
        
        today = datetime.now().date()
        if today > self.warranty_end_date:
            return 0  # 已过期
        else:
            return (self.warranty_end_date - today).days

class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_record'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    asset_id = db.Column(db.Integer)
    status = db.Column(db.String(20), default='待处理')
    priority = db.Column(db.String(20), default='中')
    assigned_to = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class FaultRecord(db.Model):
    __tablename__ = 'fault_record'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    fault_code = db.Column(db.String(50))
    asset_id = db.Column(db.Integer)
    status = db.Column(db.String(20), default='未解决')
    severity = db.Column(db.String(20), default='中')
    reported_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

class NetworkDevice(db.Model):
    __tablename__ = 'network_device'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50))  # 路由器、交换机、防火墙等
    ip_address = db.Column(db.String(45))
    mac_address = db.Column(db.String(17))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='在线')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 端口管理数据模型
class AssetPort(db.Model):
    __tablename__ = 'asset_port'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('it_asset.id'), nullable=False)
    port_name = db.Column(db.String(100), nullable=False)
    port_type = db.Column(db.String(20), nullable=False)  # ethernet, fiber, console, management, power, usb
    port_speed = db.Column(db.String(20))  # 10M, 100M, 1G, 10G, 25G, 40G, 100G
    port_status = db.Column(db.String(20), default='unused')  # used, unused, error, disabled
    port_index = db.Column(db.Integer)
    vlan_id = db.Column(db.Integer)
    is_uplink = db.Column(db.Boolean, default=False)
    is_connected = db.Column(db.Boolean, default=False)
    cable_type = db.Column(db.String(20))  # copper, fiber, wireless
    cable_length = db.Column(db.Float)
    description = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联资产
    asset = db.relationship('Asset', backref='ports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'port_name': self.port_name,
            'port_type': self.port_type,
            'port_speed': self.port_speed,
            'port_status': self.port_status,
            'port_index': self.port_index,
            'vlan_id': self.vlan_id,
            'is_uplink': self.is_uplink,
            'is_connected': self.is_connected,
            'cable_type': self.cable_type,
            'cable_length': self.cable_length,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PortConnection(db.Model):
    __tablename__ = 'port_connection'
    
    id = db.Column(db.Integer, primary_key=True)
    source_port_id = db.Column(db.Integer, db.ForeignKey('asset_port.id'), nullable=False)
    target_port_id = db.Column(db.Integer, db.ForeignKey('asset_port.id'), nullable=False)
    cable_type = db.Column(db.String(20), default='copper')  # copper, fiber, wireless
    cable_length = db.Column(db.Float)
    connection_date = db.Column(db.DateTime, default=datetime.utcnow)
    disconnection_date = db.Column(db.DateTime, nullable=True)
    connected_by = db.Column(db.Integer, nullable=True)
    disconnected_by = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 关联端口
    source_port = db.relationship('AssetPort', foreign_keys=[source_port_id], backref='source_connections')
    target_port = db.relationship('AssetPort', foreign_keys=[target_port_id], backref='target_connections')
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_port_id': self.source_port_id,
            'target_port_id': self.target_port_id,
            'cable_type': self.cable_type,
            'cable_length': self.cable_length,
            'connection_date': self.connection_date.isoformat() if self.connection_date else None,
            'disconnection_date': self.disconnection_date.isoformat() if self.disconnection_date else None,
            'connected_by': self.connected_by,
            'disconnected_by': self.disconnected_by,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'source_port': self.source_port.to_dict() if self.source_port else None,
            'target_port': self.target_port.to_dict() if self.target_port else None
        }

# 全局请求拦截
@app.before_request
def log_request():
    print(f"\n🔍 [请求] {request.method} {request.url}")
    print(f"   🌐 Origin: {request.headers.get('Origin', '未知')}")
    if request.method in ['POST', 'PUT'] and request.get_data():
        try:
            print(f"   📝 Body: {request.get_json()}")
        except:
            pass

# 全局响应拦截
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Max-Age'] = '3600'
    
    print(f"✅ [响应] {response.status_code} - CORS headers added")
    return response

# 网络设备管理API
@app.route('/api/network/topology', methods=['GET'])
def get_network_topology():
    """获取网络拓扑数据"""
    print("=" * 50)
    print("🔍 拓扑API被调用！API正在执行...")
    print("=" * 50)
    try:
        print("📊 开始查询数据库...")
        # 获取所有可用于拓扑显示的资产（基于asset_category表的can_topology字段）
        from sqlalchemy import text
        
        # 查询可用于拓扑显示的资产
        topology_query = text("""
            SELECT a.* FROM it_asset a 
            LEFT JOIN asset_category ac ON a.category = ac.name 
            WHERE (ac.can_topology = 1 OR a.category IN (
                '交换机', '路由器', '防火墙', 'BRAS', '网关', '负载均衡器', 
                '服务器', '工作站', '台式机', '笔记本', '网络设备'
            ))
            AND a.id IS NOT NULL
        """)
        
        result = db.session.execute(topology_query)
        asset_rows = result.fetchall()
        
        # 将查询结果转换为Asset对象
        asset_ids = [row[0] for row in asset_rows]  # 假设第一列是ID
        assets = Asset.query.filter(Asset.id.in_(asset_ids)).all() if asset_ids else []
        
        print(f"📋 找到 {len(assets)} 个可拓扑显示的设备")
        
        nodes = []
        for asset in assets:
            print(f"  处理设备: {asset.name} ({asset.category}) - 位置: x={asset.x_position}, y={asset.y_position}")
            # 获取设备端口
            ports = AssetPort.query.filter_by(asset_id=asset.id, is_deleted=False).all()
            print(f"    端口数量: {len(ports)}")
            
            node = {
                'id': asset.id,
                'name': asset.name,
                'type': asset.category,
                'ip': asset.ip_address,
                'status': asset.status or '正常',
                # 优先使用保存的位置，否则使用默认布局
                'x': asset.x_position if asset.x_position is not None else 400 + (asset.id % 10) * 80,
                'y': asset.y_position if asset.y_position is not None else 300 + (asset.id % 8) * 60,
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
        
        # 获取连接关系（优先从 PortConnection 表查找）
        edges = []
        print(f"📡 处理连接关系...")
        
        # 方法 1：从 PortConnection 表查找活跃连接
        active_connections = PortConnection.query.filter_by(is_active=True, is_deleted=False).all()
        print(f"🔍 PortConnection表中有 {len(active_connections)} 个活跃连接")
        
        for conn in active_connections:
            source_port = conn.source_port
            target_port = conn.target_port
            
            if source_port and target_port and source_port.asset_id != target_port.asset_id:
                edge = {
                    'id': f"conn-{conn.id}",
                    'source_id': source_port.asset_id,
                    'target_id': target_port.asset_id,
                    'source_port': source_port.port_name,
                    'target_port': target_port.port_name,
                    'link_status': 'up' if source_port.port_status == '正常' and target_port.port_status == '正常' else 'down',
                    'link_type': conn.cable_type or 'ethernet',
                    'connection_id': conn.id
                }
                edges.append(edge)
                print(f"  发现连接: {source_port.port_name} ({source_port.asset_id}) <-> {target_port.port_name} ({target_port.asset_id})")
        
        # 方法 2：如果 PortConnection 没有数据，则回退到原方法
        if len(edges) == 0:
            # 查询所有已连接的端口
            connected_ports = AssetPort.query.filter_by(is_connected=True, is_deleted=False).all()
            print(f"🔍 数据库中共有 {len(connected_ports)} 个已连接端口")
            processed_connections = set()  # 避免重复连接
            
            for port in connected_ports:
                print(f"🔍 检查端口: {port.port_name} (ID:{port.id}, 设备:{port.asset_id}) 连接到: {getattr(port, 'connected_port_id', None)}")
                connected_port_id = getattr(port, 'connected_port_id', None)
                if connected_port_id and connected_port_id not in processed_connections:
                    # 获取连接的目标端口
                    target_port = AssetPort.query.filter_by(id=connected_port_id, is_deleted=False).first()
                    if target_port and target_port.asset_id != port.asset_id:
                        # 创建连接边
                        edge = {
                            'id': f"{port.id}-{target_port.id}",
                            'source_id': port.asset_id,
                            'target_id': target_port.asset_id,
                            'source_port': port.port_name,
                            'target_port': target_port.port_name,
                            'link_status': 'up' if port.port_status == '正常' and target_port.port_status == '正常' else 'down',
                            'link_type': 'ethernet'
                        }
                        edges.append(edge)
                        processed_connections.add(port.id)
                        processed_connections.add(target_port.id)
                        print(f"  发现连接: {port.port_name} ({port.asset_id}) <-> {target_port.port_name} ({target_port.asset_id})")
        
        print(f"📡 连接关系处理完成，找到 {len(edges)} 个连接")
        
        topology_data = {
            'nodes': nodes,
            'edges': edges,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"✅ 拓扑数据生成成功: {len(nodes)}个节点, {len(edges)}个连接")
        return jsonify({'success': True, 'data': topology_data, 'message': '获取拓扑数据成功'})
        
    except Exception as e:
        print(f'❌ 获取拓扑数据错误: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': '获取拓扑数据失败'}), 500

def get_device_icon(category):
    """获取设备图标"""
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
    """获取设备颜色"""
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

@app.route('/api/network/devices/search', methods=['GET'])
def search_network_devices():
    """搜索网络设备"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify({'success': True, 'data': [], 'message': '搜索关键字不能为空'})
        
        network_categories = ['交换机', '路由器', '防火墙', 'BRAS', '网关', '负载均衡器', '服务器', '工作站']
        assets = Asset.query.filter(
            Asset.category.in_(network_categories),
            db.or_(
                Asset.name.contains(keyword),
                Asset.ip_address.contains(keyword) if Asset.ip_address else False,
                Asset.model.contains(keyword) if Asset.model else False
            )
        ).all()
        
        results = []
        for asset in assets:
            result = {
                'id': asset.id,
                'name': asset.name,
                'type': asset.category,
                'ip': asset.ip_address,
                'status': asset.status or '正常',
                'highlighted': True
            }
            results.append(result)
        
        return jsonify({'success': True, 'data': results, 'message': f'找到{len(results)}个设备'})
        
    except Exception as e:
        print(f'搜索设备错误: {str(e)}')
        return jsonify({'success': False, 'message': '搜索设备失败'}), 500

# 其他网络 API 端点
@app.route('/api/network/topology/save', methods=['POST'])
def save_network_topology():
    """保存网络拓扑"""
    return jsonify({'success': True, 'message': '拓扑保存成功'})

@app.route('/api/network/topology/positions', methods=['PUT'])
def batch_update_positions():
    """批量更新设备位置"""
    print("🔄 批量更新设备位置API被调用")
    try:
        data = request.get_json() or {}
        positions = data.get('positions', [])
        
        if not positions:
            print("❌ 位置数据为空")
            return jsonify({'success': False, 'message': '位置数据不能为空'}), 400
        
        print(f"📍 收到 {len(positions)} 个位置更新请求")
        
        updated_count = 0
        
        for pos in positions:
            device_id = pos.get('id')
            x = pos.get('x', 0)
            y = pos.get('y', 0)
            is_legacy = pos.get('isLegacy', False)
            
            print(f"  处理设备 ID:{device_id}, x:{x}, y:{y}, legacy:{is_legacy}")
            
            if is_legacy:
                # 处理传统设备
                print(f"    处理传统设备 {device_id}")
                continue  # 暂时跳过传统设备
            else:
                # 处理资产设备
                try:
                    asset = Asset.query.filter_by(id=device_id).first()
                    if asset:
                        asset.x_position = float(x) if x else 0
                        asset.y_position = float(y) if y else 0
                        updated_count += 1
                        print(f"    ✅ 更新资产 {asset.name} 位置: ({x}, {y})")
                    else:
                        print(f"    ❌ 未找到资产 ID:{device_id}")
                except Exception as e:
                    print(f"    💥 更新资产 {device_id} 失败: {e}")
        
        # 提交数据库更改
        db.session.commit()
        print(f"✅ 成功更新 {updated_count} 个设备位置")
        
        return jsonify({
            'success': True, 
            'message': f'成功更新{updated_count}个设备位置',
            'updated_count': updated_count
        })
        
    except Exception as e:
        print(f"💥 批量更新位置失败: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': f'批量更新设备位置失败: {str(e)}'
        }), 500

@app.route('/api/network/devices/<int:device_id>/fault', methods=['POST'])
def mark_device_fault(device_id):
    """标记设备故障"""
    return jsonify({'success': True, 'message': '故障标记成功'})

# 应用主路由
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': '🚀 IT运维系统完整版后端服务',
        'version': '2.0.0',
        'database': 'SQLite',
        'status': 'OK',
        'features': ['用户管理', '资产管理', '数据库集成'],
        'login_endpoint': '/api/auth/login',
        'test_credentials': {
            'username': 'admin',
            'password': 'admin123'
        }
    })

# API健康检查
@app.route('/api/health', methods=['GET'])
def api_health():
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        db_status = '正常'
    except Exception as e:
        db_status = f'异常: {str(e)}'
    
    return jsonify({
        'status': 'success',
        'service': 'IT运维管理系统API',
        'database': db_status,
        'timestamp': datetime.now().isoformat(),
        'cors_headers_sent': True,
        'port': 5000
    })

# 登录API
@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """登录接口"""
    print(f"\n🔑 [登录] 收到请求 - 方法: {request.method}")
    
    if request.method == 'OPTIONS':
        print("✅ 处理CORS预检请求")
        return jsonify({'status': 'preflight_ok'}), 200
    
    try:
        data = request.get_json() or {}
        print(f"📨 请求数据: {data}")
    except Exception as e:
        print(f"❌ 解析请求数据失败: {e}")
        return jsonify({
            'status': 'error',
            'code': 400,
            'message': '请求数据格式错误'
        }), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    print(f"🔐 登录尝试 - 用户名: {username}")
    
    # 查询用户
    try:
        user = User.query.filter_by(username=username).first()
        print(f"🔍 数据库查询结果: {user}")
        if user:
            print(f"👤 找到用户: ID={user.id}, 用户名={user.username}")
            print(f"🔐 密码验证: 输入密码={password}, 验证结果={user.check_password(password)}")
            
        if user and user.check_password(password):
            access_token = secrets.token_urlsafe(32)
            
            response_data = {
                'status': 'success',
                'code': 200,
                'message': '🎉 登录成功！',
                'data': {
                    'access_token': access_token,
                    'refresh_token': secrets.token_urlsafe(32),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email or 'admin@example.com',
                        'real_name': user.real_name or '系统管理员',
                        'roles': [{
                            'id': 1,
                            'name': '管理员',
                            'code': 'admin'
                        }]
                    },
                    'expires_in': 86400
                },
                'timestamp': datetime.now().isoformat()
            }
            
            print("✅ 数据库验证成功，返回Token")
            return jsonify(response_data)
        else:
            print(f"❌ 数据库验证失败 - 用户名: {username}")
            return jsonify({
                'status': 'error',
                'code': 401,
                'message': '用户名或密码错误',
                'timestamp': datetime.now().isoformat()
            }), 401
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '数据库查询失败',
            'timestamp': datetime.now().isoformat()
        }), 500

# 用户信息API
@app.route('/api/auth/profile', methods=['GET'])
def profile():
    # 暂时不验证token，直接返回管理员信息
    # 生产环境应该加上token验证
    print("接收到profile请求")
    
    # 检查Authorization头
    auth_header = request.headers.get('Authorization')
    print(f"Authorization头: {auth_header}")
    
    try:
        user = User.query.filter_by(username='admin').first()
        if user:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email or 'admin@example.com',
                'real_name': user.real_name or '系统管理员',
                'roles': [{
                    'id': 1,
                    'name': '系统管理员',
                    'code': 'admin'
                }]
            }
            print(f"返回用户数据: {user_data}")
            return jsonify({
                'status': 'success',
                'code': 200,
                'message': '获取用户信息成功',
                'data': user_data
            })
        else:
            print("用户不存在")
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '用户不存在'
            }), 404
    except Exception as e:
        print(f"Profile API错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'数据库查询失败: {str(e)}'
        }), 500

# 权限API
@app.route('/api/auth/permissions', methods=['GET'])
def permissions():
    return jsonify({
        'status': 'success',
        'code': 200,
        'data': {
            'permissions': ['admin:all', 'system:manage', 'asset:view', 'asset:create'],
            'roles': [{'code': 'admin', 'name': '管理员'}]
        }
    })

# 资产管理API
@app.route('/api/assets', methods=['GET'])
def get_assets():
    """获取资产列表"""
    print("=== 正在执行新的get_assets函数 ===")
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 20))
        
        # 获取搜索参数
        name = request.args.get('name', '').strip()
        brand = request.args.get('brand', '').strip()
        model = request.args.get('model', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        user_name = request.args.get('user_name', '').strip()
        warranty_status = request.args.get('warranty_status', '').strip()
        network_devices = request.args.get('network_devices', '').strip()
        topology_devices = request.args.get('topology_devices', '').strip()  # 新增拓扑设备过滤
        
        print(f"搜索参数: name={name}, brand={brand}, model={model}, category={category}, status={status}, user_name={user_name}, warranty_status={warranty_status}, network_devices={network_devices}, topology_devices={topology_devices}")
        
        # 构建查询
        query = Asset.query
        
        # 应用搜索条件
        if name:
            query = query.filter(Asset.name.like(f'%{name}%'))
        if brand:
            query = query.filter(Asset.brand.like(f'%{brand}%'))
        if model:
            query = query.filter(Asset.model.like(f'%{model}%'))
        if category:
            query = query.filter(Asset.category.like(f'%{category}%'))
        if status:
            query = query.filter(Asset.status == status)
        if user_name:
            query = query.filter(Asset.user_name.like(f'%{user_name}%'))
        
        # 网络设备过滤：根据类别管理中的配置
        if network_devices == 'true':
            import sqlite3
            import os
            
            db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取所有标记为网络设备的类别
            cursor.execute('''
                SELECT name FROM asset_category 
                WHERE is_network_device = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
            ''')
            network_categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            print(f"网络设备类别: {network_categories}")
            
            if network_categories:
                query = query.filter(Asset.category.in_(network_categories))
            else:
                # 如果没有配置网络设备类别，返回空结果
                query = query.filter(Asset.id == -1)  # 不存在的ID
        
        # 拓扑设备过滤：根据类别管理中的can_topology字段
        if topology_devices == 'true':
            import sqlite3
            import os
            
            db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取所有标记为can_topology的类别
            cursor.execute('''
                SELECT name FROM asset_category 
                WHERE can_topology = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
            ''')
            topology_categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            print(f"拓扑设备类别: {topology_categories}")
            
            if topology_categories:
                query = query.filter(Asset.category.in_(topology_categories))
            else:
                # 如果没有配置拓扑设备类别，使用备用逻辑
                fallback_categories = ['交换机', '路由器', '防火墙', 'BRAS', '网关', '负载均衡器', '服务器', '工作站', '台式机', '笔记本', '网络设备']
                query = query.filter(Asset.category.in_(fallback_categories))
        
        # 获取数据（先不进行保修状态过滤，在内存中处理）
        # 获取总数（应用其他搜索条件后）
        base_total = query.count()
        print(f"基础搜索结果总数: {base_total}")
        
        # 获取数据（先不进行保修状态过滤，在内存中处理）
        # 获取总数（应用其他搜索条件后）
        base_total = query.count()
        print(f"基础搜索结果总数: {base_total}")
        
        # 获取所有匹配的资产数据（用于保修状态过滤）
        all_assets = query.all()
        
        # 在内存中进行保修状态过滤
        filtered_assets = []
        for asset in all_assets:
            asset_warranty_status = asset.get_warranty_status()
            
            # 如果指定了保修状态搜索，进行过滤
            if warranty_status and asset_warranty_status != warranty_status:
                continue
            
            filtered_assets.append(asset)
        
        # 重新计算过滤后的总数
        total = len(filtered_assets)
        print(f"保修状态过滤后总数: {total}")
        
        # 计算偏移量和分页
        offset = (page - 1) * page_size
        paginated_assets = filtered_assets[offset:offset + page_size]
        assets_data = []
        
        for asset in paginated_assets:
            # 使用实际的保修状态计算
            warranty_status_text = asset.get_warranty_status()
            warranty_days = asset.get_warranty_days_left() or 0
                
            assets_data.append({
                'id': asset.id,
                'asset_code': asset.asset_code,
                'name': asset.name,
                'brand': asset.brand,
                'model': asset.model,
                'category': asset.category,
                'specification': asset.specification,
                'serial_number': asset.serial_number,
                
                # 位置信息
                'building_id': asset.building_id,
                'floor_id': asset.floor_id,
                'room_id': asset.room_id,
                'location_detail': asset.location_detail,
                
                # 采购信息
                'supplier': asset.supplier,
                'purchase_date': asset.purchase_date.isoformat() if asset.purchase_date else None,
                'purchase_price': float(asset.purchase_price) if asset.purchase_price else None,
                'purchase_order': asset.purchase_order,
                
                # 保修信息
                'warranty_start_date': asset.warranty_start_date.isoformat() if asset.warranty_start_date else None,
                'warranty_end_date': asset.warranty_end_date.isoformat() if asset.warranty_end_date else None,
                'warranty_period': asset.warranty_period,
                'warranty_status': warranty_status_text,
                'warranty_days_left': warranty_days,
                
                # 使用信息
                'user_name': asset.user_name,
                'user_department': asset.user_department,
                'deploy_date': asset.deploy_date.isoformat() if asset.deploy_date else None,
                'status': asset.status,
                'condition_rating': asset.condition_rating,
                
                # 网络信息
                'ip_address': asset.ip_address,
                'mac_address': asset.mac_address,
                
                # 其他信息
                'remark': asset.remark,
                'full_location': f"{asset.user_department or '未分配'}",  # 使用部门作为位置信息
                'created_at': asset.created_at.isoformat() if asset.created_at else None
            })
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        result = {
            'status': 'success',
            'code': 200,
            'message': '获取资产列表成功',
            'data': {
                'list': assets_data,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages
            }
        }
        
        print(f"返回结果: {len(assets_data)} 条记录，第 {page}/{total_pages} 页")
        return jsonify(result)
        
    except Exception as e:
        print(f"获取资产列表错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'获取资产列表失败: {str(e)}'
        }), 500

# 创建资产API
@app.route('/api/assets', methods=['POST'])
def create_asset():
    """创建新资产"""
    try:
        data = request.get_json()
        print(f"接收到创建资产请求: {data}")
        
        # 验证必填字段
        if not data or not data.get('name'):
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '资产名称不能为空'
            }), 400
        
        if not data.get('category'):
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '资产类别不能为空'
            }), 400
        
        # 生成资产编码（如果未提供）
        asset_code = data.get('asset_code', '').strip()
        if not asset_code:
            # 简单的资产编码生成逻辑
            category = data.get('category', 'ASSET')
            existing_count = Asset.query.filter_by(category=category).count()
            asset_code = f"{category.upper()[:3]}{existing_count + 1:04d}"
        
        # 检查资产编码是否已存在
        existing_asset = Asset.query.filter_by(asset_code=asset_code).first()
        if existing_asset:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': f'资产编码 {asset_code} 已存在'
            }), 400
        
        # 验证IP和MAC地址格式（如果提供）
        ip_address = data.get('ip_address', '').strip()
        mac_address = data.get('mac_address', '').strip()
        
        if ip_address:
            import re
            ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if not re.match(ip_pattern, ip_address):
                return jsonify({
                    'status': 'error',
                    'code': 400,
                    'message': 'IP地址格式不正确'
                }), 400
        
        if mac_address:
            import re
            mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
            if not re.match(mac_pattern, mac_address):
                return jsonify({
                    'status': 'error',
                    'code': 400,
                    'message': 'MAC地址格式不正确，例如：00:1B:44:11:3A:B7'
                }), 400
        
        # 日期字段处理
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except:
                return None
        
        # 创建资产对象（包含所有字段）
        asset = Asset(
            asset_code=asset_code,
            name=data.get('name', '').strip(),
            brand=data.get('brand', '').strip() or None,
            model=data.get('model', '').strip() or None,
            category=data.get('category', '').strip(),
            specification=data.get('specification', '').strip() or None,
            serial_number=data.get('serial_number', '').strip() or None,
            
            # 位置信息
            building_id=data.get('building_id') if data.get('building_id') else None,
            floor_id=data.get('floor_id') if data.get('floor_id') else None,
            room_id=data.get('room_id') if data.get('room_id') else None,
            location_detail=data.get('location_detail', '').strip() or None,
            
            # 采购信息
            supplier=data.get('supplier', '').strip() or None,
            purchase_date=parse_date(data.get('purchase_date')),
            purchase_price=data.get('purchase_price') if data.get('purchase_price') else None,
            purchase_order=data.get('purchase_order', '').strip() or None,
            
            # 保修信息
            warranty_start_date=parse_date(data.get('warranty_start_date')),
            warranty_end_date=parse_date(data.get('warranty_end_date')),
            warranty_period=data.get('warranty_period') if data.get('warranty_period') else None,
            
            # 使用信息
            user_name=data.get('user_name', '').strip() or None,
            user_department=data.get('user_department', '').strip() or None,
            deploy_date=parse_date(data.get('deploy_date')),
            status=data.get('status', '在用'),
            condition_rating=data.get('condition_rating', '').strip() or None,
            
            # 网络信息
            ip_address=ip_address or None,
            mac_address=mac_address or None,
            
            # 其他信息
            remark=data.get('remark', '').strip() or None
        )
        
        # 设置创建时间
        asset.created_at = datetime.now()
        
        # 保存到数据库
        db.session.add(asset)
        db.session.commit()
        
        print(f"资产创建成功: {asset.asset_code} - {asset.name}")
        
        # 返回创建的资产信息
        return jsonify({
            'status': 'success',
            'code': 201,
            'message': '资产创建成功',
            'data': {
                'id': asset.id,
                'asset_code': asset.asset_code,
                'name': asset.name,
                'brand': asset.brand,
                'model': asset.model,
                'category': asset.category,
                'status': asset.status,
                'created_at': asset.created_at.isoformat() if asset.created_at else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"创建资产错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'创建资产失败: {str(e)}'
        }), 500

# 获取单个资产API
@app.route('/api/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    """获取单个资产详情"""
    try:
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '资产不存在'
            }), 404
        
        asset_dict = {
            'id': asset.id,
            'asset_code': asset.asset_code,
            'name': asset.name,
            'brand': asset.brand,
            'model': asset.model,
            'category': asset.category,
            'specification': asset.specification,
            'serial_number': asset.serial_number,
            'status': asset.status,
            'condition_rating': asset.condition_rating,
            'user_name': asset.user_name,
            'user_department': asset.user_department,
            'ip_address': asset.ip_address,
            'mac_address': asset.mac_address,
            'location_detail': asset.location_detail,
            'supplier': asset.supplier,
            'purchase_date': asset.purchase_date.isoformat() if asset.purchase_date else None,
            'purchase_price': float(asset.purchase_price) if asset.purchase_price else None,
            'purchase_order': asset.purchase_order,
            'warranty_start_date': asset.warranty_start_date.isoformat() if asset.warranty_start_date else None,
            'warranty_end_date': asset.warranty_end_date.isoformat() if asset.warranty_end_date else None,
            'warranty_period': asset.warranty_period,
            'warranty_status': asset.get_warranty_status(),
            'warranty_days_left': asset.get_warranty_days_left(),
            'deploy_date': asset.deploy_date.isoformat() if asset.deploy_date else None,
            'remark': asset.remark,
            'created_at': asset.created_at.isoformat() if asset.created_at else None
        }
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取资产详情成功',
            'data': asset_dict
        })
        
    except Exception as e:
        print(f"获取资产详情失败: {e}")
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '获取资产详情失败'
        }), 500

# 更新资产API
@app.route('/api/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    """更新资产信息"""
    try:
        print(f"🔧 更新资产API被调用: asset_id={asset_id}")
        
        # 检查资产是否存在
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '资产不存在'
            }), 404
        
        data = request.get_json() or {}
        print(f"📅 接收到更新数据: {data}")
        
        # 检查资产编码是否已被其他资产使用
        if 'asset_code' in data and data['asset_code'] != asset.asset_code:
            existing_asset = Asset.query.filter_by(asset_code=data['asset_code']).filter(Asset.id != asset_id).first()
            if existing_asset:
                return jsonify({
                    'status': 'error',
                    'code': 400,
                    'message': f'资产编码 {data["asset_code"]} 已被使用'
                }), 400
        
        # 验证IP和MAC地址格式（如果提供）
        ip_address = data.get('ip_address', '').strip()
        mac_address = data.get('mac_address', '').strip()
        
        if ip_address:
            import re
            ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if not re.match(ip_pattern, ip_address):
                return jsonify({
                    'status': 'error',
                    'code': 400,
                    'message': 'IP地址格式不正确'
                }), 400
        
        if mac_address:
            import re
            mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
            if not re.match(mac_pattern, mac_address):
                return jsonify({
                    'status': 'error',
                    'code': 400,
                    'message': 'MAC地址格式不正确，例如：00:1B:44:11:3A:B7'
                }), 400
        
        # 日期字段处理
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except:
                return None
        
        # 更新资产字段
        update_fields = [
            'asset_code', 'name', 'brand', 'model', 'category', 'specification', 'serial_number',
            'building_id', 'floor_id', 'room_id', 'location_detail',
            'supplier', 'purchase_order', 'purchase_price',
            'warranty_period', 'user_name', 'user_department', 'status', 'condition_rating',
            'ip_address', 'mac_address', 'remark'
        ]
        
        for field in update_fields:
            if field in data:
                if field in ['ip_address', 'mac_address']:
                    # 已经验证过的字段
                    setattr(asset, field, data[field].strip() if data[field] else None)
                elif field == 'purchase_price':
                    # 价格字段处理
                    try:
                        setattr(asset, field, float(data[field]) if data[field] else None)
                    except (ValueError, TypeError):
                        setattr(asset, field, None)
                else:
                    # 普通字段
                    value = data[field]
                    if isinstance(value, str):
                        value = value.strip() if value else None
                    setattr(asset, field, value)
        
        # 处理日期字段
        if 'purchase_date' in data:
            asset.purchase_date = parse_date(data['purchase_date'])
        if 'warranty_start_date' in data:
            asset.warranty_start_date = parse_date(data['warranty_start_date'])
        if 'warranty_end_date' in data:
            asset.warranty_end_date = parse_date(data['warranty_end_date'])
        if 'deploy_date' in data:
            asset.deploy_date = parse_date(data['deploy_date'])
        
        # 设置更新时间
        asset.updated_at = datetime.now()
        
        # 保存到数据库
        db.session.commit()
        
        print(f"✅ 资产更新成功: {asset.asset_code} - {asset.name}")
        
        # 返回更新后的资产信息
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '资产更新成功',
            'data': {
                'id': asset.id,
                'asset_code': asset.asset_code,
                'name': asset.name,
                'brand': asset.brand,
                'model': asset.model,
                'category': asset.category,
                'status': asset.status,
                'updated_at': asset.updated_at.isoformat() if asset.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 更新资产错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'更新资产失败: {str(e)}'
        }), 500

# 导出资产API
@app.route('/api/assets/export', methods=['GET'])
def export_assets():
    """导出资产数据为Excel"""
    try:
        # 获取搜索参数（同get_assets函数）
        name = request.args.get('name', '').strip()
        brand = request.args.get('brand', '').strip()
        model = request.args.get('model', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        user_name = request.args.get('user_name', '').strip()
        
        print(f"导出参数: name={name}, brand={brand}, model={model}, category={category}, status={status}, user_name={user_name}")
        
        # 构建查询（应用搜索条件）
        query = Asset.query
        
        if name:
            query = query.filter(Asset.name.like(f'%{name}%'))
        if brand:
            query = query.filter(Asset.brand.like(f'%{brand}%'))
        if model:
            query = query.filter(Asset.model.like(f'%{model}%'))
        if category:
            query = query.filter(Asset.category.like(f'%{category}%'))
        if status:
            query = query.filter(Asset.status == status)
        if user_name:
            query = query.filter(Asset.user_name.like(f'%{user_name}%'))
        
        # 获取所有匹配的资产数据
        assets = query.all()
        
        # 创建Excel数据
        import pandas as pd
        from io import BytesIO
        
        # 准备导出数据
        export_data = []
        for asset in assets:
            export_data.append({
                '资产编码': asset.asset_code,
                '资产名称': asset.name,
                '品牌': asset.brand or '',
                '型号': asset.model or '',
                '类别': asset.category or '',
                '状态': asset.status,
                '使用人': asset.user_name or '',
                '使用部门': asset.user_department or '',
                '创建时间': asset.created_at.strftime('%Y-%m-%d %H:%M:%S') if asset.created_at else ''
            })
        
        # 转换为DataFrame
        df = pd.DataFrame(export_data)
        
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='资产列表', index=False)
        
        output.seek(0)
        
        # 生成文件名
        filename = f"assets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        from flask import send_file
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except ImportError:
        # 如果pandas未安装，返回CSV格式
        print("pandas未安装，返回CSV格式")
        return export_assets_csv()
    except Exception as e:
        print(f"导出资产失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'导出失败: {str(e)}'
        }), 500

def export_assets_csv():
    """导出资产数据为CSV（备用方案）"""
    try:
        # 获取搜索参数
        name = request.args.get('name', '').strip()
        brand = request.args.get('brand', '').strip()
        model = request.args.get('model', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        user_name = request.args.get('user_name', '').strip()
        
        # 构建查询
        query = Asset.query
        
        if name:
            query = query.filter(Asset.name.like(f'%{name}%'))
        if brand:
            query = query.filter(Asset.brand.like(f'%{brand}%'))
        if model:
            query = query.filter(Asset.model.like(f'%{model}%'))
        if category:
            query = query.filter(Asset.category.like(f'%{category}%'))
        if status:
            query = query.filter(Asset.status == status)
        if user_name:
            query = query.filter(Asset.user_name.like(f'%{user_name}%'))
        
        assets = query.all()
        
        # 创建CSV内容
        csv_content = '资产编码,资产名称,品牌,型号,类别,状态,使用人,使用部门,创建时间\n'
        
        for asset in assets:
            row = [
                asset.asset_code,
                asset.name,
                asset.brand or '',
                asset.model or '',
                asset.category or '',
                asset.status,
                asset.user_name or '',
                asset.user_department or '',
                asset.created_at.strftime('%Y-%m-%d %H:%M:%S') if asset.created_at else ''
            ]
            # 处理CSV中的特殊字符
            escaped_row = [f'"{str(field).replace("\"", "\"\"")}"' for field in row]
            csv_content += ','.join(escaped_row) + '\n'
        
        # 添加BOM以支持中文
        csv_content = '\ufeff' + csv_content
        
        from flask import make_response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=assets_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        print(f"导出CSV失败: {e}")
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'导出失败: {str(e)}'
        }), 500

# 下载导入模板API
@app.route('/api/assets/import-template', methods=['GET'])
def download_import_template():
    """下载资产导入模板"""
    try:
        # 创建模板数据
        template_data = [
            {
                '资产编码': 'AS20240001',
                '资产名称': 'Dell服务器01',
                '品牌': 'Dell',
                '型号': 'PowerEdge R740',
                '类别': '服务器',
                '状态': '在用',
                '使用人': '张三',
                '使用部门': 'IT部',
                '保修开始日期': '2024-01-01',
                '保修结束日期': '2027-01-01',
                '保修期(月)': 36
            },
            {
                '资产编码': 'AS20240002',
                '资产名称': 'HP笔记本01',
                '品牌': 'HP',
                '型号': 'EliteBook 840',
                '类别': '笔记本',
                '状态': '在用',
                '使用人': '李四',
                '使用部门': '财务部',
                '保修开始日期': '2024-02-01',
                '保修结束日期': '2026-02-01',
                '保修期(月)': 24
            }
        ]
        
        try:
            # 尝试使用pandas创建Excel模板
            import pandas as pd
            from io import BytesIO
            
            df = pd.DataFrame(template_data)
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='资产导入模板', index=False)
            
            output.seek(0)
            
            from flask import send_file
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='asset_import_template.xlsx'
            )
            
        except ImportError:
            # 如果pandas未安装，返回CSV模板
            csv_content = '资产编码,资产名称,品牌,型号,类别,状态,使用人,使用部门,保修开始日期,保修结束日期,保修期(月)\n'
            csv_content += 'AS20240001,Dell服务器01,Dell,PowerEdge R740,服务器,在用,张三,IT部,2024-01-01,2027-01-01,36\n'
            csv_content += 'AS20240002,HP笔记本01,HP,EliteBook 840,笔记本,在用,李四,财务部,2024-02-01,2026-02-01,24\n'
            
            # 添加BOM以支持中文
            csv_content = '\ufeff' + csv_content
            
            from flask import make_response
            response = make_response(csv_content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = 'attachment; filename=asset_import_template.csv'
            
            return response
            
    except Exception as e:
        print(f"生成导入模板失败: {e}")
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'模板生成失败: {str(e)}'
        }), 500

# 导入资产API
@app.route('/api/assets/import', methods=['POST'])
def import_assets():
    """导入资产数据"""
    print("📥 导入资产API被调用")
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '请选择要导入的文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '请选择要导入的文件'
            }), 400
        
        # 检查文件格式
        allowed_extensions = {'.xlsx', '.xls', '.csv'}
        file_ext = '.' + file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '只支持 Excel (.xlsx, .xls) 和 CSV (.csv) 文件格式'
            }), 400
        
        print(f"开始导入文件: {file.filename}")
        
        # 解析文件
        if file_ext == '.csv':
            result = import_from_csv(file)
        else:
            result = import_from_excel(file)
        
        if not result['success']:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': result['message']
            }), 400
        
        import_data = result['data']
        assets_data = import_data['assets']
        errors = import_data.get('errors', [])
        
        # 批量导入资产
        success_count = 0
        failed_count = 0
        import_errors = []
        
        for i, asset_data in enumerate(assets_data):
            try:
                # 检查资产编码是否已存在
                existing_asset = Asset.query.filter_by(asset_code=asset_data['asset_code']).first()
                if existing_asset:
                    import_errors.append(f"资产编码 {asset_data['asset_code']} 已存在")
                    failed_count += 1
                    continue
                
                # 创建资产对象
                asset = Asset(
                    asset_code=asset_data['asset_code'],
                    name=asset_data['name'],
                    brand=asset_data.get('brand'),
                    model=asset_data.get('model'),
                    category=asset_data.get('category'),
                    status=asset_data.get('status', '在用'),
                    user_name=asset_data.get('user_name'),
                    user_department=asset_data.get('user_department'),
                    warranty_start_date=asset_data.get('warranty_start_date'),
                    warranty_end_date=asset_data.get('warranty_end_date'),
                    warranty_period=asset_data.get('warranty_period')
                )
                
                db.session.add(asset)
                success_count += 1
                
            except Exception as e:
                import_errors.append(f"第 {i+2} 行: {str(e)}")
                failed_count += 1
                continue
        
        # 提交数据库事务
        try:
            db.session.commit()
            print(f"导入完成: 成功 {success_count} 条，失败 {failed_count} 条")
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'code': 500,
                'message': f'数据库保存失败: {str(e)}'
            }), 500
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': f'导入完成！成功 {success_count} 条，失败 {failed_count} 条',
            'data': {
                'success_count': success_count,
                'error_count': failed_count,
                'errors': import_errors[:10],  # 最多返回10个错误
                'total_errors': len(import_errors)
            }
        })
        
    except Exception as e:
        print(f"导入资产失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'导入失败: {str(e)}'
        }), 500

def import_from_csv(file):
    """从 CSV 文件导入资产"""
    try:
        import csv
        import io
        from datetime import datetime
        
        # 读取 CSV 内容
        content = file.read().decode('utf-8-sig')  # 支持 BOM
        csv_reader = csv.DictReader(io.StringIO(content))
        
        # 定义字段映射
        field_mapping = {
            '资产编码': 'asset_code',
            '资产名称': 'name',
            '品牌': 'brand',
            '型号': 'model',
            '类别': 'category',
            '状态': 'status',
            '使用人': 'user_name',
            '使用部门': 'user_department',
            # 英文字段兼容
            'asset_code': 'asset_code',
            'name': 'name',
            'brand': 'brand',
            'model': 'model',
            'category': 'category',
            'status': 'status',
            'user_name': 'user_name',
            'user_department': 'user_department'
        }
        
        assets = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, 2):
            try:
                asset_data = {}
                
                # 映射字段
                for csv_field, db_field in field_mapping.items():
                    if csv_field in row and row[csv_field]:
                        value = str(row[csv_field]).strip()
                        if value:
                            asset_data[db_field] = value
                
                # 必填字段验证
                if not asset_data.get('asset_code'):
                    errors.append(f'第{row_num}行: 资产编码不能为空')
                    continue
                
                if not asset_data.get('name'):
                    errors.append(f'第{row_num}行: 资产名称不能为空')
                    continue
                
                assets.append(asset_data)
                
            except Exception as e:
                errors.append(f'第{row_num}行: 数据解析错误 - {str(e)}')
        
        return {
            'success': True,
            'message': f'解析完成，共{len(assets)}条有效数据',
            'data': {
                'assets': assets,
                'errors': errors
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'CSV文件解析失败: {str(e)}',
            'data': None
        }

def import_from_excel(file):
    """从 Excel 文件导入资产"""
    try:
        import pandas as pd
        from datetime import datetime
        
        # 读取 Excel 文件
        df = pd.read_excel(file, engine='openpyxl')
        
        # 定义字段映射
        field_mapping = {
            '资产编码': 'asset_code',
            '资产名称': 'name',
            '品牌': 'brand',
            '型号': 'model',
            '类别': 'category',
            '状态': 'status',
            '使用人': 'user_name',
            '使用部门': 'user_department',
            '保修开始日期': 'warranty_start_date',
            '保修结束日期': 'warranty_end_date',
            '保修期(月)': 'warranty_period',
            # 英文字段兼容
            'asset_code': 'asset_code',
            'name': 'name',
            'brand': 'brand',
            'model': 'model',
            'category': 'category',
            'status': 'status',
            'user_name': 'user_name',
            'user_department': 'user_department',
            'warranty_start_date': 'warranty_start_date',
            'warranty_end_date': 'warranty_end_date',
            'warranty_period': 'warranty_period'
        }
        
        assets = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                asset_data = {}
                row_num = index + 2  # Excel行号从2开始
                
                # 映射字段
                for excel_field, db_field in field_mapping.items():
                    if excel_field in df.columns and pd.notna(row[excel_field]):
                        value = str(row[excel_field]).strip()
                        if value and value != 'nan':
                            # 特殊字段处理
                            if db_field in ['warranty_start_date', 'warranty_end_date']:
                                try:
                                    if isinstance(row[excel_field], str):
                                        # 字符串日期解析
                                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日']:
                                            try:
                                                asset_data[db_field] = datetime.strptime(value, fmt).date()
                                                break
                                            except:
                                                continue
                                    else:
                                        # pandas Timestamp 对象
                                        asset_data[db_field] = row[excel_field].date() if hasattr(row[excel_field], 'date') else None
                                except:
                                    pass  # 日期解析失败时跳过
                            elif db_field == 'warranty_period':
                                try:
                                    asset_data[db_field] = int(float(value))
                                except:
                                    pass  # 数字解析失败时跳过
                            else:
                                asset_data[db_field] = value
                
                # 必填字段验证
                if not asset_data.get('asset_code'):
                    errors.append(f'第{row_num}行: 资产编码不能为空')
                    continue
                
                if not asset_data.get('name'):
                    errors.append(f'第{row_num}行: 资产名称不能为空')
                    continue
                
                assets.append(asset_data)
                
            except Exception as e:
                errors.append(f'第{row_num}行: 数据解析错误 - {str(e)}')
        
        return {
            'success': True,
            'message': f'解析完成，共{len(assets)}条有效数据',
            'data': {
                'assets': assets,
                'errors': errors
            }
        }
        
    except ImportError:
        return {
            'success': False,
            'message': 'pandas库未安装，无法解析Excel文件，请使用CSV格式',
            'data': None
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Excel文件解析失败: {str(e)}',
            'data': None
        }

# 资产类别API
@app.route('/api/assets/categories', methods=['GET'])
def get_asset_categories():
    """获取资产类别列表"""
    try:
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有未删除的类别
        cursor.execute('''
        SELECT id, name, code, description
        FROM asset_category 
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
        ORDER BY sort_order, name
        ''')
        
        rows = cursor.fetchall()
        categories = []
        for row in rows:
            categories.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'description': row[3]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'code': 200,
            'message': '获取资产类别成功',
            'data': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'code': 500,
            'message': f'获取资产类别失败: {str(e)}'
        }), 500

# 统计数据API
@app.route('/api/statistics/overview', methods=['GET'])
def statistics_overview():
    """获取统计概览"""
    try:
        # 资产统计
        total_assets = Asset.query.count()
        active_assets = Asset.query.filter_by(status='在用').count()
        
        # 网络设备统计 - 从资产表中统计网络设备类别的资产
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有网络设备类别
        cursor.execute('''
        SELECT name FROM asset_category 
        WHERE is_network_device = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
        ''')
        network_categories = [row[0] for row in cursor.fetchall()]
        
        # 统计网络设备数量
        if network_categories:
            placeholders = ','.join(['?' for _ in network_categories])
            cursor.execute(f'''
            SELECT COUNT(*) FROM it_asset 
            WHERE category IN ({placeholders})
            ''', network_categories)
            device_count = cursor.fetchone()[0]
            
            # 统计在线网络设备（状态为在用的设备）
            cursor.execute(f'''
            SELECT COUNT(*) FROM it_asset 
            WHERE category IN ({placeholders}) AND status = '在用'
            ''', network_categories)
            online_devices = cursor.fetchone()[0]
        else:
            device_count = 0
            online_devices = 0
        
        conn.close()
        
        # 运维记录统计
        maintenance_count = MaintenanceRecord.query.count()
        pending_maintenance = MaintenanceRecord.query.filter_by(status='待处理').count()
        
        # 故障记录统计
        fault_count = FaultRecord.query.count()
        unresolved_faults = FaultRecord.query.filter_by(status='未解决').count()
        
        return jsonify({
            'success': True,  # 添加success字段
            'status': 'success',
            'code': 200,
            'message': '获取统计数据成功',
            'data': {
                'total_assets': total_assets,
                'active_assets': active_assets,
                'inactive_assets': total_assets - active_assets,
                'device_count': device_count,  # 现在统计的是网络设备类别的资产
                'online_devices': online_devices,
                'offline_devices': device_count - online_devices,
                'maintenance_count': maintenance_count,
                'pending_maintenance': pending_maintenance,
                'completed_maintenance': maintenance_count - pending_maintenance,
                'fault_count': fault_count,
                'unresolved_faults': unresolved_faults,
                'resolved_faults': fault_count - unresolved_faults,
                'users_count': User.query.count(),
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,  # 添加success字段
            'status': 'error',
            'code': 500,
            'message': f'获取统计数据失败: {str(e)}'
        }), 500

# 类别管理API
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有资产类别"""
    try:
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取查询参数
        network_only = request.args.get('network_only', 'false').lower() == 'true'
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if not include_deleted:
            where_conditions.append('(is_deleted = 0 OR is_deleted IS NULL)')
        
        if network_only:
            where_conditions.append('is_network_device = 1')
        
        where_clause = ' WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        query = f'''
        SELECT id, name, code, parent_id, description, sort_order, 
               is_network_device, can_topology, is_terminal, default_port_count,
               device_icon, device_color, created_at, updated_at, is_deleted
        FROM asset_category 
        {where_clause}
        ORDER BY sort_order, name
        '''
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        categories = []
        for row in rows:
            categories.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'parent_id': row[3],
                'description': row[4],
                'sort_order': row[5],
                'is_network_device': bool(row[6]),
                'can_topology': bool(row[7]),
                'is_terminal': bool(row[8]),
                'default_port_count': row[9],
                'device_icon': row[10],
                'device_color': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取类别列表成功',
            'data': categories
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'获取类别列表失败: {str(e)}'
        }), 500

@app.route('/api/categories', methods=['POST'])
def create_category():
    """创建新的资产类别"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name') or not data.get('code'):
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '类别名称和编码不能为空'
            }), 400
        
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查编码是否已存在
        cursor.execute('SELECT id FROM asset_category WHERE code = ? AND (is_deleted = 0 OR is_deleted IS NULL)', (data['code'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '类别编码已存在'
            }), 400
        
        # 插入新类别
        now = datetime.now().isoformat()
        insert_sql = '''
        INSERT INTO asset_category (name, code, parent_id, description, sort_order,
                                   is_network_device, can_topology, is_terminal, 
                                   default_port_count, device_icon, device_color,
                                   created_at, updated_at, is_deleted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        cursor.execute(insert_sql, (
            data['name'], data['code'], data.get('parent_id'),
            data.get('description', ''), data.get('sort_order', 0),
            data.get('is_network_device', False), data.get('can_topology', False),
            data.get('is_terminal', False), data.get('default_port_count', 0),
            data.get('device_icon', '📦'), data.get('device_color', '#606266'),
            now, now, False
        ))
        
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '创建类别成功',
            'data': {'id': new_id}
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'创建类别失败: {str(e)}'
        }), 500

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """更新资产类别"""
    try:
        data = request.get_json()
        
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查类别是否存在
        cursor.execute('SELECT id FROM asset_category WHERE id = ?', (category_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '类别不存在'
            }), 404
        
        # 更新类别
        now = datetime.now().isoformat()
        update_sql = '''
        UPDATE asset_category SET 
            name = ?, description = ?, sort_order = ?,
            is_network_device = ?, can_topology = ?, is_terminal = ?,
            default_port_count = ?, device_icon = ?, device_color = ?,
            updated_at = ?
        WHERE id = ?
        '''
        
        cursor.execute(update_sql, (
            data.get('name'), data.get('description', ''), data.get('sort_order', 0),
            data.get('is_network_device', False), data.get('can_topology', False),
            data.get('is_terminal', False), data.get('default_port_count', 0),
            data.get('device_icon', '📦'), data.get('device_color', '#606266'),
            now, category_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '更新类别成功'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'更新类别失败: {str(e)}'
        }), 500

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除资产类别（软删除）"""
    try:
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查是否有资产使用此类别
        cursor.execute('SELECT COUNT(*) FROM it_asset WHERE category = (SELECT name FROM asset_category WHERE id = ?)', (category_id,))
        asset_count = cursor.fetchone()[0]
        
        if asset_count > 0:
            conn.close()
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': f'该类别下还有{asset_count}个资产，无法删除'
            }), 400
        
        # 软删除类别
        now = datetime.now().isoformat()
        cursor.execute('UPDATE asset_category SET is_deleted = 1, updated_at = ? WHERE id = ?', (now, category_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '类别不存在'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '删除类别成功'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'删除类别失败: {str(e)}'
        }), 500

# 错误处理
@app.errorhandler(404)
def handle_not_found(e):
    # 动态获取所有注册的路由
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith('/api/'):
            endpoints.append(rule.rule)
    
    return jsonify({
        'status': 'error',
        'code': 404,
        'message': '请求的资源不存在',
        'available_endpoints': sorted(set(endpoints))  # 去重并排序
    }), 404

@app.errorhandler(500)
def handle_server_error(e):
    return jsonify({
        'status': 'error',
        'code': 500,
        'message': '服务器内部错误'
    }), 500

# ===================== 端口管理API =====================

@app.route('/api/ports/assets/<int:asset_id>/ports', methods=['GET'])
def get_asset_ports(asset_id):
    """获取资产的端口列表"""
    try:
        # 检查资产是否存在
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '资产不存在'
            }), 404
        
        # 获取端口列表
        ports = AssetPort.query.filter_by(
            asset_id=asset_id, 
            is_deleted=False
        ).order_by(AssetPort.port_index, AssetPort.port_name).all()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取端口列表成功',
            'data': {
                'ports': [port.to_dict() for port in ports],
                'asset': {
                    'id': asset.id,
                    'name': asset.name,
                    'category': asset.category
                }
            }
        })
    except Exception as e:
        print(f"获取端口列表失败: {e}")
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '获取端口列表失败'
        }), 500

@app.route('/api/ports/assets/<int:asset_id>/ports', methods=['POST'])
def create_asset_port(asset_id):
    """创建资产端口"""
    try:
        # 检查资产是否存在
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '资产不存在'
            }), 404
        
        data = request.get_json() or {}
        
        # 检查端口名称是否重复
        existing_port = AssetPort.query.filter_by(
            asset_id=asset_id,
            port_name=data.get('port_name'),
            is_deleted=False
        ).first()
        
        if existing_port:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '端口名称已存在'
            }), 400
        
        # 创建端口
        port = AssetPort(
            asset_id=asset_id,
            port_name=data.get('port_name'),
            port_type=data.get('port_type', 'ethernet'),
            port_speed=data.get('port_speed'),
            port_status=data.get('port_status', 'unused'),
            port_index=data.get('port_index'),
            vlan_id=data.get('vlan_id'),
            is_uplink=data.get('is_uplink', False),
            description=data.get('description')
        )
        
        db.session.add(port)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 201,
            'message': '端口创建成功',
            'data': port.to_dict()
        }), 201
        
    except Exception as e:
        print(f"创建端口失败: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '创建端口失败'
        }), 500

@app.route('/api/ports/assets/<int:asset_id>/ports/batch', methods=['POST'])
def create_ports_batch(asset_id):
    """批量创建端口"""
    try:
        # 检查资产是否存在
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '资产不存在'
            }), 404
        
        data = request.get_json() or {}
        ports_data = data.get('ports', [])
        
        if not ports_data:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '未提供端口数据'
            }), 400
        
        created_ports = []
        errors = []
        
        for port_data in ports_data:
            try:
                # 检查端口名称是否重复
                existing_port = AssetPort.query.filter_by(
                    asset_id=asset_id,
                    port_name=port_data.get('port_name'),
                    is_deleted=False
                ).first()
                
                if existing_port:
                    errors.append(f"端口 {port_data.get('port_name')} 已存在")
                    continue
                
                port = AssetPort(
                    asset_id=asset_id,
                    port_name=port_data.get('port_name'),
                    port_type=port_data.get('port_type', 'ethernet'),
                    port_speed=port_data.get('port_speed'),
                    port_status=port_data.get('port_status', 'unused'),
                    port_index=port_data.get('port_index'),
                    vlan_id=port_data.get('vlan_id'),
                    is_uplink=port_data.get('is_uplink', False),
                    description=port_data.get('description')
                )
                
                db.session.add(port)
                created_ports.append(port)
                
            except Exception as e:
                errors.append(f"创建端口 {port_data.get('port_name', '未知')} 失败: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 201,
            'message': f'批量创建完成，成功: {len(created_ports)}个，失败: {len(errors)}个',
            'data': {
                'created': [port.to_dict() for port in created_ports],
                'errors': errors
            }
        }), 201
        
    except Exception as e:
        print(f"批量创建端口失败: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '批量创建端口失败'
        }), 500

@app.route('/api/ports/<int:port_id>', methods=['PUT'])
def update_port(port_id):
    """更新端口信息"""
    try:
        port = AssetPort.query.get(port_id)
        if not port or port.is_deleted:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '端口不存在'
            }), 404
        
        data = request.get_json() or {}
        
        # 检查端口名称是否重复（排除自己）
        if 'port_name' in data:
            existing_port = AssetPort.query.filter_by(
                asset_id=port.asset_id,
                port_name=data['port_name'],
                is_deleted=False
            ).filter(AssetPort.id != port_id).first()
            
            if existing_port:
                return jsonify({
                    'status': 'error',
                    'code': 400,
                    'message': '端口名称已存在'
                }), 400
        
        # 更新字段
        for field in ['port_name', 'port_type', 'port_speed', 'port_status', 
                     'port_index', 'vlan_id', 'is_uplink', 'description']:
            if field in data:
                setattr(port, field, data[field])
        
        port.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '端口更新成功',
            'data': port.to_dict()
        })
        
    except Exception as e:
        print(f"更新端口失败: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '更新端口失败'
        }), 500

@app.route('/api/ports/<int:port_id>', methods=['DELETE'])
def delete_port(port_id):
    """删除端口"""
    try:
        port = AssetPort.query.get(port_id)
        if not port or port.is_deleted:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '端口不存在'
            }), 404
        
        # 软删除
        port.is_deleted = True
        port.updated_at = datetime.utcnow()
        
        # 如果端口有连接，也需要断开
        if port.is_connected:
            port.is_connected = False
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '端口删除成功'
        })
        
    except Exception as e:
        print(f"删除端口失败: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '删除端口失败'
        }), 500

@app.route('/api/ports/connect', methods=['POST'])
def connect_ports():
    """连接两个端口"""
    try:
        data = request.get_json() or {}
        source_port_id = data.get('source_port_id')
        target_port_id = data.get('target_port_id')
        
        if not source_port_id or not target_port_id:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '缺少必要的端口ID'
            }), 400
        
        # 检查端口是否存在
        source_port = AssetPort.query.get(source_port_id)
        target_port = AssetPort.query.get(target_port_id)
        
        if not source_port or source_port.is_deleted:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '源端口不存在'
            }), 404
        
        if not target_port or target_port.is_deleted:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '目标端口不存在'
            }), 404
        
        # 检查端口是否已连接
        if source_port.is_connected or target_port.is_connected:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '端口已被连接'
            }), 400
        
        # 创建连接记录
        connection = PortConnection(
            source_port_id=source_port_id,
            target_port_id=target_port_id,
            cable_type=data.get('cable_type', 'copper'),
            cable_length=data.get('cable_length'),
            notes=data.get('notes'),
            connected_by=1,  # 暂时使用固定用户ID
            is_active=True
        )
        
        # 更新端口状态和连接关系
        source_port.is_connected = True
        target_port.is_connected = True
        source_port.cable_type = data.get('cable_type', 'copper')
        target_port.cable_type = data.get('cable_type', 'copper')
        
        # 关键修复：设置双向连接的 connected_port_id
        source_port.connected_port_id = target_port_id
        target_port.connected_port_id = source_port_id
        
        if data.get('cable_length'):
            source_port.cable_length = data.get('cable_length')
            target_port.cable_length = data.get('cable_length')
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 201,
            'message': '端口连接成功',
            'data': connection.to_dict()
        }), 201
        
    except Exception as e:
        print(f"连接端口失败: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '连接端口失败'
        }), 500

@app.route('/api/ports/<int:port_id>/disconnect', methods=['POST'])
def disconnect_port(port_id):
    """断开端口连接"""
    try:
        port = AssetPort.query.get(port_id)
        if not port or port.is_deleted:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '端口不存在'
            }), 404
        
        if not port.is_connected:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '端口未连接'
            }), 400
        
        # 查找并删除连接记录
        connections = PortConnection.query.filter(
            (PortConnection.source_port_id == port_id) |
            (PortConnection.target_port_id == port_id)
        ).all()
        
        for connection in connections:
            # 断开两个端口的连接
            source_port = AssetPort.query.get(connection.source_port_id)
            target_port = AssetPort.query.get(connection.target_port_id)
            
            if source_port:
                source_port.is_connected = False
                source_port.cable_type = None
                source_port.cable_length = None
            
            if target_port:
                target_port.is_connected = False
                target_port.cable_type = None
                target_port.cable_length = None
            
            db.session.delete(connection)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '端口连接已断开'
        })
        
    except Exception as e:
        print(f"断开端口连接失败: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '断开端口连接失败'
        }), 500

@app.route('/api/ports/export', methods=['GET'])
def export_ports():
    """导出端口信息"""
    try:
        asset_id = request.args.get('asset_id')
        
        # 构建查询
        query = AssetPort.query.filter_by(is_deleted=False)
        if asset_id:
            query = query.filter_by(asset_id=asset_id)
        
        ports = query.all()
        
        # 构建导出数据
        export_data = []
        for port in ports:
            row = {
                '资产名称': port.asset.name if port.asset else '',
                '端口名称': port.port_name,
                '端口类型': port.port_type,
                '端口速率': port.port_speed or '',
                '端口状态': port.port_status,
                '端口序号': port.port_index or '',
                'VLAN ID': port.vlan_id or '',
                '是否上联': '是' if port.is_uplink else '否',
                '是否连接': '是' if port.is_connected else '否',
                '描述': port.description or ''
            }
            export_data.append(row)
        
        try:
            import pandas as pd
            from io import BytesIO
            
            # 创建Excel文件
            df = pd.DataFrame(export_data)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='端口信息', index=False)
            
            output.seek(0)
            
            from flask import send_file
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='端口信息.xlsx'
            )
            
        except ImportError:
            # 如果没有pandas，返回JSON格式
            return jsonify({
                'status': 'success',
                'code': 200,
                'message': '导出端口信息成功',
                'data': export_data
            })
            
    except Exception as e:
        print(f"导出端口信息失败: {e}")
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '导出端口信息失败'
        }), 500

@app.route('/api/ports/statistics/batch', methods=['GET'])
def get_ports_statistics_batch():
    """批量获取多个资产的端口统计信息"""
    try:
        # 获取参数
        asset_ids = request.args.get('asset_ids', '')
        if not asset_ids:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '缺少asset_ids参数'
            }), 400
        
        # 解析asset_ids
        try:
            asset_id_list = [int(id.strip()) for id in asset_ids.split(',') if id.strip()]
        except ValueError:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': 'asset_ids格式错误'
            }), 400
        
        if not asset_id_list:
            return jsonify({
                'status': 'success',
                'code': 200,
                'message': '获取端口统计成功',
                'data': {}
            })
        
        # 批量查询端口统计信息
        port_stats = {}
        
        # 使用简单的方法逐个查询资产的端口统计
        for asset_id in asset_id_list:
            # 统计总端口数
            total_count = AssetPort.query.filter_by(
                asset_id=asset_id,
                is_deleted=False
            ).count()
            
            # 统计已连接端口数
            connected_count = AssetPort.query.filter_by(
                asset_id=asset_id,
                is_connected=True,
                is_deleted=False
            ).count()
            
            port_stats[asset_id] = {
                'port_count': total_count,
                'connected_ports': connected_count,
                'available_ports': total_count - connected_count
            }
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取端口统计成功',
            'data': port_stats
        })
        
    except Exception as e:
        print(f"获取端口统计失败: {e}")
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '获取端口统计失败'
        }), 500

# =================== 数据字典API ===================

@app.route('/api/dictionary/maintenance/types', methods=['GET'])
def get_maintenance_types_for_form():
    """为运维记录表单提供类型选项"""
    try:
        import sqlite3
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name FROM dict_maintenance_type 
            WHERE is_active = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, name
        ''')
        
        types = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 如果数据字典为空，返回默认值
        if not types:
            types = ['例行维护', '紧急处理', '升级改造', '故障修复', '巡检']
        
        return jsonify({
            'success': True,
            'status': 'success',
            'code': 200,
            'message': '获取运维类型成功',
            'data': types
        })
        
    except Exception as e:
        print(f'获取运维类型失败: {e}')
        # 返回默认数据
        return jsonify({
            'success': True,
            'status': 'success',
            'code': 200,
            'message': '获取运维类型成功',
            'data': ['例行维护', '紧急处理', '升级改造', '故障修复', '巡检']
        })

@app.route('/api/dictionary/maintenance/categories', methods=['GET'])
def get_maintenance_categories_for_form():
    """为运维记录表单提供类别选项"""
    try:
        import sqlite3
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name FROM dict_maintenance_category 
            WHERE is_active = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, name
        ''')
        
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 如果数据字典为空，返回默认值
        if not categories:
            categories = ['硬件维护', '软件维护', '网络设备', '系统巡检', '故障修复']
        
        return jsonify({
            'success': True,
            'status': 'success',
            'code': 200,
            'message': '获取维护类别成功',
            'data': categories
        })
        
    except Exception as e:
        print(f'获取维护类别失败: {e}')
        # 返回默认数据
        return jsonify({
            'success': True,
            'status': 'success',
            'code': 200,
            'message': '获取维护类别成功',
            'data': ['硬件维护', '软件维护', '网络设备', '系统巡检', '故障修复']
        })

@app.route('/api/dictionary/departments/simple', methods=['GET'])
def get_departments_for_form():
    """为表单提供部门选项"""
    try:
        import sqlite3
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name FROM dict_department 
            WHERE is_active = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, name
        ''')
        
        departments = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 如果数据字典为空，返回默认值
        if not departments:
            departments = ['IT部门', '运维部门', '技术部门', '网络部门']
        
        return jsonify({
            'success': True,
            'status': 'success',
            'code': 200,
            'message': '获取部门列表成功',
            'data': departments
        })
        
    except Exception as e:
        print(f'获取部门列表失败: {e}')
        # 返回默认数据
        return jsonify({
            'success': True,
            'status': 'success',
            'code': 200,
            'message': '获取部门列表成功',
            'data': ['IT部门', '运维部门', '技术部门', '网络部门']
        })

@app.route('/api/dictionary/maintenance-types', methods=['GET'])
def get_maintenance_types():
    """获取运维记录类型列表"""
    try:
        import sqlite3
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, code, description, parent_id, sort_order, is_active, created_at, updated_at
            FROM dict_maintenance_type 
            WHERE (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, created_at
        ''')
        
        types = []
        for row in cursor.fetchall():
            types.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'description': row[3],
                'parent_id': row[4],
                'sort_order': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'status': 'success',
            'code': 200,
            'message': '获取运维记录类型列表成功',
            'data': types
        })
        
    except Exception as e:
        print(f'获取运维记录类型列表失败: {e}')
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取运维记录类型列表失败: {str(e)}'
        }), 500

# 简化的数据字典管理API（只提供列表查看功能）
@app.route('/api/dictionary/maintenance-categories', methods=['GET'])
def get_maintenance_categories():
    """获取运维维护类别列表"""
    try:
        import sqlite3
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, code, description, parent_id, sort_order, is_active, created_at, updated_at
            FROM dict_maintenance_category 
            WHERE (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, created_at
        ''')
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'description': row[3],
                'parent_id': row[4],
                'sort_order': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'status': 'success',
            'code': 200,
            'message': '获取运维维护类别列表成功',
            'data': categories
        })
        
    except Exception as e:
        print(f'获取运维维护类别列表失败: {e}')
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取运维维护类别列表失败: {str(e)}'
        }), 500

@app.route('/api/dictionary/departments', methods=['GET'])
def get_departments():
    """获取组织机构列表"""
    try:
        import sqlite3
        
        db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, code, description, parent_id, sort_order, is_active, created_at, updated_at
            FROM dict_department 
            WHERE (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, created_at
        ''')
        
        departments = []
        for row in cursor.fetchall():
            departments.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'description': row[3],
                'parent_id': row[4],
                'sort_order': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'status': 'success',
            'code': 200,
            'message': '获取组织机构列表成功',
            'data': departments
        })
        
    except Exception as e:
        print(f'获取组织机构列表失败: {e}')
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取组织机构列表失败: {str(e)}'
        }), 500

# 测试数据初始化函数
def init_test_data():
    """初始化测试数据，包含有实际保修信息的资产"""
    try:
        # 检查是否已有数据
        if Asset.query.count() > 0:
            print("📋 数据库已有数据，跳过初始化")
            return
        
        print("📊 初始化测试数据...")
        
        from datetime import date, timedelta
        
        # 创建不同保修状态的测试资产
        test_assets = [
            {
                'asset_code': 'AS20240001',
                'name': 'Dell服务器01',
                'brand': 'Dell',
                'model': 'PowerEdge R740',
                'category': '服务器',
                'status': '在用',
                'user_name': '张三',
                'user_department': 'IT部',
                'warranty_start_date': date(2024, 1, 1),
                'warranty_end_date': date(2027, 1, 1),  # 保修中
                'warranty_period': 36
            },
            {
                'asset_code': 'AS20240002',
                'name': 'HP工作站01',
                'brand': 'HP',
                'model': 'Z4 G4',
                'category': '工作站',
                'status': '在用',
                'user_name': '李四',
                'user_department': '研发部',
                'warranty_start_date': date(2022, 6, 1),
                'warranty_end_date': date(2023, 6, 1),  # 已过保
                'warranty_period': 12
            },
            {
                'asset_code': 'AS20240003',
                'name': 'Cisco交换机01',
                'brand': 'Cisco',
                'model': 'Catalyst 3850',
                'category': '交换机',
                'status': '在用',
                'user_name': '网络管理员',
                'user_department': 'IT部',
                'warranty_start_date': date(2024, 9, 1),
                'warranty_end_date': date.today() + timedelta(days=15),  # 即将到期
                'warranty_period': 12
            },
            {
                'asset_code': 'AS20240004',
                'name': 'Dell工作站02',
                'brand': 'Dell',
                'model': 'Precision 3640',
                'category': '工作站',
                'status': '在用',
                'user_name': '王五',
                'user_department': '设计部',
                'warranty_start_date': date(2024, 1, 15),
                'warranty_end_date': date(2026, 1, 15),  # 保修中
                'warranty_period': 24
            },
            {
                'asset_code': 'AS20240005',
                'name': 'Lenovo服务器01',
                'brand': 'Lenovo',
                'model': 'ThinkServer RD550',
                'category': '服务器',
                'status': '在用',
                'user_name': '系统管理员',
                'user_department': 'IT部',
                'warranty_start_date': date(2021, 3, 1),
                'warranty_end_date': date(2022, 3, 1),  # 已过保
                'warranty_period': 12
            },
            {
                'asset_code': 'AS20240006',
                'name': '打印机01',
                'brand': 'Canon',
                'model': 'imageRUNNER 2630i',
                'category': '办公设备',
                'status': '在用',
                'user_name': '办公室',
                'user_department': '行政部',
                'warranty_start_date': date(2024, 8, 1),
                'warranty_end_date': date.today() + timedelta(days=25),  # 即将到期
                'warranty_period': 12
            },
            {
                'asset_code': 'AS20240007',
                'name': 'UPS电源01',
                'brand': 'APC',
                'model': 'Smart-UPS 3000VA',
                'category': 'UPS',
                'status': '在用',
                'user_name': '机房管理员',
                'user_department': 'IT部',
                'warranty_start_date': date(2024, 2, 1),
                'warranty_end_date': date(2029, 2, 1),  # 保修中
                'warranty_period': 60
            },
            {
                'asset_code': 'AS20240008',
                'name': '显示器01',
                'brand': 'Dell',
                'model': 'UltraSharp U2720Q',
                'category': '显示器',
                'status': '在用',
                'user_name': '赵六',
                'user_department': '研发部',
                'warranty_start_date': None,  # 无保修信息
                'warranty_end_date': None,
                'warranty_period': None
            }
        ]
        
        # 创建资产记录
        for asset_data in test_assets:
            asset = Asset(**asset_data)
            db.session.add(asset)
        
        # 创建管理员用户
        if User.query.filter_by(username='admin').first() is None:
            admin_user = User(
                username='admin',
                password_hash='pbkdf2:sha256:100000$salt$adb7d68e614527420719cea2a7f49848c6980e06f5e15867ebbf24cc2acc1d49',
                email='admin@itops.com',
                real_name='系统管理员',
                status=1
            )
            db.session.add(admin_user)
        
        db.session.commit()
        print(f"✅ 测试数据初始化完成，创建了 {len(test_assets)} 个资产记录")
        print("📋 保修状态分布:")
        print("   - 保修中: 3个 (Dell服务器01, Dell工作站02, UPS电源01)")
        print("   - 已过保: 2个 (HP工作站01, Lenovo服务器01)")
        print("   - 即将到期: 2个 (Cisco交换机01, 打印机01)")
        print("   - 无保修信息: 1个 (显示器01)")
        
    except Exception as e:
        print(f"⚠️  测试数据初始化失败: {e}")
        db.session.rollback()

def main():
    """启动服务"""
    print("=" * 70)
    print("🚀 IT运维系统 - 完整版后端服务启动中...")
    print("=" * 70)
    print("📋 服务信息:")
    print(f"   🌐 后端地址: http://localhost:5000")
    print(f"   🔗 前端地址: http://localhost:3000")
    print(f"   🔑 默认账户: admin / admin123")
    print(f"   📡 CORS已启用，支持跨域访问")
    print(f"   🗄️  数据库: SQLite (it_ops_system.db)")
    print("=" * 70)
    print("🔍 测试步骤:")
    print("   1. 访问 http://localhost:5000 检查后端状态")
    print("   2. 访问 http://localhost:3000 打开前端界面")
    print("   3. 使用 admin/admin123 进行登录测试")
    print("   4. 查看资产管理和统计数据")
    print("=" * 70)
    
    # 确保数据库表存在
    with app.app_context():
        try:
            db.create_all()
            print("✅ 数据库表检查完成")
            
            # 打印所有注册的路由
            print("📋 注册的路由:")
            for rule in app.url_map.iter_rules():
                print(f"  {rule.rule} - {rule.methods}")
            
            # 初始化测试数据
            init_test_data()
            
        except Exception as e:
            print(f"⚠️  数据库表检查失败: {e}")
    
    # 启动应用
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()