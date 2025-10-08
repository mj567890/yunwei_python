"""
认证装饰器和权限检查
"""
import functools
from datetime import datetime
from flask import request, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.user import User, OperationLog
from app.utils.exceptions import AuthenticationError, AuthorizationError
from app.utils.helpers import get_client_ip
from app import db


def login_required(f):
    """登录验证装饰器"""
    @functools.wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            # 获取当前用户ID
            user_id = get_jwt_identity()
            if not user_id:
                raise AuthenticationError("无效的令牌")
            
            # 获取用户信息
            user = User.find_by_id(user_id)
            if not user:
                raise AuthenticationError("用户不存在")
            
            # 检查用户状态
            if not user.is_active():
                raise AuthenticationError("用户已被禁用或锁定")
            
            # 将用户信息存储到g对象中
            g.current_user = user
            
            return f(*args, **kwargs)
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, AuthorizationError)):
                raise e
            else:
                current_app.logger.error(f"认证装饰器异常: {str(e)}")
                raise AuthenticationError("认证失败")
    
    return decorated_function


def permission_required(permission_code: str):
    """权限验证装饰器"""
    def decorator(f):
        @functools.wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = g.current_user
            
            # 检查用户是否有指定权限
            if not user.has_permission(permission_code):
                current_app.logger.warning(
                    f"权限不足: 用户{user.username}尝试访问{permission_code}权限"
                )
                raise AuthorizationError(f"缺少权限: {permission_code}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def role_required(role_name: str):
    """角色验证装饰器"""
    def decorator(f):
        @functools.wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = g.current_user
            
            # 检查用户是否有指定角色
            if not user.has_role(role_name):
                current_app.logger.warning(
                    f"角色不足: 用户{user.username}尝试访问{role_name}角色"
                )
                raise AuthorizationError(f"需要{role_name}角色")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def admin_required(f):
    """管理员权限验证装饰器"""
    @functools.wraps(f)
    @role_required('系统管理员')
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated_function


def log_operation(operation: str, auto_log: bool = True):
    """操作日志装饰器"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                # 执行原函数
                result = f(*args, **kwargs)
                
                # 记录操作日志
                if auto_log and hasattr(g, 'current_user'):
                    end_time = datetime.now()
                    duration = int((end_time - start_time).total_seconds() * 1000)
                    
                    log_entry = OperationLog(
                        user_id=g.current_user.id,
                        username=g.current_user.username,
                        operation=operation,
                        method=request.method,
                        url=request.url,
                        ip=get_client_ip(request),
                        user_agent=request.headers.get('User-Agent'),
                        request_data=_get_request_data(),
                        status_code=200,
                        duration=duration
                    )
                    
                    try:
                        db.session.add(log_entry)
                        db.session.commit()
                    except Exception as e:
                        current_app.logger.error(f"记录操作日志失败: {str(e)}")
                        db.session.rollback()
                
                return result
                
            except Exception as e:
                # 记录错误日志
                if auto_log and hasattr(g, 'current_user'):
                    end_time = datetime.now()
                    duration = int((end_time - start_time).total_seconds() * 1000)
                    
                    log_entry = OperationLog(
                        user_id=g.current_user.id,
                        username=g.current_user.username,
                        operation=f"{operation}(失败)",
                        method=request.method,
                        url=request.url,
                        ip=get_client_ip(request),
                        user_agent=request.headers.get('User-Agent'),
                        request_data=_get_request_data(),
                        response_data=str(e),
                        status_code=getattr(e, 'code', 500),
                        duration=duration
                    )
                    
                    try:
                        db.session.add(log_entry)
                        db.session.commit()
                    except:
                        db.session.rollback()
                
                raise e
        
        return decorated_function
    return decorator


def _get_request_data() -> str:
    """获取请求数据"""
    try:
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.is_json:
                data = request.get_json()
                # 过滤敏感字段
                if isinstance(data, dict):
                    sensitive_fields = ['password', 'password_hash', 'token', 'secret']
                    filtered_data = {k: v for k, v in data.items() 
                                   if k not in sensitive_fields}
                    return str(filtered_data)
                return str(data)
            else:
                return str(dict(request.form))
        else:
            return str(dict(request.args))
    except:
        return ""


def validate_user_ownership(user_field: str = 'user_id'):
    """验证用户所有权装饰器"""
    def decorator(f):
        @functools.wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = g.current_user
            
            # 管理员跳过检查
            if user.has_role('系统管理员'):
                return f(*args, **kwargs)
            
            # 从请求中获取资源的用户ID
            resource_user_id = None
            
            # 从URL参数获取
            if user_field in kwargs:
                resource_user_id = kwargs[user_field]
            # 从查询参数获取
            elif request.args.get(user_field):
                resource_user_id = int(request.args.get(user_field))
            # 从JSON数据获取
            elif request.is_json and request.json.get(user_field):
                resource_user_id = request.json.get(user_field)
            
            # 检查所有权
            if resource_user_id and resource_user_id != user.id:
                raise AuthorizationError("只能操作自己的资源")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator