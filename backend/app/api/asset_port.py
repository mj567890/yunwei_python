#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资产端口管理API
支持端口CRUD、连接管理、拓扑数据生成
"""

from flask import Blueprint, request
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

from app.models.asset_port import AssetPort, PortConnection
from app.models.asset import Asset
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required, log_operation
from app.utils.exceptions import ValidationError as CustomValidationError, ResourceNotFoundError
from app import db

port_bp = Blueprint('port', __name__)


class AssetPortSchema(Schema):
    """资产端口参数验证"""
    asset_id = fields.Int(required=True)
    port_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    port_type = fields.Str(allow_none=True, validate=validate.OneOf(['ethernet', 'fiber', 'console', 'management', 'power', 'usb']))
    port_speed = fields.Str(allow_none=True, validate=validate.OneOf(['10M', '100M', '1G', '10G', '25G', '40G', '100G']))
    port_status = fields.Str(validate=validate.OneOf(['used', 'unused', 'error', 'disabled']), missing='unused')
    port_index = fields.Int(allow_none=True)
    is_uplink = fields.Bool(missing=False)
    duplex_mode = fields.Str(allow_none=True, validate=validate.OneOf(['full', 'half', 'auto']))
    vlan_id = fields.Int(allow_none=True)
    ip_address = fields.Str(allow_none=True, validate=validate.Length(max=15))
    mac_address = fields.Str(allow_none=True, validate=validate.Length(max=17))
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))


class PortConnectionSchema(Schema):
    """端口连接参数验证"""
    source_port_id = fields.Int(required=True)
    target_port_id = fields.Int(required=True)
    cable_type = fields.Str(validate=validate.OneOf(['copper', 'fiber', 'wireless']), missing='copper')
    cable_length = fields.Float(allow_none=True, validate=validate.Range(min=0))
    notes = fields.Str(allow_none=True)


@port_bp.route('/assets/<int:asset_id>/ports', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_asset_ports(asset_id):
    """获取资产的端口列表"""
    asset = Asset.find_by_id(asset_id)
    if not asset:
        raise ResourceNotFoundError("资产不存在")
    
    ports = AssetPort.query.filter_by(asset_id=asset_id, is_deleted=False).order_by(AssetPort.port_index, AssetPort.port_name).all()
    port_list = [port.to_dict() for port in ports]
    
    return ApiResponse.success({
        'asset': {
            'id': asset.id,
            'name': asset.name,
            'category': asset.category
        },
        'ports': port_list,
        'total_count': len(port_list),
        'connected_count': len([p for p in port_list if p.get('is_connected')]),
        'unused_count': len([p for p in port_list if p.get('port_status') == 'unused'])
    }, "获取端口列表成功")


@port_bp.route('/assets/<int:asset_id>/ports', methods=['POST'])
@login_required
@permission_required('asset:edit')
@log_operation("创建端口")
def create_asset_port(asset_id):
    """为资产创建端口"""
    asset = Asset.find_by_id(asset_id)
    if not asset:
        raise ResourceNotFoundError("资产不存在")
    
    try:
        schema = AssetPortSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 确保asset_id正确
    data['asset_id'] = asset_id
    
    # 检查端口名称在同一资产内是否已存在
    if AssetPort.query.filter_by(
        asset_id=asset_id,
        port_name=data['port_name'],
        is_deleted=False
    ).first():
        raise CustomValidationError("端口名称在该资产内已存在")
    
    port = AssetPort(**data)
    
    try:
        port.save()
        return ApiResponse.success(port.to_dict(), "端口创建成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("端口创建失败")


@port_bp.route('/ports/<int:port_id>', methods=['PUT'])
@login_required
@permission_required('asset:edit')
@log_operation("更新端口")
def update_port(port_id):
    """更新端口信息"""
    port = AssetPort.find_by_id(port_id)
    if not port:
        raise ResourceNotFoundError("端口不存在")
    
    try:
        schema = AssetPortSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查端口名称唯一性
    if data.get('port_name') and data['port_name'] != port.port_name:
        if AssetPort.query.filter_by(
            asset_id=port.asset_id,
            port_name=data['port_name'],
            is_deleted=False
        ).filter(AssetPort.id != port_id).first():
            raise CustomValidationError("端口名称在该资产内已存在")
    
    # 更新端口信息
    for key, value in data.items():
        if key != 'asset_id':  # 不允许更改资产ID
            setattr(port, key, value)
    
    port.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(port.to_dict(), "端口更新成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("端口更新失败")


@port_bp.route('/ports/<int:port_id>', methods=['DELETE'])
@login_required
@permission_required('asset:edit')
@log_operation("删除端口")
def delete_port(port_id):
    """删除端口"""
    port = AssetPort.find_by_id(port_id)
    if not port:
        raise ResourceNotFoundError("端口不存在")
    
    # 如果端口已连接，先断开连接
    if port.is_connected:
        port.disconnect()
    
    port.delete()
    return ApiResponse.success(message="端口删除成功")


@port_bp.route('/ports/connect', methods=['POST'])
@login_required
@permission_required('asset:edit')
@log_operation("连接端口")
def connect_ports():
    """连接两个端口"""
    try:
        schema = PortConnectionSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    source_port = AssetPort.find_by_id(data['source_port_id'])
    target_port = AssetPort.find_by_id(data['target_port_id'])
    
    if not source_port:
        raise ResourceNotFoundError("源端口不存在")
    if not target_port:
        raise ResourceNotFoundError("目标端口不存在")
    
    try:
        # 连接端口
        result = source_port.connect_to_port(
            target_port,
            data.get('cable_type', 'copper'),
            data.get('cable_length')
        )
        
        # 记录连接历史
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        
        connection_record = PortConnection(
            source_port_id=source_port.id,
            target_port_id=target_port.id,
            cable_type=data.get('cable_type', 'copper'),
            cable_length=data.get('cable_length'),
            connected_by=user_id,
            notes=data.get('notes'),
            is_active=True
        )
        connection_record.save()
        
        return ApiResponse.success({
            'connection': result,
            'source_port': source_port.to_dict(),
            'target_port': target_port.to_dict(),
            'record_id': connection_record.id
        }, "端口连接成功")
        
    except ValueError as e:
        raise CustomValidationError(str(e))
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("端口连接失败")


@port_bp.route('/ports/<int:port_id>/disconnect', methods=['POST'])
@login_required
@permission_required('asset:edit')
@log_operation("断开端口")
def disconnect_port(port_id):
    """断开端口连接"""
    port = AssetPort.find_by_id(port_id)
    if not port:
        raise ResourceNotFoundError("端口不存在")
    
    if not port.is_connected:
        raise CustomValidationError("端口未连接")
    
    try:
        # 更新连接记录为非活跃状态
        active_connection = PortConnection.query.filter(
            ((PortConnection.source_port_id == port_id) | (PortConnection.target_port_id == port_id)),
            PortConnection.is_active == True
        ).first()
        
        if active_connection:
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            
            active_connection.is_active = False
            active_connection.disconnection_date = datetime.utcnow()
            active_connection.disconnected_by = user_id
        
        # 断开端口
        result = port.disconnect()
        
        return ApiResponse.success({
            'result': result,
            'port': port.to_dict()
        }, "端口断开成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("端口断开失败")


@port_bp.route('/assets/<int:asset_id>/ports/auto-create', methods=['POST'])
@login_required
@permission_required('asset:edit')
@log_operation("自动创建端口")
def auto_create_ports(asset_id):
    """根据资产类别自动创建端口"""
    asset = Asset.find_by_id(asset_id)
    if not asset:
        raise ResourceNotFoundError("资产不存在")
    
    # 获取类别配置
    category_config = asset.get_category_config()
    if not category_config or not category_config.get('default_port_count'):
        raise CustomValidationError("该资产类别未配置默认端口数量")
    
    port_count = category_config['default_port_count']
    data = request.json or {}
    port_name_pattern = data.get('port_name_pattern', 'Port{index}')
    port_type = data.get('port_type', 'ethernet')
    
    created_ports = []
    
    try:
        for i in range(1, port_count + 1):
            port_name = port_name_pattern.format(index=i)
            
            # 检查是否已存在
            if AssetPort.query.filter_by(
                asset_id=asset_id,
                port_name=port_name,
                is_deleted=False
            ).first():
                continue
            
            port = AssetPort(
                asset_id=asset_id,
                port_name=port_name,
                port_type=port_type,
                port_index=i,
                port_status='unused'
            )
            port.save()
            created_ports.append(port.to_dict())
        
        return ApiResponse.success({
            'created_count': len(created_ports),
            'ports': created_ports,
            'asset': {
                'id': asset.id,
                'name': asset.name,
                'category': asset.category
            }
        }, f"成功为 {asset.name} 创建 {len(created_ports)} 个端口")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("自动创建端口失败")


@port_bp.route('/topology/connections', methods=['GET'])
@login_required
@permission_required('topology:view')
def get_topology_connections():
    """获取拓扑连接关系"""
    # 获取所有活跃的端口连接
    connections = db.session.query(AssetPort).filter(
        AssetPort.is_connected == True,
        AssetPort.is_deleted == False
    ).all()
    
    edges = []
    processed_connections = set()
    
    for port in connections:
        if port.connected_port_id and port.connected_port:
            connection_key = tuple(sorted([port.id, port.connected_port_id]))
            if connection_key not in processed_connections:
                edge = {
                    'source_asset_id': port.asset_id,
                    'target_asset_id': port.connected_port.asset_id,
                    'source_port': {
                        'id': port.id,
                        'name': port.port_name,
                        'type': port.port_type
                    },
                    'target_port': {
                        'id': port.connected_port.id,
                        'name': port.connected_port.port_name,
                        'type': port.connected_port.port_type
                    },
                    'cable': {
                        'type': port.cable_type,
                        'length': port.cable_length
                    },
                    'connection_time': port.last_link_time.strftime('%Y-%m-%d %H:%M:%S') if port.last_link_time else None
                }
                edges.append(edge)
                processed_connections.add(connection_key)
    
    return ApiResponse.success({
        'connections': edges,
        'total_count': len(edges),
        'updated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }, "获取拓扑连接关系成功")


@port_bp.route('/connections/history', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_connection_history():
    """获取连接历史记录"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    asset_id = request.args.get('asset_id', type=int)
    
    query = PortConnection.query.filter_by(is_deleted=False)
    
    if asset_id:
        # 查询与指定资产相关的连接
        query = query.join(AssetPort, 
            (PortConnection.source_port_id == AssetPort.id) | 
            (PortConnection.target_port_id == AssetPort.id)
        ).filter(AssetPort.asset_id == asset_id)
    
    query = query.order_by(PortConnection.connection_date.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    connections = [conn.to_dict() for conn in pagination.items]
    
    return ApiResponse.page_success(
        connections,
        pagination.total,
        page,
        page_size,
        "获取连接历史成功"
    )


@port_bp.route('/export', methods=['GET'])
@login_required
@permission_required('asset:view')
def export_ports():
    """导出端口信息"""
    asset_id = request.args.get('asset_id', type=int)
    
    query = AssetPort.query.filter_by(is_deleted=False)
    if asset_id:
        query = query.filter_by(asset_id=asset_id)
    
    ports = query.all()
    
    # 构建导出数据
    export_data = []
    for port in ports:
        export_data.append({
            '资产名称': port.asset.name if port.asset else '',
            '端口名称': port.port_name,
            '端口类型': port.port_type or '',
            '端口速率': port.port_speed or '',
            '端口状态': port.port_status,
            '端口序号': port.port_index or '',
            '是否上联': '是' if port.is_uplink else '否',
            'VLAN_ID': port.vlan_id or '',
            'IP地址': port.ip_address or '',
            'MAC地址': port.mac_address or '',
            '描述': port.description or ''
        })
    
    # 生成Excel文件
    try:
        import pandas as pd
        from io import BytesIO
        
        df = pd.DataFrame(export_data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='端口信息', index=False)
        
        output.seek(0)
        
        from flask import send_file
        filename = f'端口信息_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except ImportError:
        # pandas未安装，返回CSV
        import csv
        from io import StringIO
        
        output = StringIO()
        if export_data:
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
            writer.writeheader()
            writer.writerows(export_data)
        
        from flask import make_response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=ports_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response


@port_bp.route('/import', methods=['POST'])
@login_required
@permission_required('asset:manage')
def import_ports():
    """导入端口信息"""
    if 'file' not in request.files:
        raise CustomValidationError('请选择要导入的文件')
    
    file = request.files['file']
    if file.filename == '':
        raise CustomValidationError('请选择要导入的文件')
    
    asset_id = request.form.get('asset_id', type=int)
    
    try:
        # 读取文件
        if file.filename.endswith('.csv'):
            import pandas as pd
            df = pd.read_csv(file)
        else:
            import pandas as pd
            df = pd.read_excel(file)
        
        created_ports = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 获取资产ID
                current_asset_id = asset_id
                if not current_asset_id and '资产名称' in row:
                    asset = Asset.query.filter_by(name=row['资产名称'], is_deleted=False).first()
                    if asset:
                        current_asset_id = asset.id
                    else:
                        errors.append(f'第{index+2}行: 找不到资产 {row["资产名称"]}')
                        continue
                
                if not current_asset_id:
                    errors.append(f'第{index+2}行: 未指定资产')
                    continue
                
                # 检查端口名称是否已存在
                existing_port = AssetPort.query.filter_by(
                    asset_id=current_asset_id,
                    port_name=row['端口名称'],
                    is_deleted=False
                ).first()
                
                if existing_port:
                    errors.append(f'第{index+2}行: 端口 {row["端口名称"]} 已存在')
                    continue
                
                # 创建端口
                port_data = {
                    'asset_id': current_asset_id,
                    'port_name': row['端口名称'],
                    'port_type': row.get('端口类型'),
                    'port_speed': row.get('端口速率'),
                    'port_status': row.get('端口状态', 'unused'),
                    'port_index': row.get('端口序号') if pd.notna(row.get('端口序号')) else None,
                    'is_uplink': row.get('是否上联') == '是',
                    'vlan_id': row.get('VLAN_ID') if pd.notna(row.get('VLAN_ID')) else None,
                    'ip_address': row.get('IP地址'),
                    'mac_address': row.get('MAC地址'),
                    'description': row.get('描述')
                }
                
                # 验证数据
                schema = AssetPortSchema()
                validated_data = schema.load(port_data)
                
                # 创建端口
                port = AssetPort(**validated_data)
                db.session.add(port)
                created_ports.append(port)
                
            except Exception as e:
                errors.append(f'第{index+2}行: {str(e)}')
        
        # 提交事务
        db.session.commit()
        
        return ApiResponse.success({
            'created': [port.to_dict() for port in created_ports],
            'errors': errors,
            'summary': {
                'total': len(df),
                'created': len(created_ports),
                'failed': len(errors)
            }
        }, f'导入完成：成功 {len(created_ports)} 个，失败 {len(errors)} 个')
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError(f'导入失败: {str(e)}')