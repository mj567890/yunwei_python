"""
资产管理API
"""
import os
from datetime import datetime
from flask import Blueprint, request, send_file, current_app
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.utils import secure_filename

from app.models.asset import Asset, AssetStatusLog, AssetCategory
from app.models.location import Building, Floor, Room
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required, log_operation
from app.utils.exceptions import ValidationError as CustomValidationError, ResourceNotFoundError
from app.utils.helpers import generate_asset_code, allowed_file, validate_ip_address, validate_mac_address
from app.utils.excel import AssetExcelProcessor
from app import db

asset_bp = Blueprint('asset', __name__)


class AssetSchema(Schema):
    """资产参数验证"""
    asset_code = fields.Str(allow_none=True, validate=validate.Length(max=50))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    brand = fields.Str(allow_none=True, validate=validate.Length(max=50))
    model = fields.Str(allow_none=True, validate=validate.Length(max=100))
    category = fields.Str(required=True, validate=validate.Length(max=50))
    specification = fields.Str(allow_none=True)
    
    # 位置信息
    building_id = fields.Int(allow_none=True)
    floor_id = fields.Int(allow_none=True)
    room_id = fields.Int(allow_none=True)
    location_detail = fields.Str(allow_none=True, validate=validate.Length(max=255))
    
    # 采购信息
    supplier = fields.Str(allow_none=True, validate=validate.Length(max=100))
    purchase_date = fields.Date(allow_none=True)
    purchase_price = fields.Decimal(allow_none=True, places=2)
    purchase_order = fields.Str(allow_none=True, validate=validate.Length(max=50))
    
    # 保修信息
    warranty_start_date = fields.Date(allow_none=True)
    warranty_end_date = fields.Date(allow_none=True)
    warranty_period = fields.Int(allow_none=True)
    
    # 使用信息
    user_name = fields.Str(allow_none=True, validate=validate.Length(max=50))
    user_department = fields.Str(allow_none=True, validate=validate.Length(max=50))
    deploy_date = fields.Date(allow_none=True)
    
    # 状态信息
    status = fields.Str(validate=validate.OneOf(['在用', '闲置', '维修', '报废']), missing='在用')
    condition_rating = fields.Str(allow_none=True, validate=validate.OneOf(['优', '良', '中', '差']))
    
    # 其他信息
    serial_number = fields.Str(allow_none=True, validate=validate.Length(max=100))
    mac_address = fields.Str(allow_none=True, validate=validate.Length(max=17))
    ip_address = fields.Str(allow_none=True, validate=validate.Length(max=15))
    remark = fields.Str(allow_none=True)
    
    # 网络设备专用字段
    device_type = fields.Str(allow_none=True, validate=validate.OneOf(['交换机', '路由器', '防火墙', '服务器', '安全设备']))
    subnet_mask = fields.Str(allow_none=True, validate=validate.Length(max=15))
    gateway = fields.Str(allow_none=True, validate=validate.Length(max=15))
    dns_servers = fields.Str(allow_none=True, validate=validate.Length(max=255))
    firmware_version = fields.Str(allow_none=True, validate=validate.Length(max=50))
    port_count = fields.Int(allow_none=True)
    is_managed = fields.Bool(missing=True)
    x_position = fields.Float(allow_none=True)
    y_position = fields.Float(allow_none=True)


@asset_bp.route('', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_assets():
    """获取资产列表"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    # 查询参数
    filters = {}
    for field in ['name', 'brand', 'model', 'category', 'status', 'user_name', 'user_department']:
        value = request.args.get(field, '').strip()
        if value:
            filters[field] = value
    
    # 网络设备过滤（大概念）
    network_devices_filter = request.args.get('network_devices', '').strip()
    if network_devices_filter == 'true':
        from app.utils.network_device_config import NetworkDeviceConfig
        network_categories = NetworkDeviceConfig.get_all_network_categories()
        # 使用 in_ 过滤器
        filters['category__in'] = network_categories
    
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
    
    # 保修状态过滤
    warranty_status = request.args.get('warranty_status')
    
    # 构建查询
    query = Asset.query.filter_by(is_deleted=False)
    
    # 应用过滤条件
    for key, value in filters.items():
        if key == 'category__in':
            # 特殊处理 in 查询
            query = query.filter(Asset.category.in_(value))
        elif hasattr(Asset, key):
            query = query.filter(getattr(Asset, key).like(f'%{value}%') if isinstance(value, str) else getattr(Asset, key) == value)
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    assets = []
    for asset in pagination.items:
        asset_dict = asset.to_dict()
        
        # 保修状态过滤
        if warranty_status:
            if warranty_status == 'expiring' and not asset.is_warranty_expiring():
                continue
            elif warranty_status == 'expired' and asset.get_warranty_status() != '已过保':
                continue
            elif warranty_status == 'valid' and asset.get_warranty_status() != '保修中':
                continue
        
        assets.append(asset_dict)
    
    return ApiResponse.page_success(
        assets,
        pagination.total,
        page,
        page_size,
        "获取资产列表成功"
    )


@asset_bp.route('/<int:asset_id>', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_asset(asset_id):
    """获取资产详情"""
    asset = Asset.find_by_id(asset_id)
    if not asset:
        raise ResourceNotFoundError("资产不存在")
    
    # 获取状态变更历史
    status_logs = asset.status_logs.order_by(AssetStatusLog.created_at.desc()).limit(10).all()
    
    asset_dict = asset.to_dict()
    asset_dict['status_logs'] = [log.to_dict() for log in status_logs]
    
    return ApiResponse.success(asset_dict, "获取资产详情成功")


@asset_bp.route('', methods=['POST'])
@login_required
@permission_required('asset:create')
@log_operation("创建资产")
def create_asset():
    """创建资产"""
    try:
        schema = AssetSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 生成资产编码
    if not data.get('asset_code'):
        # 获取同类别资产数量来生成编码
        category_count = Asset.query.filter_by(category=data['category'], is_deleted=False).count()
        data['asset_code'] = generate_asset_code(data['category'], category_count)
    
    # 检查资产编码是否已存在
    if Asset.query.filter_by(asset_code=data['asset_code'], is_deleted=False).first():
        raise CustomValidationError("资产编码已存在")
    
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
    
    # 验证IP和MAC地址格式
    if data.get('ip_address') and not validate_ip_address(data['ip_address']):
        raise CustomValidationError("IP地址格式无效")
    
    if data.get('mac_address') and not validate_mac_address(data['mac_address']):
        raise CustomValidationError("MAC地址格式无效")
    
    # 创建资产
    asset = Asset(**data)
    
    try:
        asset.save()
        return ApiResponse.success(asset.to_dict(), "资产创建成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建资产失败: {str(e)}")
        raise CustomValidationError("资产创建失败")


@asset_bp.route('/<int:asset_id>', methods=['PUT'])
@login_required
@permission_required('asset:edit')
@log_operation("更新资产")
def update_asset(asset_id):
    """更新资产"""
    asset = Asset.find_by_id(asset_id)
    if not asset:
        raise ResourceNotFoundError("资产不存在")
    
    try:
        schema = AssetSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查资产编码是否已被其他资产使用
    if data.get('asset_code') and data['asset_code'] != asset.asset_code:
        if Asset.query.filter_by(asset_code=data['asset_code'], is_deleted=False).filter(Asset.id != asset_id).first():
            raise CustomValidationError("资产编码已被使用")
    
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
    
    # 验证IP和MAC地址格式
    if data.get('ip_address') and not validate_ip_address(data['ip_address']):
        raise CustomValidationError("IP地址格式无效")
    
    if data.get('mac_address') and not validate_mac_address(data['mac_address']):
        raise CustomValidationError("MAC地址格式无效")
    
    # 检查状态变更
    old_status = asset.status
    new_status = data.get('status', asset.status)
    
    # 更新资产信息
    for key, value in data.items():
        setattr(asset, key, value)
    
    asset.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # 记录状态变更
        if old_status != new_status:
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            asset.change_status(new_status, f"状态从'{old_status}'变更为'{new_status}'", user_id)
        
        return ApiResponse.success(asset.to_dict(), "资产更新成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新资产失败: {str(e)}")
        raise CustomValidationError("资产更新失败")


@asset_bp.route('/<int:asset_id>', methods=['DELETE'])
@login_required
@permission_required('asset:delete')
@log_operation("删除资产")
def delete_asset(asset_id):
    """删除资产"""
    asset = Asset.find_by_id(asset_id)
    if not asset:
        raise ResourceNotFoundError("资产不存在")
    
    asset.delete()
    return ApiResponse.success(message="资产删除成功")


@asset_bp.route('/<int:asset_id>/change-status', methods=['POST'])
@login_required
@permission_required('asset:edit')
@log_operation("变更资产状态")
def change_asset_status(asset_id):
    """变更资产状态"""
    asset = Asset.find_by_id(asset_id)
    if not asset:
        raise ResourceNotFoundError("资产不存在")
    
    data = request.json or {}
    new_status = data.get('status')
    remark = data.get('remark')
    
    if not new_status:
        raise CustomValidationError("新状态不能为空")
    
    if new_status not in ['在用', '闲置', '维修', '报废']:
        raise CustomValidationError("无效的状态值")
    
    if new_status == asset.status:
        raise CustomValidationError("新状态与当前状态相同")
    
    try:
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        
        status_log = asset.change_status(new_status, remark, user_id)
        
        return ApiResponse.success({
            'asset': asset.to_dict(),
            'status_log': status_log.to_dict()
        }, "状态变更成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"变更资产状态失败: {str(e)}")
        raise CustomValidationError("状态变更失败")


@asset_bp.route('/categories', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_asset_categories():
    """获取资产类别"""
    categories = AssetCategory.find_all()
    
    # 构建树形结构
    category_tree = []
    category_map = {}
    
    # 先创建所有节点
    for category in categories:
        node = category.to_dict()
        node['children'] = []
        category_map[category.id] = node
    
    # 构建树形结构
    for category in categories:
        node = category_map[category.id]
        if category.parent_id and category.parent_id in category_map:
            category_map[category.parent_id]['children'].append(node)
        else:
            category_tree.append(node)
    
    return ApiResponse.success(category_tree, "获取资产类别成功")


@asset_bp.route('/export', methods=['GET'])
@login_required
@permission_required('asset:import_export')
@log_operation("导出资产数据")
def export_assets():
    """导出资产数据"""
    # 获取查询参数
    filters = {}
    for field in ['category', 'status', 'building_id', 'floor_id', 'room_id']:
        value = request.args.get(field)
        if value:
            if field in ['building_id', 'floor_id', 'room_id']:
                filters[field] = int(value)
            else:
                filters[field] = value
    
    # 查询资产数据
    query = Asset.query.filter_by(is_deleted=False)
    
    for key, value in filters.items():
        if hasattr(Asset, key):
            query = query.filter(getattr(Asset, key) == value)
    
    assets = query.all()
    asset_list = [asset.to_dict() for asset in assets]
    
    # 生成Excel文件
    try:
        processor = AssetExcelProcessor()
        excel_stream = processor.export_assets(asset_list)
        
        filename = f"assets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            excel_stream,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        current_app.logger.error(f"导出资产数据失败: {str(e)}")
        raise CustomValidationError("导出失败")


@asset_bp.route('/import-template', methods=['GET'])
@login_required
@permission_required('asset:import_export')
def download_import_template():
    """下载导入模板"""
    try:
        processor = AssetExcelProcessor()
        excel_stream = processor.generate_template()
        
        filename = "asset_import_template.xlsx"
        
        return send_file(
            excel_stream,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        current_app.logger.error(f"生成导入模板失败: {str(e)}")
        raise CustomValidationError("模板生成失败")


@asset_bp.route('/import', methods=['POST'])
@login_required
@permission_required('asset:import_export')
@log_operation("导入资产数据")
def import_assets():
    """导入资产数据"""
    if 'file' not in request.files:
        raise CustomValidationError("请选择要导入的文件")
    
    file = request.files['file']
    if file.filename == '':
        raise CustomValidationError("请选择要导入的文件")
    
    if not allowed_file(file.filename, {'xlsx', 'xls'}):
        raise CustomValidationError("只支持Excel文件格式")
    
    try:
        # 解析Excel文件
        processor = AssetExcelProcessor()
        result = processor.import_assets(file.stream)
        
        if not result['success']:
            return ApiResponse.error(result['message'])
        
        import_data = result['data']
        assets_data = import_data['assets']
        errors = import_data['errors']
        
        # 批量导入资产
        success_count = 0
        failed_count = 0
        import_errors = []
        
        for i, asset_data in enumerate(assets_data):
            try:
                # 检查资产编码是否已存在
                if Asset.query.filter_by(asset_code=asset_data['asset_code'], is_deleted=False).first():
                    import_errors.append(f"资产编码 {asset_data['asset_code']} 已存在")
                    failed_count += 1
                    continue
                
                # 解析位置信息
                if asset_data.get('building_name'):
                    building = Building.query.filter_by(name=asset_data['building_name'], is_deleted=False).first()
                    if building:
                        asset_data['building_id'] = building.id
                        
                        if asset_data.get('floor_name'):
                            floor = Floor.query.filter_by(
                                building_id=building.id,
                                name=asset_data['floor_name'],
                                is_deleted=False
                            ).first()
                            if floor:
                                asset_data['floor_id'] = floor.id
                                
                                if asset_data.get('room_name'):
                                    room = Room.query.filter_by(
                                        floor_id=floor.id,
                                        name=asset_data['room_name'],
                                        is_deleted=False
                                    ).first()
                                    if room:
                                        asset_data['room_id'] = room.id
                
                # 移除位置名称字段
                for field in ['building_name', 'floor_name', 'room_name']:
                    asset_data.pop(field, None)
                
                # 创建资产
                asset = Asset(**asset_data)
                asset.save()
                success_count += 1
                
            except Exception as e:
                import_errors.append(f"资产 {asset_data.get('asset_code', f'第{i+1}行')} 导入失败: {str(e)}")
                failed_count += 1
                db.session.rollback()
        
        return ApiResponse.success({
            'total_rows': import_data['total_rows'],
            'valid_rows': import_data['valid_rows'],
            'success_count': success_count,
            'failed_count': failed_count,
            'parse_errors': errors,
            'import_errors': import_errors
        }, f"导入完成，成功{success_count}条，失败{failed_count}条")
        
    except Exception as e:
        current_app.logger.error(f"导入资产数据失败: {str(e)}")
        raise CustomValidationError("导入失败")


@asset_bp.route('/warranty-alerts', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_warranty_alerts():
    """获取保修预警"""
    days = request.args.get('days', 30, type=int)  # 默认30天内到期
    
    assets = Asset.query.filter_by(is_deleted=False).all()
    expiring_assets = []
    
    for asset in assets:
        if asset.is_warranty_expiring(days):
            asset_dict = asset.to_dict()
            expiring_assets.append(asset_dict)
    
    return ApiResponse.success(expiring_assets, f"获取{days}天内保修到期资产成功")


@asset_bp.route('/statistics', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_asset_statistics():
    """获取资产统计"""
    # 总数统计
    total_count = Asset.query.filter_by(is_deleted=False).count()
    
    # 状态统计
    status_stats = {}
    for status in ['在用', '闲置', '维修', '报废']:
        count = Asset.query.filter_by(status=status, is_deleted=False).count()
        status_stats[status] = count
    
    # 类别统计
    categories = db.session.query(Asset.category, db.func.count(Asset.id)).filter_by(is_deleted=False).group_by(Asset.category).all()
    category_stats = {category: count for category, count in categories}
    
    # 保修状态统计
    warranty_stats = {
        'total': 0,
        'valid': 0,
        'expired': 0,
        'expiring': 0
    }
    
    assets = Asset.query.filter_by(is_deleted=False).all()
    for asset in assets:
        warranty_stats['total'] += 1
        warranty_status = asset.get_warranty_status()
        if warranty_status == '保修中':
            warranty_stats['valid'] += 1
            if asset.is_warranty_expiring():
                warranty_stats['expiring'] += 1
        elif warranty_status == '已过保':
            warranty_stats['expired'] += 1
    
    return ApiResponse.success({
        'total_count': total_count,
        'status_stats': status_stats,
        'category_stats': category_stats,
        'warranty_stats': warranty_stats
    }, "获取资产统计成功")