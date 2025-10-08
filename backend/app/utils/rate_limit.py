"""
API频率限制配置模块
实现分级频率限制策略，防止暴力攻击和API滥用
"""
from flask import request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.utils.helpers import get_client_ip


def get_user_id():
    """获取当前用户ID用于限制"""
    if hasattr(g, 'current_user') and g.current_user:
        return str(g.current_user.id)
    return get_client_ip(request)


class RateLimitConfig:
    """频率限制配置"""
    
    # 全局默认限制
    DEFAULT_LIMITS = [
        "1000 per hour",    # 每小时1000次
        "100 per minute",   # 每分钟100次
        "10 per second"     # 每秒10次
    ]
    
    # 认证相关接口限制（更严格）
    AUTH_LIMITS = [
        "50 per hour",      # 每小时50次
        "5 per minute",     # 每分钟5次
        "1 per second"      # 每秒1次
    ]
    
    # 登录接口限制（最严格）
    LOGIN_LIMITS = [
        "20 per hour",      # 每小时20次
        "3 per minute",     # 每分钟3次
        "1 per 2 seconds"   # 每2秒1次
    ]
    
    # 文件上传限制
    UPLOAD_LIMITS = [
        "200 per hour",     # 每小时200次
        "20 per minute",    # 每分钟20次
        "2 per second"      # 每秒2次
    ]
    
    # 数据导出限制
    EXPORT_LIMITS = [
        "100 per hour",     # 每小时100次
        "10 per minute",    # 每分钟10次
        "1 per second"      # 每秒1次
    ]
    
    # 查询接口限制
    QUERY_LIMITS = [
        "2000 per hour",    # 每小时2000次
        "200 per minute",   # 每分钟200次
        "20 per second"     # 每秒20次
    ]
    
    # 管理员接口限制
    ADMIN_LIMITS = [
        "500 per hour",     # 每小时500次
        "50 per minute",    # 每分钟50次
        "5 per second"      # 每秒5次
    ]


def create_limiter(app):
    """创建并配置限流器"""
    limiter = Limiter(
        app,
        key_func=get_user_id,
        default_limits=RateLimitConfig.DEFAULT_LIMITS,
        storage_uri="memory://",  # 生产环境建议使用Redis
        headers_enabled=True,
        swallow_errors=True  # 不因限流器错误而中断请求
    )
    
    return limiter


def get_rate_limit_for_endpoint(endpoint: str) -> list:
    """根据端点获取相应的频率限制"""
    
    # 认证相关端点
    auth_endpoints = [
        'auth.login', 'auth.refresh', 'auth.change_password',
        'auth.logout', 'auth.get_profile', 'auth.update_profile'
    ]
    
    # 登录端点（最严格）
    login_endpoints = ['auth.login']
    
    # 文件上传端点
    upload_endpoints = ['file.upload_file']
    
    # 数据导出端点
    export_endpoints = [
        'asset.export_assets', 'maintenance.export_records',
        'fault.export_faults', 'statistics.export_report'
    ]
    
    # 管理员端点
    admin_endpoints = [
        'user.create_user', 'user.delete_user', 'user.update_user',
        'user.assign_roles', 'user.reset_password'
    ]
    
    # 查询端点
    query_endpoints = [
        'asset.get_assets', 'maintenance.get_records',
        'fault.get_faults', 'network.get_devices',
        'statistics.get_overview'
    ]
    
    if endpoint in login_endpoints:
        return RateLimitConfig.LOGIN_LIMITS
    elif endpoint in auth_endpoints:
        return RateLimitConfig.AUTH_LIMITS
    elif endpoint in upload_endpoints:
        return RateLimitConfig.UPLOAD_LIMITS
    elif endpoint in export_endpoints:
        return RateLimitConfig.EXPORT_LIMITS
    elif endpoint in admin_endpoints:
        return RateLimitConfig.ADMIN_LIMITS
    elif endpoint in query_endpoints:
        return RateLimitConfig.QUERY_LIMITS
    else:
        return RateLimitConfig.DEFAULT_LIMITS