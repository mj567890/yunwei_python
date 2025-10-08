"""
用户管理API
"""
from flask import Blueprint, request
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

from app.models.user import User, Role
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required, log_operation
from app.utils.exceptions import ValidationError as CustomValidationError, ResourceNotFoundError
from app.utils.helpers import validate_email, validate_phone
from app.utils.api_signature import require_api_signature
from app.utils.communication_security import require_secure_communication
from app import db

user_bp = Blueprint('user', __name__)


class UserCreateSchema(Schema):
    """创建用户参数验证"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    email = fields.Email(allow_none=True)
    phone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    real_name = fields.Str(allow_none=True, validate=validate.Length(max=50))
    role_ids = fields.List(fields.Int(), missing=[])
    status = fields.Int(validate=validate.OneOf([0, 1]), missing=1)


class UserUpdateSchema(Schema):
    """更新用户参数验证"""
    email = fields.Email(allow_none=True)
    phone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    real_name = fields.Str(allow_none=True, validate=validate.Length(max=50))
    role_ids = fields.List(fields.Int(), missing=None)
    status = fields.Int(validate=validate.OneOf([0, 1]), missing=None)


@user_bp.route('', methods=['GET'])
@login_required
@permission_required('user:view')
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    username = request.args.get('username', '').strip()
    real_name = request.args.get('real_name', '').strip()
    email = request.args.get('email', '').strip()
    status = request.args.get('status', type=int)
    
    # 构建查询
    query = User.query.filter_by(is_deleted=False)
    
    if username:
        query = query.filter(User.username.like(f'%{username}%'))
    if real_name:
        query = query.filter(User.real_name.like(f'%{real_name}%'))
    if email:
        query = query.filter(User.email.like(f'%{email}%'))
    if status is not None:
        query = query.filter(User.status == status)
    
    # 分页查询
    pagination = query.paginate(
        page=page,
        per_page=page_size,
        error_out=False
    )
    
    users = [user.to_dict() for user in pagination.items]
    
    return ApiResponse.page_success(
        users,
        pagination.total,
        page,
        page_size,
        "获取用户列表成功"
    )


@user_bp.route('/<int:user_id>', methods=['GET'])
@login_required
@permission_required('user:view')
def get_user(user_id):
    """获取用户详情"""
    user = User.find_by_id(user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    return ApiResponse.success(user.to_dict(), "获取用户详情成功")


@user_bp.route('', methods=['POST'])
@login_required
@permission_required('user:create')
@require_api_signature
@log_operation("创建用户")
def create_user():
    """创建用户"""
    try:
        schema = UserCreateSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username'], is_deleted=False).first():
        raise CustomValidationError("用户名已存在")
    
    # 检查邮箱是否已存在
    if data.get('email'):
        if not validate_email(data['email']):
            raise CustomValidationError("邮箱格式无效")
        if User.query.filter_by(email=data['email'], is_deleted=False).first():
            raise CustomValidationError("邮箱已被使用")
    
    # 检查手机号是否已存在
    if data.get('phone'):
        if not validate_phone(data['phone']):
            raise CustomValidationError("手机号格式无效")
        if User.query.filter_by(phone=data['phone'], is_deleted=False).first():
            raise CustomValidationError("手机号已被使用")
    
    # 创建用户
    user = User(
        username=data['username'],
        email=data.get('email'),
        phone=data.get('phone'),
        real_name=data.get('real_name'),
        status=data['status']
    )
    user.set_password(data['password'])
    
    # 分配角色
    if data['role_ids']:
        roles = Role.query.filter(Role.id.in_(data['role_ids']), Role.is_deleted == False).all()
        user.roles = roles
    
    try:
        db.session.add(user)
        db.session.commit()
        return ApiResponse.success(user.to_dict(), "用户创建成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("用户创建失败")


@user_bp.route('/<int:user_id>', methods=['PUT'])
@login_required
@permission_required('user:edit')
@require_api_signature
@log_operation("更新用户")
def update_user(user_id):
    """更新用户"""
    user = User.find_by_id(user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    try:
        schema = UserUpdateSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 检查邮箱是否已被其他用户使用
    if data.get('email') and data['email'] != user.email:
        if not validate_email(data['email']):
            raise CustomValidationError("邮箱格式无效")
        if User.query.filter_by(email=data['email'], is_deleted=False).filter(User.id != user_id).first():
            raise CustomValidationError("邮箱已被使用")
    
    # 检查手机号是否已被其他用户使用
    if data.get('phone') and data['phone'] != user.phone:
        if not validate_phone(data['phone']):
            raise CustomValidationError("手机号格式无效")
        if User.query.filter_by(phone=data['phone'], is_deleted=False).filter(User.id != user_id).first():
            raise CustomValidationError("手机号已被使用")
    
    # 更新用户信息
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'status' in data:
        user.status = data['status']
    
    # 更新角色
    if data.get('role_ids') is not None:
        roles = Role.query.filter(Role.id.in_(data['role_ids']), Role.is_deleted == False).all()
        user.roles = roles
    
    user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(user.to_dict(), "用户更新成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("用户更新失败")


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
@permission_required('user:delete')
@require_api_signature
@log_operation("删除用户")
def delete_user(user_id):
    """删除用户"""
    user = User.find_by_id(user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    # 不能删除自己
    from flask_jwt_extended import get_jwt_identity
    current_user_id = get_jwt_identity()
    if user_id == current_user_id:
        raise CustomValidationError("不能删除当前登录用户")
    
    # 软删除
    user.delete()
    
    return ApiResponse.success(message="用户删除成功")


@user_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@login_required
@permission_required('user:edit')
@require_api_signature
@log_operation("重置用户密码")
def reset_password(user_id):
    """重置用户密码"""
    user = User.find_by_id(user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    data = request.json or {}
    new_password = data.get('new_password', '123456')  # 默认密码
    
    if len(new_password) < 6:
        raise CustomValidationError("密码长度不能少于6位")
    
    user.set_password(new_password)
    user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(message="密码重置成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("密码重置失败")


@user_bp.route('/<int:user_id>/unlock', methods=['POST'])
@login_required
@permission_required('user:edit')
@log_operation("解锁用户账户")
def unlock_user(user_id):
    """解锁用户账户"""
    user = User.find_by_id(user_id)
    if not user:
        raise ResourceNotFoundError("用户不存在")
    
    user.unlock_account()
    
    return ApiResponse.success(message="账户解锁成功")


@user_bp.route('/roles', methods=['GET'])
@login_required
@permission_required('role:view')
def get_roles():
    """获取角色列表"""
    roles = Role.query.filter_by(is_deleted=False, status=1).all()
    role_list = [role.to_dict() for role in roles]
    
    return ApiResponse.success(role_list, "获取角色列表成功")