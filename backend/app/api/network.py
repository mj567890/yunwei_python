"""
网络设备管理API
"""
from flask import Blueprint, request
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

from app.models.network import NetworkDevice, DevicePort, NetworkTopology
from app.models.location import Building, Floor, Room
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required, log_operation
from app.utils.exceptions import ValidationError as CustomValidationError, ResourceNotFoundError
from app.utils.helpers import validate_ip_address, validate_mac_address
from app import db

network_bp = Blueprint('network', __name__)


class NetworkDeviceSchema(Schema):
    """网络设备参数验证"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    device_type = fields.Str(required=True, validate=validate.OneOf(['交换机', '路由器', '防火墙', '安全设备']))
    brand = fields.Str(allow_none=True, validate=validate.Length(max=50))
    model = fields.Str(allow_none=True, validate=validate.Length(max=100))
    ip_address = fields.Str(allow_none=True, validate=validate.Length(max=15))
    mac_address = fields.Str(allow_none=True, validate=validate.Length(max=17))
    subnet_mask = fields.Str(allow_none=True, validate=validate.Length(max=15))
    gateway = fields.Str(allow_none=True, validate=validate.Length(max=15))
    dns_servers = fields.Str(allow_none=True, validate=validate.Length(max=255))
    building_id = fields.Int(allow_none=True)
    floor_id = fields.Int(allow_none=True)
    room_id = fields.Int(allow_none=True)
    location_detail = fields.Str(allow_none=True, validate=validate.Length(max=255))
    status = fields.Str(validate=validate.OneOf(['正常', '故障', '维护', '离线']), missing='正常')
    is_managed = fields.Bool(missing=True)
    serial_number = fields.Str(allow_none=True, validate=validate.Length(max=100))
    firmware_version = fields.Str(allow_none=True, validate=validate.Length(max=50))
    purchase_date = fields.Date(allow_none=True)
    warranty_end_date = fields.Date(allow_none=True)
    description = fields.Str(allow_none=True)


class DevicePortSchema(Schema):
    """设备端口参数验证"""
    device_id = fields.Int(required=True)
    port_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    port_type = fields.Str(allow_none=True, validate=validate.OneOf(['ethernet', 'fiber', 'console', 'management']))
    port_speed = fields.Str(allow_none=True, validate=validate.Length(max=20))
    status = fields.Str(validate=validate.OneOf(['使用中', '未使用', '故障']), missing='未使用')
    vlan_id = fields.Int(allow_none=True)
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))


@network_bp.route('/devices', methods=['GET'])
@login_required
@permission_required('device:view')
def get_devices():
    """获取网络设备列表"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    # 查询参数
    filters = {}
    for field in ['name', 'device_type', 'brand', 'model', 'status']:
        value = request.args.get(field, '').strip()
        if value:
            filters[field] = value
    
    # 位置过滤
    building_id = request.args.get('building_id', type=int)
    floor_id = request.args.get('floor_id', type=int)
    room_id = request.args.get('room_id', type=int)
    
    if building_id:
        filters['building_id'] = building_id
    if floor_id:
        filters['floor_id'] = floor_id
    if room_id:
        filters['room_id'] = room_id
    
    pagination = NetworkDevice.paginate(page=page, per_page=page_size, **filters)
    
    devices = [device.to_dict() for device in pagination.items]
    
    return ApiResponse.page_success(
        devices,
        pagination.total,
        page,
        page_size,
        "获取设备列表成功"
    )


@network_bp.route('/devices/<int:device_id>', methods=['GET'])
@login_required
@permission_required('device:view')
def get_device(device_id):
    """获取设备详情"""
    device = NetworkDevice.find_by_id(device_id)
    if not device:
        raise ResourceNotFoundError("设备不存在")
    
    device_dict = device.to_dict()
    device_dict['ports'] = [port.to_dict() for port in device.ports.filter_by(is_deleted=False).all()]
    
    return ApiResponse.success(device_dict, "获取设备详情成功")


@network_bp.route('/devices', methods=['POST'])
@login_required
@permission_required('device:manage')
@log_operation("创建网络设备")
def create_device():
    """创建网络设备"""
    try:
        schema = NetworkDeviceSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 验证IP地址格式
    if data.get('ip_address'):
        if not validate_ip_address(data['ip_address']):
            raise CustomValidationError("IP地址格式无效")
        
        # 检查IP地址是否已被使用
        if NetworkDevice.query.filter_by(ip_address=data['ip_address'], is_deleted=False).first():
            raise CustomValidationError("IP地址已被使用")
    
    # 验证MAC地址格式
    if data.get('mac_address'):
        if not validate_mac_address(data['mac_address']):
            raise CustomValidationError("MAC地址格式无效")
        
        # 检查MAC地址是否已被使用
        if NetworkDevice.query.filter_by(mac_address=data['mac_address'], is_deleted=False).first():
            raise CustomValidationError("MAC地址已被使用")
    
    # 验证位置信息
    if data.get('room_id'):
        room = Room.find_by_id(data['room_id'])
        if not room:
            raise ResourceNotFoundError("房间不存在")
        data['floor_id'] = room.floor_id
        data['building_id'] = room.floor.building_id
    elif data.get('floor_id'):
        floor = Floor.find_by_id(data['floor_id'])
        if not floor:
            raise ResourceNotFoundError("楼层不存在")
        data['building_id'] = floor.building_id
    elif data.get('building_id'):
        building = Building.find_by_id(data['building_id'])
        if not building:
            raise ResourceNotFoundError("楼宇不存在")
    
    device = NetworkDevice(**data)
    
    try:
        device.save()
        return ApiResponse.success(device.to_dict(), "设备创建成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("设备创建失败")


@network_bp.route('/devices/<int:device_id>', methods=['PUT'])
@login_required
@permission_required('device:manage')
@log_operation("更新网络设备")
def update_device(device_id):
    """更新网络设备"""
    device = NetworkDevice.find_by_id(device_id)
    if not device:
        raise ResourceNotFoundError("设备不存在")
    
    try:
        schema = NetworkDeviceSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 验证IP地址
    if data.get('ip_address') and data['ip_address'] != device.ip_address:
        if not validate_ip_address(data['ip_address']):
            raise CustomValidationError("IP地址格式无效")
        
        if NetworkDevice.query.filter_by(ip_address=data['ip_address'], is_deleted=False).filter(NetworkDevice.id != device_id).first():
            raise CustomValidationError("IP地址已被使用")
    
    # 验证MAC地址
    if data.get('mac_address') and data['mac_address'] != device.mac_address:
        if not validate_mac_address(data['mac_address']):
            raise CustomValidationError("MAC地址格式无效")
        
        if NetworkDevice.query.filter_by(mac_address=data['mac_address'], is_deleted=False).filter(NetworkDevice.id != device_id).first():
            raise CustomValidationError("MAC地址已被使用")
    
    # 验证位置信息
    if data.get('room_id'):
        room = Room.find_by_id(data['room_id'])
        if not room:
            raise ResourceNotFoundError("房间不存在")
        data['floor_id'] = room.floor_id
        data['building_id'] = room.floor.building_id
    elif data.get('floor_id'):
        floor = Floor.find_by_id(data['floor_id'])
        if not floor:
            raise ResourceNotFoundError("楼层不存在")
        data['building_id'] = floor.building_id
    elif data.get('building_id'):
        building = Building.find_by_id(data['building_id'])
        if not building:
            raise ResourceNotFoundError("楼宇不存在")
    
    # 更新设备信息
    for key, value in data.items():
        setattr(device, key, value)
    
    device.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(device.to_dict(), "设备更新成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("设备更新失败")


@network_bp.route('/devices/<int:device_id>', methods=['DELETE'])
@login_required
@permission_required('device:manage')
@log_operation("删除网络设备")
def delete_device(device_id):
    """删除网络设备"""
    device = NetworkDevice.find_by_id(device_id)
    if not device:
        raise ResourceNotFoundError("设备不存在")
    
    # 检查是否有连接的端口
    connected_ports = device.ports.filter_by(is_connected=True, is_deleted=False).first()
    if connected_ports:
        raise CustomValidationError("设备存在连接的端口，请先断开连接")
    
    device.delete()
    return ApiResponse.success(message="设备删除成功")


@network_bp.route('/devices/<int:device_id>/ports', methods=['GET'])
@login_required
@permission_required('device:view')
def get_device_ports(device_id):
    """获取设备端口列表"""
    device = NetworkDevice.find_by_id(device_id)
    if not device:
        raise ResourceNotFoundError("设备不存在")
    
    ports = device.ports.filter_by(is_deleted=False).all()
    port_list = [port.to_dict() for port in ports]
    
    return ApiResponse.success(port_list, "获取端口列表成功")


@network_bp.route('/devices/<int:device_id>/ports', methods=['POST'])
@login_required
@permission_required('device:manage')
@log_operation("创建设备端口")
def create_device_port(device_id):
    """创建设备端口"""
    device = NetworkDevice.find_by_id(device_id)
    if not device:
        raise ResourceNotFoundError("设备不存在")
    
    try:
        schema = DevicePortSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 确保device_id正确
    data['device_id'] = device_id
    
    # 检查端口名称在同一设备内是否已存在
    if DevicePort.query.filter_by(
        device_id=device_id,
        port_name=data['port_name'],
        is_deleted=False
    ).first():
        raise CustomValidationError("端口名称在该设备内已存在")
    
    port = DevicePort(**data)
    
    try:
        port.save()
        return ApiResponse.success(port.to_dict(), "端口创建成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("端口创建失败")


@network_bp.route('/ports/<int:port_id>/connect', methods=['POST'])
@login_required
@permission_required('device:manage')
@log_operation("连接设备端口")
def connect_ports(port_id):
    """连接端口"""
    port = DevicePort.find_by_id(port_id)
    if not port:
        raise ResourceNotFoundError("端口不存在")
    
    data = request.json or {}
    target_port_id = data.get('target_port_id')
    
    if not target_port_id:
        raise CustomValidationError("目标端口ID不能为空")
    
    target_port = DevicePort.find_by_id(target_port_id)
    if not target_port:
        raise ResourceNotFoundError("目标端口不存在")
    
    if port.device_id == target_port.device_id:
        raise CustomValidationError("不能连接同一设备的端口")
    
    try:
        port.connect_to_port(target_port)
        return ApiResponse.success({
            'port': port.to_dict(),
            'target_port': target_port.to_dict()
        }, "端口连接成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("端口连接失败")


@network_bp.route('/ports/<int:port_id>/disconnect', methods=['POST'])
@login_required
@permission_required('device:manage')
@log_operation("断开设备端口")
def disconnect_port(port_id):
    """断开端口连接"""
    port = DevicePort.find_by_id(port_id)
    if not port:
        raise ResourceNotFoundError("端口不存在")
    
    if not port.is_connected:
        raise CustomValidationError("端口未连接")
    
    try:
        port.disconnect()
        return ApiResponse.success(port.to_dict(), "端口断开成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("端口断开失败")


@network_bp.route('/topology', methods=['GET'])
@login_required
@permission_required('topology:view')
def get_network_topology():
    """获取网络拓扑（支持资产数据）"""
    from app.models.asset import Asset
    from app.utils.network_device_config import NetworkDeviceConfig
    
    # 获取所有拓扑设备（只包括可用于生成拓扑图的设备）
    topology_categories = NetworkDeviceConfig.get_topology_categories()
    topology_assets = Asset.query.filter(
        Asset.category.in_(topology_categories),
        Asset.is_deleted == False
    ).all()
    
    # 获取终端设备（作为连接端点）
    terminal_categories = NetworkDeviceConfig.get_terminal_categories() 
    terminal_assets = Asset.query.filter(
        Asset.category.in_(terminal_categories),
        Asset.is_deleted == False,
        Asset.ip_address.isnot(None)  # 只显示有IP的终端设备
    ).all()
    
    # 获取传统网络设备（兼容旧数据）
    legacy_devices = NetworkDevice.query.filter_by(is_deleted=False, is_managed=True).all()
    
    # 构建拓扑数据
    nodes = []
    edges = []
    
    # 处理拓扑设备
    for asset in topology_assets:
        node = asset.get_topology_data()
        if node:
            node['device_category'] = 'topology'
            node['icon'] = NetworkDeviceConfig.get_device_icon(asset.category)
            node['color'] = NetworkDeviceConfig.get_device_color(asset.category)
            nodes.append(node)
    
    # 处理终端设备
    for asset in terminal_assets:
        node = asset.get_topology_data()
        if node:
            node['device_category'] = 'terminal'
            node['icon'] = NetworkDeviceConfig.get_device_icon(asset.category)
            node['color'] = NetworkDeviceConfig.get_device_color(asset.category)
            nodes.append(node)
    
    # 处理传统网络设备（如果没有对应的资产记录）
    for device in legacy_devices:
        # 检查是否已经有对应的资产记录
        existing_asset = Asset.query.filter(
            Asset.name == device.name,
            Asset.ip_address == device.ip_address,
            Asset.is_deleted == False
        ).first()
        
        if not existing_asset:
            node = device.get_topology_data()
            node['legacy'] = True  # 标记为传统设备
            node['device_category'] = 'legacy'
            node['icon'] = '📶'  # 传统设备图标
            node['color'] = '#c0c4cc'  # 灰色
            nodes.append(node)
    
    # 构建连接关系逻辑保持不变...
    processed_connections = set()
    
    # 处理资产设备的连接
    for asset in topology_assets + terminal_assets:
        if hasattr(asset, 'device_ports'):
            for port in asset.device_ports.filter_by(is_deleted=False, is_connected=True).all():
                if port.connected_port_id:
                    connection_key = tuple(sorted([port.id, port.connected_port_id]))
                    if connection_key not in processed_connections:
                        # 获取连接的设备信息
                        connected_device_id = None
                        if port.connected_port and port.connected_port.asset_device_id:
                            connected_device_id = port.connected_port.asset_device_id
                        elif port.connected_port and port.connected_port.device_id:
                            # 兼容传统设备
                            connected_device_id = f"legacy_{port.connected_port.device_id}"
                        
                        if connected_device_id:
                            edge = {
                                'source': asset.id,
                                'target': connected_device_id,
                                'source_port': port.port_name,
                                'target_port': port.connected_port.port_name if port.connected_port else '',
                                'type': 'network'
                            }
                            edges.append(edge)
                            processed_connections.add(connection_key)
    
    # 处理传统设备的连接逻辑保持不变...
    for device in legacy_devices:
        existing_asset = Asset.query.filter(
            Asset.name == device.name,
            Asset.ip_address == device.ip_address,
            Asset.is_deleted == False
        ).first()
        
        if not existing_asset:
            for port in device.ports.filter_by(is_deleted=False, is_connected=True).all():
                if port.connected_port_id:
                    connection_key = tuple(sorted([port.id, port.connected_port_id]))
                    if connection_key not in processed_connections:
                        edge = {
                            'source': f"legacy_{device.id}",
                            'target': f"legacy_{port.connected_device_id}" if port.connected_device_id else None,
                            'source_port': port.port_name,
                            'target_port': port.connected_port.port_name if port.connected_port else '',
                            'type': 'network'
                        }
                        if edge['target']:
                            edges.append(edge)
                            processed_connections.add(connection_key)
    
    topology_data = {
        'nodes': nodes,
        'edges': edges,
        'updated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'mixed_mode': True,  # 标记为混合模式
        'topology_count': len(topology_assets),
        'terminal_count': len(terminal_assets),
        'legacy_count': len([n for n in nodes if n.get('legacy')])
    }
    
    return ApiResponse.success(topology_data, "获取网络拓扑成功")


@network_bp.route('/topology/save', methods=['POST'])
@login_required
@permission_required('topology:edit')
@log_operation("保存网络拓扑")
def save_network_topology():
    """保存网络拓扑（支持资产数据）"""
    data = request.json or {}
    name = data.get('name', '默认拓扑')
    description = data.get('description', '')
    topology_data = data.get('topology_data')
    
    if not topology_data:
        raise CustomValidationError("拓扑数据不能为空")
    
    from app.models.asset import Asset
    
    # 更新设备位置坐标
    nodes = topology_data.get('nodes', [])
    for node in nodes:
        device_id = node.get('id')
        x = node.get('x', 0)
        y = node.get('y', 0)
        is_legacy = node.get('legacy', False)
        
        if is_legacy:
            # 处理传统设备
            if isinstance(device_id, str) and device_id.startswith('legacy_'):
                legacy_id = int(device_id.replace('legacy_', ''))
                device = NetworkDevice.find_by_id(legacy_id)
                if device:
                    device.x_position = x
                    device.y_position = y
        else:
            # 处理资产设备
            asset = Asset.find_by_id(device_id)
            if asset:
                asset.x_position = x
                asset.y_position = y
    
    # 保存拓扑配置
    topology = NetworkTopology(
        name=name,
        description=description,
        topology_data=str(topology_data)
    )
    
    try:
        db.session.commit()
        topology.save()
        return ApiResponse.success(topology.to_dict(), "拓扑保存成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("拓扑保存失败")


@network_bp.route('/devices/search', methods=['GET'])
@login_required
@permission_required('device:view')
def search_devices():
    """搜索设备"""
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return ApiResponse.success([], "搜索关键字不能为空")
    
    from app.models.asset import Asset
    from app.utils.network_device_config import NetworkDeviceConfig
    
    # 搜索资产设备
    all_categories = (NetworkDeviceConfig.get_topology_categories() + 
                     NetworkDeviceConfig.get_terminal_categories())
    
    assets = Asset.query.filter(
        Asset.category.in_(all_categories),
        Asset.is_deleted == False,
        db.or_(
            Asset.name.contains(keyword),
            Asset.ip_address.contains(keyword),
            Asset.model.contains(keyword)
        )
    ).all()
    
    # 搜索传统网络设备
    legacy_devices = NetworkDevice.query.filter(
        NetworkDevice.is_deleted == False,
        db.or_(
            NetworkDevice.name.contains(keyword),
            NetworkDevice.ip_address.contains(keyword),
            NetworkDevice.model.contains(keyword)
        )
    ).all()
    
    results = []
    
    # 处理资产设备结果
    for asset in assets:
        node = asset.get_topology_data()
        if node:
            node['highlighted'] = True
            results.append(node)
    
    # 处理传统设备结果
    for device in legacy_devices:
        node = device.get_topology_data()
        node['highlighted'] = True
        node['legacy'] = True
        results.append(node)
    
    return ApiResponse.success(results, f"找到{len(results)}个设备")


@network_bp.route('/devices/legacy/<int:device_id>', methods=['GET'])
@login_required
@permission_required('device:view')
def get_legacy_device_details(device_id):
    """获取传统设备详情"""
    device = NetworkDevice.find_by_id(device_id)
    if not device:
        raise ResourceNotFoundError("设备不存在")
    
    device_data = device.get_topology_data()
    device_data['legacy'] = True
    
    return ApiResponse.success(device_data, "获取设备详情成功")


@network_bp.route('/devices/<int:device_id>/position', methods=['PUT'])
@login_required
@permission_required('device:manage')
@log_operation("更新设备位置")
def update_device_position(device_id):
    """更新资产设备位置"""
    from app.models.asset import Asset
    
    asset = Asset.find_by_id(device_id)
    if not asset:
        raise ResourceNotFoundError("设备不存在")
    
    data = request.json or {}
    x = data.get('x', 0)
    y = data.get('y', 0)
    
    asset.x_position = x
    asset.y_position = y
    asset.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(message="设备位置更新成功")
    except Exception:
        db.session.rollback()
        raise CustomValidationError("设备位置更新失败")


@network_bp.route('/devices/legacy/<int:device_id>/position', methods=['PUT'])
@login_required
@permission_required('device:manage') 
@log_operation("更新传统设备位置")
def update_legacy_device_position(device_id):
    """更新传统设备位置"""
    device = NetworkDevice.find_by_id(device_id)
    if not device:
        raise ResourceNotFoundError("设备不存在")
    
    data = request.json or {}
    x = data.get('x', 0)
    y = data.get('y', 0)
    
    device.x_position = x
    device.y_position = y
    device.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(message="设备位置更新成功")
    except Exception:
        db.session.rollback()
        raise CustomValidationError("设备位置更新失败")


@network_bp.route('/topology/positions', methods=['PUT'])
@login_required
@permission_required('device:manage')
@log_operation("批量更新设备位置")
def batch_update_positions():
    """批量更新设备位置"""
    data = request.json or {}
    positions = data.get('positions', [])
    
    if not positions:
        raise CustomValidationError("位置数据不能为空")
    
    from app.models.asset import Asset
    
    try:
        for pos in positions:
            device_id = pos.get('id')
            x = pos.get('x', 0)
            y = pos.get('y', 0)
            is_legacy = pos.get('isLegacy', False)
            
            if is_legacy:
                device = NetworkDevice.find_by_id(device_id)
                if device:
                    device.x_position = x
                    device.y_position = y
                    device.updated_at = datetime.utcnow()
            else:
                asset = Asset.find_by_id(device_id)
                if asset:
                    asset.x_position = x
                    asset.y_position = y
                    asset.updated_at = datetime.utcnow()
        
        db.session.commit()
        return ApiResponse.success(message=f"成功更新{len(positions)}个设备位置")
        
    except Exception:
        db.session.rollback()
        raise CustomValidationError("批量更新设备位置失败")


@network_bp.route('/topology/config', methods=['GET'])
@login_required
@permission_required('topology:view')
def get_topology_config():
    """获取拓扑配置"""
    # 返回默认配置，可以后续扩展为数据库存储
    config = {
        'layout_algorithm': 'force',
        'show_ports': False,
        'show_labels': True, 
        'show_ips': True,
        'auto_refresh': False,
        'refresh_interval': 30,
        'node_size': 30,
        'edge_width': 2,
        'show_device_icons': True,
        'color_by_status': True
    }
    
    return ApiResponse.success(config, "获取拓扑配置成功")


@network_bp.route('/topology/config', methods=['POST'])
@login_required
@permission_required('topology:edit')
@log_operation("保存拓扑配置")
def save_topology_config():
    """保存拓扑配置"""
    config = request.json or {}
    
    # 这里可以将配置保存到数据库或配置文件
    # 暂时只做参数验证
    allowed_algorithms = ['force', 'circular', 'grid', 'manual']
    if config.get('layout_algorithm') not in allowed_algorithms:
        raise CustomValidationError("无效的布局算法")
    
    return ApiResponse.success(message="拓扑配置保存成功")


@network_bp.route('/topology/auto-layout', methods=['POST'])
@login_required
@permission_required('topology:edit')
@log_operation("自动布局拓扑")
def auto_layout_topology():
    """自动布局拓扑"""
    data = request.json or {}
    algorithm = data.get('algorithm', 'force')
    
    from app.models.asset import Asset
    from app.utils.network_device_config import NetworkDeviceConfig
    import math
    
    # 获取所有设备
    topology_categories = NetworkDeviceConfig.get_topology_categories()
    terminal_categories = NetworkDeviceConfig.get_terminal_categories()
    
    assets = Asset.query.filter(
        Asset.category.in_(topology_categories + terminal_categories),
        Asset.is_deleted == False
    ).all()
    
    legacy_devices = NetworkDevice.query.filter_by(is_deleted=False, is_managed=True).all()
    
    all_nodes = []
    
    # 处理资产设备
    for asset in assets:
        node = asset.get_topology_data()
        if node:
            all_nodes.append({
                'id': asset.id,
                'type': 'asset',
                'data': asset
            })
    
    # 处理传统设备
    for device in legacy_devices:
        all_nodes.append({
            'id': device.id,
            'type': 'legacy', 
            'data': device
        })
    
    # 应用布局算法
    if algorithm == 'circular':
        center_x, center_y = 400, 300
        radius = min(200, len(all_nodes) * 30)
        
        for i, node in enumerate(all_nodes):
            angle = (i * 2 * math.pi) / len(all_nodes)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            if node['type'] == 'asset':
                node['data'].x_position = x
                node['data'].y_position = y
            else:
                node['data'].x_position = x
                node['data'].y_position = y
                
    elif algorithm == 'grid':
        cols = math.ceil(math.sqrt(len(all_nodes)))
        spacing = 100
        
        for i, node in enumerate(all_nodes):
            x = (i % cols) * spacing + 100
            y = (i // cols) * spacing + 100
            
            if node['type'] == 'asset':
                node['data'].x_position = x
                node['data'].y_position = y
            else:
                node['data'].x_position = x
                node['data'].y_position = y
    
    # 保存位置更新
    try:
        db.session.commit()
        
        # 返回更新后的节点位置
        updated_nodes = []
        for node in all_nodes:
            updated_nodes.append({
                'id': node['data'].id,
                'x': node['data'].x_position,
                'y': node['data'].y_position,
                'legacy': node['type'] == 'legacy'
            })
        
        return ApiResponse.success({
            'nodes': updated_nodes
        }, f"使用{algorithm}算法自动布局成功")
        
    except Exception:
        db.session.rollback()
        raise CustomValidationError("自动布局失败")


@network_bp.route('/devices/<int:device_id>/fault', methods=['POST'])
@login_required
@permission_required('fault:handle')
@log_operation("标记设备故障")
def mark_device_fault(device_id):
    """标记设备故障"""
    device = NetworkDevice.find_by_id(device_id)
    if not device:
        raise ResourceNotFoundError("设备不存在")
    
    data = request.json or {}
    fault_description = data.get('description', '')
    
    # 更新设备状态
    device.status = '故障'
    device.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # 创建故障记录（这里简化处理，实际应该调用故障分析模块）
        from app.models.fault import FaultRecord
        from app.utils.helpers import generate_fault_code
        from flask_jwt_extended import get_jwt_identity
        
        fault = FaultRecord(
            fault_code=generate_fault_code(),
            title=f'{device.name}设备故障',
            description=fault_description,
            fault_type='网络故障',
            severity='中',
            source_type='device',
            source_id=device_id,
            fault_time=datetime.utcnow(),
            building_id=device.building_id,
            floor_id=device.floor_id,
            room_id=device.room_id,
            reporter_id=get_jwt_identity()
        )
        fault.save()
        
        return ApiResponse.success({
            'device': device.to_dict(),
            'fault': fault.to_dict()
        }, "设备故障标记成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("故障标记失败")