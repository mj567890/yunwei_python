"""
安全中间件
集成异常检测、API签名验证、通信安全等功能
"""
import time
from flask import request, g, current_app
from functools import wraps

from app.utils.anomaly_detection import anomaly_detector
from app.utils.helpers import get_client_ip
from app.utils.enhanced_audit import audit_logger, AuditEventType, AuditSeverity
from app.utils.performance_monitor import performance_monitor


class SecurityMiddleware:
    """安全中间件"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
    
    def before_request(self):
        """请求前处理"""
        g.start_time = time.time()
        g.client_ip = get_client_ip(request)
        g.user_agent = request.headers.get('User-Agent', '')
        g.request_id = request.headers.get('X-Request-ID', '')
        
        # 检查IP黑名单
        if self._is_ip_blocked(g.client_ip):
            audit_logger.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                severity=AuditSeverity.HIGH,
                operation_description=f"被阻止的IP访问: {g.client_ip}",
                ip_address=g.client_ip,
                user_agent=g.user_agent
            )
            return {'error': 'Access denied'}, 403
        
        # 异常行为检测
        self._detect_suspicious_activity()
    
    def after_request(self, response):
        """请求后处理"""
        # 记录请求性能指标
        if hasattr(g, 'start_time'):
            response_time = (time.time() - g.start_time) * 1000  # 毫秒
            response.headers['X-Response-Time'] = f"{response_time:.2f}ms"
            
            # 记录到性能监控
            endpoint = request.endpoint or request.path
            performance_monitor.record_request(response_time, response.status_code, endpoint)
        
        # 添加安全头
        self._add_security_headers(response)
        
        # 记录异常响应
        if response.status_code >= 400:
            self._log_error_response(response)
        
        # 检查登录失败情况
        if hasattr(g, 'login_failed') and g.login_failed:
            anomaly_detector.mark_login_failure(g.client_ip)
        
        return response
    
    def teardown_request(self, exception):
        """请求清理"""
        if exception:
            current_app.logger.error(f"请求异常: {str(exception)}")
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                operation_description=f"系统异常: {str(exception)}",
                error_message=str(exception),
                ip_address=getattr(g, 'client_ip', ''),
                user_agent=getattr(g, 'user_agent', '')
            )
    
    def _is_ip_blocked(self, ip):
        """检查IP是否被阻止"""
        # 检查是否在异常检测的阻止列表中
        return anomaly_detector.is_ip_blocked(ip)
    
    def _detect_suspicious_activity(self):
        """检测可疑活动"""
        try:
            # 频率检测
            anomaly_detector.detect_high_frequency_requests(g.client_ip)
            
            # 异常User-Agent检测
            anomaly_detector.detect_unusual_user_agent(g.user_agent, g.client_ip)
            
            # 异常访问时间检测
            anomaly_detector.detect_unusual_access_time(g.client_ip)
            
        except Exception as e:
            current_app.logger.error(f"异常检测错误: {str(e)}")
    
    def _add_security_headers(self, response):
        """添加安全响应头"""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
    
    def _log_error_response(self, response):
        """记录错误响应"""
        if response.status_code == 401:
            audit_logger.log_event(
                event_type=AuditEventType.UNAUTHORIZED_ACCESS,
                severity=AuditSeverity.MEDIUM,
                operation_description="未授权访问",
                ip_address=g.client_ip,
                user_agent=g.user_agent
            )
        elif response.status_code == 403:
            audit_logger.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                severity=AuditSeverity.MEDIUM,
                operation_description="访问被拒绝",
                ip_address=g.client_ip,
                user_agent=g.user_agent
            )
        elif response.status_code >= 500:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                operation_description=f"服务器错误: {response.status_code}",
                ip_address=g.client_ip,
                user_agent=g.user_agent
            )


def require_security_compliance(f):
    """要求安全合规的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查请求是否符合安全要求
        client_ip = get_client_ip(request)
        
        # 检查异常行为
        anomaly_event = anomaly_detector.check_request_anomaly(
            ip=client_ip,
            user_agent=request.headers.get('User-Agent', ''),
            endpoint=request.endpoint
        )
        
        if anomaly_event and anomaly_event.risk_score >= 80:
            audit_logger.log_event(
                event_type=AuditEventType.SECURITY_VIOLATION,
                severity=AuditSeverity.HIGH,
                operation_description=f"高风险请求被阻止: {anomaly_event.event_type}",
                ip_address=client_ip,
                error_message=f"风险评分: {anomaly_event.risk_score}"
            )
            return {'error': '请求被安全策略阻止', 'code': 'SECURITY_VIOLATION'}, 403
        
        return f(*args, **kwargs)
    
    return decorated_function


# 创建中间件实例
security_middleware = SecurityMiddleware()