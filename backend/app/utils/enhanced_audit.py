"""
增强审计日志系统
实现全面的操作审计、异常检测和安全事件记录
"""
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
from flask import request, g, current_app
from sqlalchemy import and_, or_, func
from app import db
from app.models.base import BaseModel
from app.utils.helpers import get_client_ip


class AuditEventType(Enum):
    """审计事件类型"""
    # 认证相关
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    
    # 数据操作
    DATA_CREATE = "DATA_CREATE"
    DATA_READ = "DATA_READ"
    DATA_UPDATE = "DATA_UPDATE"
    DATA_DELETE = "DATA_DELETE"
    DATA_EXPORT = "DATA_EXPORT"
    DATA_IMPORT = "DATA_IMPORT"
    
    # 权限操作
    PERMISSION_GRANT = "PERMISSION_GRANT"
    PERMISSION_REVOKE = "PERMISSION_REVOKE"
    ROLE_ASSIGN = "ROLE_ASSIGN"
    ROLE_REMOVE = "ROLE_REMOVE"
    
    # 系统配置
    SYSTEM_CONFIG = "SYSTEM_CONFIG"
    USER_MANAGEMENT = "USER_MANAGEMENT"
    SECURITY_SETTING = "SECURITY_SETTING"
    
    # 文件操作
    FILE_UPLOAD = "FILE_UPLOAD"
    FILE_DOWNLOAD = "FILE_DOWNLOAD"
    FILE_DELETE = "FILE_DELETE"
    
    # 安全事件
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    ACCESS_DENIED = "ACCESS_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class AuditSeverity(Enum):
    """审计严重级别"""
    LOW = "LOW"           # 低级别：一般操作
    MEDIUM = "MEDIUM"     # 中级别：重要操作
    HIGH = "HIGH"         # 高级别：敏感操作
    CRITICAL = "CRITICAL" # 严重级别：安全事件


class EnhancedAuditLog(BaseModel):
    """增强审计日志模型"""
    __tablename__ = 'enhanced_audit_log'
    
    # 基本信息
    event_type = db.Column(db.String(50), nullable=False, comment='事件类型')
    severity = db.Column(db.String(20), nullable=False, default='MEDIUM', comment='严重程度')
    event_category = db.Column(db.String(30), nullable=False, comment='事件分类')
    
    # 用户信息
    user_id = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='用户ID')
    username = db.Column(db.String(50), nullable=True, comment='用户名')
    user_role = db.Column(db.String(100), nullable=True, comment='用户角色')
    
    # 请求信息
    request_method = db.Column(db.String(10), nullable=True, comment='请求方法')
    request_url = db.Column(db.String(500), nullable=True, comment='请求URL')
    request_params = db.Column(db.Text, nullable=True, comment='请求参数')
    
    # 网络信息
    client_ip = db.Column(db.String(45), nullable=True, comment='客户端IP')
    user_agent = db.Column(db.Text, nullable=True, comment='用户代理')
    referer = db.Column(db.String(500), nullable=True, comment='来源页面')
    
    # 操作信息
    resource_type = db.Column(db.String(50), nullable=True, comment='资源类型')
    resource_id = db.Column(db.String(100), nullable=True, comment='资源ID')
    operation_description = db.Column(db.Text, nullable=False, comment='操作描述')
    
    # 结果信息
    operation_result = db.Column(db.String(20), nullable=False, comment='操作结果: SUCCESS/FAILED/ERROR')
    error_message = db.Column(db.Text, nullable=True, comment='错误信息')
    response_code = db.Column(db.Integer, nullable=True, comment='响应状态码')
    
    # 数据变更
    old_values = db.Column(db.Text, nullable=True, comment='变更前数据')
    new_values = db.Column(db.Text, nullable=True, comment='变更后数据')
    
    # 时间和性能
    event_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='事件时间')
    processing_time = db.Column(db.Integer, nullable=True, comment='处理时间(毫秒)')
    
    # 安全相关
    session_id = db.Column(db.String(100), nullable=True, comment='会话ID')
    risk_score = db.Column(db.Integer, default=0, comment='风险评分(0-100)')
    security_context = db.Column(db.Text, nullable=True, comment='安全上下文')
    
    # 数据完整性
    checksum = db.Column(db.String(64), nullable=True, comment='数据校验和')
    
    def calculate_checksum(self):
        """计算数据校验和"""
        data = f"{self.event_type}{self.user_id}{self.event_timestamp}{self.operation_description}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        result = super().to_dict()
        
        # 解析JSON字段
        if self.request_params:
            try:
                result['request_params'] = json.loads(self.request_params)
            except:
                pass
                
        if self.old_values:
            try:
                result['old_values'] = json.loads(self.old_values)
            except:
                pass
                
        if self.new_values:
            try:
                result['new_values'] = json.loads(self.new_values)
            except:
                pass
        
        # 敏感信息处理
        if not include_sensitive:
            # 掩码IP地址
            if result.get('client_ip'):
                ip_parts = result['client_ip'].split('.')
                if len(ip_parts) == 4:
                    result['client_ip'] = f"{ip_parts[0]}.{ip_parts[1]}.*.* "
            
            # 移除敏感的请求参数
            if isinstance(result.get('request_params'), dict):
                sensitive_keys = ['password', 'token', 'secret', 'key']
                for key in list(result['request_params'].keys()):
                    if any(s in key.lower() for s in sensitive_keys):
                        result['request_params'][key] = "***"
        
        return result


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self):
        self.risk_patterns = {
            'multiple_failed_login': {'score': 30, 'threshold': 5, 'timeframe': 300},
            'privilege_escalation': {'score': 80, 'pattern': ['ROLE_ASSIGN', 'PERMISSION_GRANT']},
            'data_exfiltration': {'score': 70, 'pattern': ['DATA_EXPORT', 'FILE_DOWNLOAD']},
            'suspicious_ip': {'score': 50, 'threshold': 100, 'timeframe': 3600},
        }
    
    def log_event(self, 
                  event_type: AuditEventType,
                  severity: AuditSeverity = AuditSeverity.MEDIUM,
                  operation_description: str = "",
                  resource_type: str = None,
                  resource_id: str = None,
                  old_values: Dict = None,
                  new_values: Dict = None,
                  error_message: str = None,
                  processing_time: int = None,
                  additional_context: Dict = None) -> EnhancedAuditLog:
        """
        记录审计事件
        
        Args:
            event_type: 事件类型
            severity: 严重程度
            operation_description: 操作描述
            resource_type: 资源类型
            resource_id: 资源ID
            old_values: 变更前数据
            new_values: 变更后数据
            error_message: 错误信息
            processing_time: 处理时间
            additional_context: 额外上下文
            
        Returns:
            审计日志记录
        """
        try:
            # 获取当前用户信息
            user_id = None
            username = None
            user_role = None
            
            if hasattr(g, 'current_user') and g.current_user:
                user_id = g.current_user.id
                username = g.current_user.username
                user_role = ','.join([role.name for role in g.current_user.roles])
            
            # 获取请求信息
            request_method = request.method if request else None
            request_url = request.url if request else None
            client_ip = get_client_ip(request) if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            referer = request.headers.get('Referer') if request else None
            
            # 获取请求参数（安全处理）
            request_params = None
            if request:
                if request.method in ['POST', 'PUT', 'PATCH']:
                    if request.is_json:
                        params = request.get_json() or {}
                    else:
                        params = dict(request.form)
                else:
                    params = dict(request.args)
                
                # 过滤敏感参数
                sensitive_keys = ['password', 'token', 'secret', 'key', 'hash']
                filtered_params = {}
                for k, v in params.items():
                    if any(s in k.lower() for s in sensitive_keys):
                        filtered_params[k] = "***"
                    else:
                        filtered_params[k] = str(v)[:500]  # 限制长度
                
                request_params = json.dumps(filtered_params, ensure_ascii=False)
            
            # 确定操作结果
            operation_result = "SUCCESS"
            response_code = 200
            
            if error_message:
                operation_result = "FAILED"
                response_code = 500
            
            # 计算风险评分
            risk_score = self._calculate_risk_score(
                event_type, user_id, client_ip, severity
            )
            
            # 创建审计日志记录
            audit_log = EnhancedAuditLog(
                event_type=event_type.value,
                severity=severity.value,
                event_category=self._get_event_category(event_type),
                user_id=user_id,
                username=username,
                user_role=user_role,
                request_method=request_method,
                request_url=request_url,
                request_params=request_params,
                client_ip=client_ip,
                user_agent=user_agent,
                referer=referer,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                operation_description=operation_description,
                operation_result=operation_result,
                error_message=error_message,
                response_code=response_code,
                old_values=json.dumps(old_values, ensure_ascii=False) if old_values else None,
                new_values=json.dumps(new_values, ensure_ascii=False) if new_values else None,
                processing_time=processing_time,
                session_id=request.cookies.get('session_id') if request else None,
                risk_score=risk_score,
                security_context=json.dumps(additional_context, ensure_ascii=False) if additional_context else None
            )
            
            # 计算校验和
            audit_log.checksum = audit_log.calculate_checksum()
            
            # 保存到数据库
            db.session.add(audit_log)
            db.session.commit()
            
            # 高风险事件告警
            if risk_score >= 70 or severity == AuditSeverity.CRITICAL:
                self._trigger_security_alert(audit_log)
            
            return audit_log
            
        except Exception as e:
            current_app.logger.error(f"审计日志记录失败: {str(e)}")
            db.session.rollback()
            return None
    
    def _get_event_category(self, event_type: AuditEventType) -> str:
        """获取事件分类"""
        category_mapping = {
            AuditEventType.LOGIN_SUCCESS: "AUTHENTICATION",
            AuditEventType.LOGIN_FAILED: "AUTHENTICATION",
            AuditEventType.LOGOUT: "AUTHENTICATION",
            AuditEventType.PASSWORD_CHANGE: "AUTHENTICATION",
            
            AuditEventType.DATA_CREATE: "DATA_OPERATION",
            AuditEventType.DATA_READ: "DATA_OPERATION",
            AuditEventType.DATA_UPDATE: "DATA_OPERATION",
            AuditEventType.DATA_DELETE: "DATA_OPERATION",
            AuditEventType.DATA_EXPORT: "DATA_OPERATION",
            AuditEventType.DATA_IMPORT: "DATA_OPERATION",
            
            AuditEventType.PERMISSION_GRANT: "ACCESS_CONTROL",
            AuditEventType.PERMISSION_REVOKE: "ACCESS_CONTROL",
            AuditEventType.ROLE_ASSIGN: "ACCESS_CONTROL",
            AuditEventType.ROLE_REMOVE: "ACCESS_CONTROL",
            
            AuditEventType.SYSTEM_CONFIG: "SYSTEM_MANAGEMENT",
            AuditEventType.USER_MANAGEMENT: "SYSTEM_MANAGEMENT",
            AuditEventType.SECURITY_SETTING: "SYSTEM_MANAGEMENT",
            
            AuditEventType.FILE_UPLOAD: "FILE_OPERATION",
            AuditEventType.FILE_DOWNLOAD: "FILE_OPERATION",
            AuditEventType.FILE_DELETE: "FILE_OPERATION",
            
            AuditEventType.SECURITY_VIOLATION: "SECURITY_EVENT",
            AuditEventType.SUSPICIOUS_ACTIVITY: "SECURITY_EVENT",
            AuditEventType.ACCESS_DENIED: "SECURITY_EVENT",
            AuditEventType.RATE_LIMIT_EXCEEDED: "SECURITY_EVENT",
        }
        
        return category_mapping.get(event_type, "OTHER")
    
    def _calculate_risk_score(self, event_type: AuditEventType, user_id: int, 
                            client_ip: str, severity: AuditSeverity) -> int:
        """计算风险评分"""
        base_score = 10
        
        # 基于严重程度的评分
        severity_scores = {
            AuditSeverity.LOW: 5,
            AuditSeverity.MEDIUM: 20,
            AuditSeverity.HIGH: 50,
            AuditSeverity.CRITICAL: 90
        }
        base_score += severity_scores.get(severity, 20)
        
        # 基于事件类型的评分
        event_scores = {
            AuditEventType.LOGIN_FAILED: 15,
            AuditEventType.SECURITY_VIOLATION: 80,
            AuditEventType.SUSPICIOUS_ACTIVITY: 60,
            AuditEventType.DATA_EXPORT: 30,
            AuditEventType.PERMISSION_GRANT: 40,
            AuditEventType.SYSTEM_CONFIG: 50,
        }
        base_score += event_scores.get(event_type, 0)
        
        try:
            # 检查历史模式
            if user_id and client_ip:
                # 检查最近的失败登录
                recent_failures = db.session.query(EnhancedAuditLog).filter(
                    and_(
                        EnhancedAuditLog.user_id == user_id,
                        EnhancedAuditLog.event_type == AuditEventType.LOGIN_FAILED.value,
                        EnhancedAuditLog.event_timestamp > datetime.utcnow() - timedelta(minutes=5)
                    )
                ).count()
                
                if recent_failures >= 3:
                    base_score += 30
                
                # 检查异常IP访问
                normal_ips = db.session.query(EnhancedAuditLog.client_ip).filter(
                    and_(
                        EnhancedAuditLog.user_id == user_id,
                        EnhancedAuditLog.operation_result == 'SUCCESS',
                        EnhancedAuditLog.event_timestamp > datetime.utcnow() - timedelta(days=30)
                    )
                ).distinct().all()
                
                normal_ip_list = [ip[0] for ip in normal_ips if ip[0]]
                if client_ip not in normal_ip_list and len(normal_ip_list) > 0:
                    base_score += 25
                    
        except Exception as e:
            current_app.logger.warning(f"风险评分计算异常: {str(e)}")
        
        return min(base_score, 100)  # 限制最高分为100
    
    def _trigger_security_alert(self, audit_log: EnhancedAuditLog):
        """触发安全告警"""
        try:
            alert_message = f"高风险安全事件检测: {audit_log.event_type} - 风险评分: {audit_log.risk_score}"
            current_app.logger.critical(alert_message)
            
            # 这里可以集成邮件、短信、webhook等告警机制
            # 例如：send_security_alert(audit_log)
            
        except Exception as e:
            current_app.logger.error(f"安全告警触发失败: {str(e)}")
    
    def get_security_dashboard_data(self, days: int = 7) -> Dict[str, Any]:
        """获取安全仪表板数据"""
        try:
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # 事件统计
            event_stats = db.session.query(
                EnhancedAuditLog.event_category,
                func.count(EnhancedAuditLog.id).label('count')
            ).filter(
                EnhancedAuditLog.event_timestamp >= start_time
            ).group_by(EnhancedAuditLog.event_category).all()
            
            # 风险事件统计
            high_risk_events = db.session.query(EnhancedAuditLog).filter(
                and_(
                    EnhancedAuditLog.event_timestamp >= start_time,
                    EnhancedAuditLog.risk_score >= 70
                )
            ).count()
            
            # 失败事件统计
            failed_events = db.session.query(EnhancedAuditLog).filter(
                and_(
                    EnhancedAuditLog.event_timestamp >= start_time,
                    EnhancedAuditLog.operation_result == 'FAILED'
                )
            ).count()
            
            return {
                'event_statistics': {row.event_category: row.count for row in event_stats},
                'high_risk_events': high_risk_events,
                'failed_events': failed_events,
                'total_events': sum(row.count for row in event_stats),
                'time_range': f"最近{days}天",
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"获取安全仪表板数据失败: {str(e)}")
            return {'error': str(e)}


# 全局审计日志实例
audit_logger = AuditLogger()