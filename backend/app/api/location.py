"""
位置管理API
"""
from flask import Blueprint, request
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

from app.models.location import Building, Floor, Room
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required, log_operation
from app.utils.exceptions import ValidationError as CustomValidationError, ResourceNotFoundError
from app import db

location_bp = Blueprint('location', __name__)


class BuildingSchema(Schema):
    """楼宇参数验证"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    code = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    address = fields.Str(allow_none=True, validate=validate.Length(max=255))
    description = fields.Str(allow_none=True)
    status = fields.Int(validate=validate.OneOf([0, 1]), missing=1)


class FloorSchema(Schema):
    """楼层参数验证"""
    building_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    code = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    floor_number = fields.Int(required=True)
    description = fields.Str(allow_none=True)
    status = fields.Int(validate=validate.OneOf([0, 1]), missing=1)


class RoomSchema(Schema):
    """房间参数验证"""
    floor_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    code = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    room_type = fields.Str(allow_none=True, validate=validate.Length(max=50))
    area = fields.Decimal(allow_none=True, places=2)
    capacity = fields.Int(allow_none=True)
    description = fields.Str(allow_none=True)
    status = fields.Int(validate=validate.OneOf([0, 1]), missing=1)


# ========== 楼宇管理 ==========

@location_bp.route('/buildings', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_buildings():
    """获取楼宇列表"""
    buildings = Building.find_all()
    building_list = [building.to_dict() for building in buildings]
    
    return ApiResponse.success(building_list, "获取楼宇列表成功")


@location_bp.route('/buildings/<int:building_id>', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_building(building_id):
    """获取楼宇详情"""
    building = Building.find_by_id(building_id)
    if not building:
        raise ResourceNotFoundError("楼宇不存在")
    
    return ApiResponse.success(building.to_dict(), "获取楼宇详情成功")


@location_bp.route('/buildings', methods=['POST'])
@login_required
@permission_required('asset:create')
@log_operation("创建楼宇")
def create_building():
    """创建楼宇"""
    try:
        schema = BuildingSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查编码是否已存在
    if Building.query.filter_by(code=data['code'], is_deleted=False).first():
        raise CustomValidationError("楼宇编码已存在")
    
    building = Building(**data)
    
    try:
        building.save()
        return ApiResponse.success(building.to_dict(), "楼宇创建成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("楼宇创建失败")


@location_bp.route('/buildings/<int:building_id>', methods=['PUT'])
@login_required
@permission_required('asset:edit')
@log_operation("更新楼宇")
def update_building(building_id):
    """更新楼宇"""
    building = Building.find_by_id(building_id)
    if not building:
        raise ResourceNotFoundError("楼宇不存在")
    
    try:
        schema = BuildingSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查编码是否已被其他楼宇使用
    if data['code'] != building.code:
        if Building.query.filter_by(code=data['code'], is_deleted=False).filter(Building.id != building_id).first():
            raise CustomValidationError("楼宇编码已被使用")
    
    # 更新楼宇信息
    for key, value in data.items():
        setattr(building, key, value)
    
    building.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(building.to_dict(), "楼宇更新成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("楼宇更新失败")


@location_bp.route('/buildings/<int:building_id>', methods=['DELETE'])
@login_required
@permission_required('asset:delete')
@log_operation("删除楼宇")
def delete_building(building_id):
    """删除楼宇"""
    building = Building.find_by_id(building_id)
    if not building:
        raise ResourceNotFoundError("楼宇不存在")
    
    # 检查是否有关联的楼层
    if building.floors.filter_by(is_deleted=False).first():
        raise CustomValidationError("楼宇下存在楼层，无法删除")
    
    building.delete()
    return ApiResponse.success(message="楼宇删除成功")


# ========== 楼层管理 ==========

@location_bp.route('/floors', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_floors():
    """获取楼层列表"""
    building_id = request.args.get('building_id', type=int)
    
    query = Floor.query.filter_by(is_deleted=False)
    if building_id:
        query = query.filter_by(building_id=building_id)
    
    floors = query.all()
    floor_list = [floor.to_dict() for floor in floors]
    
    return ApiResponse.success(floor_list, "获取楼层列表成功")


@location_bp.route('/floors/<int:floor_id>', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_floor(floor_id):
    """获取楼层详情"""
    floor = Floor.find_by_id(floor_id)
    if not floor:
        raise ResourceNotFoundError("楼层不存在")
    
    return ApiResponse.success(floor.to_dict(), "获取楼层详情成功")


@location_bp.route('/floors', methods=['POST'])
@login_required
@permission_required('asset:create')
@log_operation("创建楼层")
def create_floor():
    """创建楼层"""
    try:
        schema = FloorSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查楼宇是否存在
    building = Building.find_by_id(data['building_id'])
    if not building:
        raise ResourceNotFoundError("楼宇不存在")
    
    # 检查楼层编码在同一楼宇内是否已存在
    if Floor.query.filter_by(
        building_id=data['building_id'],
        code=data['code'],
        is_deleted=False
    ).first():
        raise CustomValidationError("楼层编码在该楼宇内已存在")
    
    floor = Floor(**data)
    
    try:
        floor.save()
        return ApiResponse.success(floor.to_dict(), "楼层创建成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("楼层创建失败")


@location_bp.route('/floors/<int:floor_id>', methods=['PUT'])
@login_required
@permission_required('asset:edit')
@log_operation("更新楼层")
def update_floor(floor_id):
    """更新楼层"""
    floor = Floor.find_by_id(floor_id)
    if not floor:
        raise ResourceNotFoundError("楼层不存在")
    
    try:
        schema = FloorSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查楼宇是否存在
    building = Building.find_by_id(data['building_id'])
    if not building:
        raise ResourceNotFoundError("楼宇不存在")
    
    # 检查楼层编码在同一楼宇内是否已被其他楼层使用
    if (data['building_id'] != floor.building_id or data['code'] != floor.code):
        if Floor.query.filter_by(
            building_id=data['building_id'],
            code=data['code'],
            is_deleted=False
        ).filter(Floor.id != floor_id).first():
            raise CustomValidationError("楼层编码在该楼宇内已被使用")
    
    # 更新楼层信息
    for key, value in data.items():
        setattr(floor, key, value)
    
    floor.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(floor.to_dict(), "楼层更新成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("楼层更新失败")


@location_bp.route('/floors/<int:floor_id>', methods=['DELETE'])
@login_required
@permission_required('asset:delete')
@log_operation("删除楼层")
def delete_floor(floor_id):
    """删除楼层"""
    floor = Floor.find_by_id(floor_id)
    if not floor:
        raise ResourceNotFoundError("楼层不存在")
    
    # 检查是否有关联的房间
    if floor.rooms.filter_by(is_deleted=False).first():
        raise CustomValidationError("楼层下存在房间，无法删除")
    
    floor.delete()
    return ApiResponse.success(message="楼层删除成功")


# ========== 房间管理 ==========

@location_bp.route('/rooms', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_rooms():
    """获取房间列表"""
    floor_id = request.args.get('floor_id', type=int)
    building_id = request.args.get('building_id', type=int)
    
    query = Room.query.filter_by(is_deleted=False)
    
    if floor_id:
        query = query.filter_by(floor_id=floor_id)
    elif building_id:
        query = query.join(Floor).filter(Floor.building_id == building_id)
    
    rooms = query.all()
    room_list = [room.to_dict() for room in rooms]
    
    return ApiResponse.success(room_list, "获取房间列表成功")


@location_bp.route('/rooms/<int:room_id>', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_room(room_id):
    """获取房间详情"""
    room = Room.find_by_id(room_id)
    if not room:
        raise ResourceNotFoundError("房间不存在")
    
    return ApiResponse.success(room.to_dict(), "获取房间详情成功")


@location_bp.route('/rooms', methods=['POST'])
@login_required
@permission_required('asset:create')
@log_operation("创建房间")
def create_room():
    """创建房间"""
    try:
        schema = RoomSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查楼层是否存在
    floor = Floor.find_by_id(data['floor_id'])
    if not floor:
        raise ResourceNotFoundError("楼层不存在")
    
    # 检查房间编码在同一楼层内是否已存在
    if Room.query.filter_by(
        floor_id=data['floor_id'],
        code=data['code'],
        is_deleted=False
    ).first():
        raise CustomValidationError("房间编码在该楼层内已存在")
    
    room = Room(**data)
    
    try:
        room.save()
        return ApiResponse.success(room.to_dict(), "房间创建成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("房间创建失败")


@location_bp.route('/rooms/<int:room_id>', methods=['PUT'])
@login_required
@permission_required('asset:edit')
@log_operation("更新房间")
def update_room(room_id):
    """更新房间"""
    room = Room.find_by_id(room_id)
    if not room:
        raise ResourceNotFoundError("房间不存在")
    
    try:
        schema = RoomSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查楼层是否存在
    floor = Floor.find_by_id(data['floor_id'])
    if not floor:
        raise ResourceNotFoundError("楼层不存在")
    
    # 检查房间编码在同一楼层内是否已被其他房间使用
    if (data['floor_id'] != room.floor_id or data['code'] != room.code):
        if Room.query.filter_by(
            floor_id=data['floor_id'],
            code=data['code'],
            is_deleted=False
        ).filter(Room.id != room_id).first():
            raise CustomValidationError("房间编码在该楼层内已被使用")
    
    # 更新房间信息
    for key, value in data.items():
        setattr(room, key, value)
    
    room.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(room.to_dict(), "房间更新成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("房间更新失败")


@location_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
@login_required
@permission_required('asset:delete')
@log_operation("删除房间")
def delete_room(room_id):
    """删除房间"""
    room = Room.find_by_id(room_id)
    if not room:
        raise ResourceNotFoundError("房间不存在")
    
    # 检查是否有关联的资产
    from app.models.asset import Asset
    if Asset.query.filter_by(room_id=room_id, is_deleted=False).first():
        raise CustomValidationError("房间内存在资产，无法删除")
    
    room.delete()
    return ApiResponse.success(message="房间删除成功")


# ========== 位置树形结构 ==========

@location_bp.route('/tree', methods=['GET'])
@login_required
@permission_required('asset:view')
def get_location_tree():
    """获取位置树形结构"""
    buildings = Building.find_all()
    tree = []
    
    for building in buildings:
        building_node = {
            'id': f'building_{building.id}',
            'label': building.name,
            'type': 'building',
            'data': building.to_dict(),
            'children': []
        }
        
        floors = building.floors.filter_by(is_deleted=False).all()
        for floor in floors:
            floor_node = {
                'id': f'floor_{floor.id}',
                'label': floor.name,
                'type': 'floor',
                'data': floor.to_dict(),
                'children': []
            }
            
            rooms = floor.rooms.filter_by(is_deleted=False).all()
            for room in rooms:
                room_node = {
                    'id': f'room_{room.id}',
                    'label': room.name,
                    'type': 'room',
                    'data': room.to_dict(),
                    'children': []
                }
                floor_node['children'].append(room_node)
            
            building_node['children'].append(floor_node)
        
        tree.append(building_node)
    
    return ApiResponse.success(tree, "获取位置树形结构成功")