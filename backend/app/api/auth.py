"""
认证API
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from marshmallow import Schema, fields, validate, ValidationError

from app.models.user import User
from app.utils.response import ApiResponse
from app.utils.auth import log_operation
from app.utils.helpers import get_client_ip
from app.utils.enhanced_audit import audit_logger, AuditEventType, AuditSeverity
from app.utils.api_signature import require_api_signature
from app.utils.anomaly_detection import anomaly_detector
from app.utils.communication_security import require_secure_communication
from app.utils.exceptions import AuthenticationError, ValidationError as CustomValidationError
from app import db, limiter

auth_bp = Blueprint('auth', __name__)


class LoginSchema(Schema):
    """登录参数验证"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    remember_me = fields.Bool(missing=False)


class ChangePasswordSchema(Schema):
    """修改密码参数验证"""
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    confirm_password = fields.Str(required=True)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("3 per minute", key_func=lambda: get_client_ip(request))
@limiter.limit("20 per hour", key_func=lambda: get_client_ip(request))
@require_api_signature
@require_secure_communication
@log_operation("用户登录")
def login():
    """用户登录"""
    try:
        # 参数验证
        schema = LoginSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    username = data['username']
    password = data['password']
    remember_me = data.get('remember_me', False)
    
    # 查找用户
    user = User.query.filter_by(username=username, is_deleted=False).first()
    if not user:
        current_app.logger.warning(f"登录失败: 用户名不存在 - {username} - IP: {get_client_ip(request)}")
        # 记录登录失败审计日志
        audit_logger.log_event(
            event_type=AuditEventType.LOGIN_FAILED,
            severity=AuditSeverity.MEDIUM,
            operation_description=f"用户名不存在: {username}",
            error_message="用户名或密码错误"
        )
        # 标记登录失败供异常检测
        g.login_failed = True
        raise AuthenticationError("用户名或密码错误")
    
    # 检查账户是否被锁定
    if user.is_locked():
        current_app.logger.warning(f"登录失败: 账户被锁定 - {username}")
        raise AuthenticationError("账户已被锁定，请稍后再试")
    
    # 检查账户状态
    if not user.is_active():
        current_app.logger.warning(f"登录失败: 账户被禁用 - {username}")
        raise AuthenticationError("账户已被禁用")
    
    # 验证密码
    if not user.check_password(password):
        # 增加失败次数
        user.failed_login_count += 1
        
        # 连续失败5次锁定账户30分钟
        if user.failed_login_count >= 5:
            user.lock_account(30)
            current_app.logger.warning(f"账户因连续登录失败被锁定 - {username}")
        
        db.session.commit()
        
        current_app.logger.warning(f"登录失败: 密码错误 - {username} - 失败次数: {user.failed_login_count}")
        raise AuthenticationError("用户名或密码错误")
    
    # 登录成功，重置失败次数
    user.failed_login_count = 0
    user.login_count += 1
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = get_client_ip(request)
    db.session.commit()
    
    # 记录成功登录审计日志
    audit_logger.log_event(
        event_type=AuditEventType.LOGIN_SUCCESS,
        severity=AuditSeverity.LOW,
        operation_description=f"用户成功登录: {username}",
        resource_type="User",
        resource_id=str(user.id)
    )
    
    # 生成令牌
    expires_delta = timedelta(days=7) if remember_me else None
    access_token = create_access_token(
        identity=user.id,
        expires_delta=expires_delta
    )
    refresh_token = create_refresh_token(identity=user.id)
    
    current_app.logger.info(f"用户登录成功 - {username} - IP: {get_client_ip(request)}")
    
    return ApiResponse.success({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(exclude_fields=['failed_login_count', 'locked_until']),
        'expires_in': int(expires_delta.total_seconds()) if expires_delta else 86400
    }, "登录成功")


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@log_operation("用户登出")
def logout():
    """用户登出"""
    # 将令牌加入黑名单（这里简化处理，实际应该使用Redis等缓存）
    jti = get_jwt()['jti']
    # TODO: 将jti加入黑名单
    
    return ApiResponse.success(message="登出成功")


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@require_api_signature
def refresh():
    """刷新令牌"""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    
    if not user or not user.is_active():
        raise AuthenticationError("无效的刷新令牌")
    
    # 生成新的访问令牌
    access_token = create_access_token(identity=user_id)
    
    return ApiResponse.success({
        'access_token': access_token,
        'expires_in': 86400
    }, "令牌刷新成功")


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    
    if not user:
        raise AuthenticationError("用户不存在")
    
    return ApiResponse.success(user.to_dict(), "获取用户信息成功")


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
@log_operation("更新用户信息")
def update_profile():
    """更新当前用户信息"""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    
    if not user:
        raise AuthenticationError("用户不存在")
    
    data = request.json or {}
    
    # 允许更新的字段
    allowed_fields = ['real_name', 'email', 'phone']
    
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
        return ApiResponse.success(user.to_dict(), "更新成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新用户信息失败: {str(e)}")
        return ApiResponse.error("更新失败")


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@require_api_signature
@log_operation("修改密码")
def change_password():
    """修改密码"""
    try:
        # 参数验证
        schema = ChangePasswordSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    
    if not user:
        raise AuthenticationError("用户不存在")
    
    # 验证旧密码
    if not user.check_password(data['old_password']):
        raise AuthenticationError("原密码错误")
    
    # 验证新密码确认
    if data['new_password'] != data['confirm_password']:
        raise CustomValidationError("新密码确认不匹配")
    
    # 检查新密码是否与旧密码相同
    if user.check_password(data['new_password']):
        raise CustomValidationError("新密码不能与原密码相同")
    
    # 更新密码
    user.set_password(data['new_password'])
    user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        current_app.logger.info(f"用户修改密码成功 - {user.username}")
        return ApiResponse.success(message="密码修改成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"修改密码失败: {str(e)}")
        return ApiResponse.error("密码修改失败")


@auth_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_user_permissions():
    """获取当前用户权限"""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    
    if not user:
        raise AuthenticationError("用户不存在")
    
    # 收集用户所有权限
    permissions = set()
    roles = []
    
    for role in user.roles:
        if role.status == 1:  # 启用的角色
            roles.append({
                'id': role.id,
                'name': role.name,
                'code': role.code,
                'description': role.description
            })
            
            for permission in role.permissions:
                permissions.add(permission.code)
    
    return ApiResponse.success({
        'permissions': list(permissions),
        'roles': roles
    }, "获取权限成功")