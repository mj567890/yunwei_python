"""
异常行为检测系统
实现智能的用户行为分析和异常检测，满足等保2.0入侵防范要求
"""
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from flask import current_app, g, request
from sqlalchemy import and_, func, desc
from app.models.user import User
from app.utils.enhanced_audit import EnhancedAuditLog, AuditEventType, AuditSeverity, audit_logger
from app.utils.helpers import get_client_ip


class AnomalyType(Enum):
    """异常类型"""
    BRUTE_FORCE_ATTACK = "BRUTE_FORCE_ATTACK"           # 暴力破解攻击
    UNUSUAL_LOGIN_TIME = "UNUSUAL_LOGIN_TIME"           # 异常登录时间
    SUSPICIOUS_IP = "SUSPICIOUS_IP"                     # 可疑IP地址
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"       # 权限提升
    DATA_EXFILTRATION = "DATA_EXFILTRATION"            # 数据外泄
    UNUSUAL_ACCESS_PATTERN = "UNUSUAL_ACCESS_PATTERN"   # 异常访问模式
    RAPID_API_CALLS = "RAPID_API_CALLS"                # 快速API调用
    ACCOUNT_ENUMERATION = "ACCOUNT_ENUMERATION"         # 账户枚举
    SUSPICIOUS_USER_AGENT = "SUSPICIOUS_USER_AGENT"     # 可疑用户代理
    GEOGRAPHIC_ANOMALY = "GEOGRAPHIC_ANOMALY"           # 地理位置异常


class ThreatLevel(Enum):
    """威胁级别"""
    LOW = "LOW"           # 低威胁
    MEDIUM = "MEDIUM"     # 中等威胁  
    HIGH = "HIGH"         # 高威胁
    CRITICAL = "CRITICAL" # 严重威胁


@dataclass
class AnomalyEvent:
    """异常事件"""
    anomaly_type: AnomalyType
    threat_level: ThreatLevel
    user_id: Optional[int]
    ip_address: str
    description: str
    confidence_score: float  # 置信度 0.0-1.0
    evidence: Dict[str, Any]
    timestamp: datetime
    risk_score: int  # 风险评分 0-100


class BehaviorProfile:
    """用户行为画像"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.login_times = []  # 登录时间列表
        self.ip_addresses = set()  # 常用IP地址
        self.user_agents = set()  # 常用用户代理
        self.api_call_patterns = defaultdict(list)  # API调用模式
        self.access_frequency = defaultdict(int)  # 访问频率
        self.last_updated = datetime.utcnow()
    
    def update_from_logs(self, days: int = 30):
        """从审计日志更新行为画像"""
        try:
            from app import db
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # 获取用户的审计日志
            logs = db.session.query(EnhancedAuditLog).filter(
                and_(
                    EnhancedAuditLog.user_id == self.user_id,
                    EnhancedAuditLog.event_timestamp >= start_time,
                    EnhancedAuditLog.operation_result == 'SUCCESS'
                )
            ).order_by(desc(EnhancedAuditLog.event_timestamp)).limit(1000).all()
            
            # 分析登录时间模式
            login_logs = [log for log in logs if log.event_type == AuditEventType.LOGIN_SUCCESS.value]
            self.login_times = [log.event_timestamp.hour for log in login_logs]
            
            # 分析IP地址
            self.ip_addresses = {log.client_ip for log in logs if log.client_ip}
            
            # 分析用户代理
            self.user_agents = {log.user_agent for log in logs if log.user_agent}
            
            # 分析API调用模式
            for log in logs:
                if log.request_url:
                    endpoint = log.request_url.split('?')[0]  # 移除查询参数
                    hour = log.event_timestamp.hour
                    self.api_call_patterns[endpoint].append(hour)
            
            # 计算访问频率
            for log in logs:
                if log.request_url:
                    self.access_frequency[log.request_url.split('?')[0]] += 1
            
            self.last_updated = datetime.utcnow()
            
        except Exception as e:
            current_app.logger.error(f"更新用户行为画像失败: {str(e)}")
    
    def is_unusual_login_time(self, hour: int) -> Tuple[bool, float]:
        """检查是否为异常登录时间"""
        if not self.login_times:
            return False, 0.0
        
        # 计算历史登录时间的统计信息
        mean_hour = statistics.mean(self.login_times)
        
        if len(self.login_times) > 1:
            std_hour = statistics.stdev(self.login_times)
        else:
            std_hour = 0
        
        # 如果标准差太小，说明用户登录时间很规律
        if std_hour < 1:
            std_hour = 2  # 设置最小标准差
        
        # 计算偏离程度
        deviation = abs(hour - mean_hour)
        # 处理跨天情况（例如23点和1点）
        deviation = min(deviation, 24 - deviation)
        
        # 如果偏离超过2个标准差，认为异常
        threshold = max(2 * std_hour, 3)  # 至少3小时的容忍度
        is_unusual = deviation > threshold
        confidence = min(deviation / threshold, 1.0) if threshold > 0 else 0.0
        
        return is_unusual, confidence
    
    def is_new_ip_address(self, ip: str) -> bool:
        """检查是否为新的IP地址"""
        return ip not in self.ip_addresses
    
    def is_unusual_user_agent(self, user_agent: str) -> bool:
        """检查是否为异常的用户代理"""
        return user_agent not in self.user_agents


class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self):
        self.behavior_profiles: Dict[int, BehaviorProfile] = {}
        self.ip_request_counts = defaultdict(lambda: deque(maxlen=100))  # IP请求计数
        self.failed_login_attempts = defaultdict(lambda: deque(maxlen=50))  # 失败登录尝试
        self.api_call_history = defaultdict(lambda: deque(maxlen=200))  # API调用历史
        
        # 检测阈值配置
        self.thresholds = {
            'brute_force_attempts': 5,      # 暴力破解尝试次数
            'brute_force_timeframe': 300,   # 暴力破解时间窗口（秒）
            'rapid_api_calls': 100,         # 快速API调用次数
            'rapid_api_timeframe': 60,      # 快速API调用时间窗口（秒）
            'unusual_login_confidence': 0.7, # 异常登录时间置信度阈值
            'data_export_threshold': 10,    # 数据导出阈值
            'data_export_timeframe': 3600,  # 数据导出时间窗口（秒）
        }
    
    def get_behavior_profile(self, user_id: int) -> BehaviorProfile:
        """获取或创建用户行为画像"""
        if user_id not in self.behavior_profiles:
            profile = BehaviorProfile(user_id)
            profile.update_from_logs()
            self.behavior_profiles[user_id] = profile
        
        # 定期更新画像
        profile = self.behavior_profiles[user_id]
        if (datetime.utcnow() - profile.last_updated).total_seconds() > 3600:  # 1小时更新一次
            profile.update_from_logs()
        
        return profile
    
    def detect_brute_force_attack(self, ip: str, user_id: Optional[int] = None) -> Optional[AnomalyEvent]:
        """检测暴力破解攻击"""
        current_time = time.time()
        
        # 记录失败登录尝试
        self.failed_login_attempts[ip].append(current_time)
        
        # 清理过期记录
        cutoff_time = current_time - self.thresholds['brute_force_timeframe']
        while (self.failed_login_attempts[ip] and 
               self.failed_login_attempts[ip][0] < cutoff_time):
            self.failed_login_attempts[ip].popleft()
        
        # 检查是否达到阈值
        attempt_count = len(self.failed_login_attempts[ip])
        if attempt_count >= self.thresholds['brute_force_attempts']:
            confidence = min(attempt_count / self.thresholds['brute_force_attempts'], 1.0)
            
            return AnomalyEvent(
                anomaly_type=AnomalyType.BRUTE_FORCE_ATTACK,
                threat_level=ThreatLevel.HIGH,
                user_id=user_id,
                ip_address=ip,
                description=f"检测到暴力破解攻击，{self.thresholds['brute_force_timeframe']}秒内失败{attempt_count}次",
                confidence_score=confidence,
                evidence={
                    'attempt_count': attempt_count,
                    'timeframe': self.thresholds['brute_force_timeframe'],
                    'recent_attempts': list(self.failed_login_attempts[ip])[-5:]
                },
                timestamp=datetime.utcnow(),
                risk_score=min(70 + attempt_count * 5, 100)
            )
        
        return None
    
    def detect_rapid_api_calls(self, ip: str, user_id: Optional[int] = None) -> Optional[AnomalyEvent]:
        """检测快速API调用"""
        current_time = time.time()
        
        # 记录API调用
        self.api_call_history[ip].append(current_time)
        
        # 清理过期记录
        cutoff_time = current_time - self.thresholds['rapid_api_timeframe']
        while (self.api_call_history[ip] and 
               self.api_call_history[ip][0] < cutoff_time):
            self.api_call_history[ip].popleft()
        
        # 检查调用频率
        call_count = len(self.api_call_history[ip])
        if call_count >= self.thresholds['rapid_api_calls']:
            confidence = min(call_count / self.thresholds['rapid_api_calls'], 1.0)
            
            return AnomalyEvent(
                anomaly_type=AnomalyType.RAPID_API_CALLS,
                threat_level=ThreatLevel.MEDIUM,
                user_id=user_id,
                ip_address=ip,
                description=f"检测到快速API调用，{self.thresholds['rapid_api_timeframe']}秒内调用{call_count}次",
                confidence_score=confidence,
                evidence={
                    'call_count': call_count,
                    'timeframe': self.thresholds['rapid_api_timeframe'],
                    'calls_per_minute': call_count / (self.thresholds['rapid_api_timeframe'] / 60)
                },
                timestamp=datetime.utcnow(),
                risk_score=min(50 + call_count, 100)
            )
        
        return None
    
    def detect_unusual_login_time(self, user_id: int, login_hour: int) -> Optional[AnomalyEvent]:
        """检测异常登录时间"""
        try:
            profile = self.get_behavior_profile(user_id)
            is_unusual, confidence = profile.is_unusual_login_time(login_hour)
            
            if is_unusual and confidence >= self.thresholds['unusual_login_confidence']:
                return AnomalyEvent(
                    anomaly_type=AnomalyType.UNUSUAL_LOGIN_TIME,
                    threat_level=ThreatLevel.LOW,
                    user_id=user_id,
                    ip_address=get_client_ip(request) if request else "unknown",
                    description=f"用户在异常时间登录：{login_hour}:00",
                    confidence_score=confidence,
                    evidence={
                        'login_hour': login_hour,
                        'historical_hours': profile.login_times[-10:],  # 最近10次登录时间
                        'deviation': confidence
                    },
                    timestamp=datetime.utcnow(),
                    risk_score=int(30 + confidence * 20)
                )
        except Exception as e:
            current_app.logger.error(f"检测异常登录时间失败: {str(e)}")
        
        return None
    
    def detect_suspicious_ip(self, user_id: int, ip: str) -> Optional[AnomalyEvent]:
        """检测可疑IP地址"""
        try:
            profile = self.get_behavior_profile(user_id)
            
            if profile.is_new_ip_address(ip):
                # 检查IP地址的历史记录
                recent_logs = db.session.query(EnhancedAuditLog).filter(
                    and_(
                        EnhancedAuditLog.client_ip == ip,
                        EnhancedAuditLog.event_timestamp >= datetime.utcnow() - timedelta(days=7)
                    )
                ).count()
                
                # 如果是全新IP且没有历史记录，标记为可疑
                if recent_logs == 0:
                    return AnomalyEvent(
                        anomaly_type=AnomalyType.SUSPICIOUS_IP,
                        threat_level=ThreatLevel.MEDIUM,
                        user_id=user_id,
                        ip_address=ip,
                        description=f"用户从新IP地址登录: {ip}",
                        confidence_score=0.8,
                        evidence={
                            'new_ip': ip,
                            'known_ips': list(profile.ip_addresses)[-5:],  # 最近5个已知IP
                            'historical_count': recent_logs
                        },
                        timestamp=datetime.utcnow(),
                        risk_score=60
                    )
        except Exception as e:
            current_app.logger.error(f"检测可疑IP失败: {str(e)}")
        
        return None
    
    def detect_data_exfiltration(self, user_id: int) -> Optional[AnomalyEvent]:
        """检测数据外泄行为"""
        try:
            # 检查最近1小时的数据导出操作
            start_time = datetime.utcnow() - timedelta(seconds=self.thresholds['data_export_timeframe'])
            
            export_events = db.session.query(EnhancedAuditLog).filter(
                and_(
                    EnhancedAuditLog.user_id == user_id,
                    EnhancedAuditLog.event_timestamp >= start_time,
                    or_(
                        EnhancedAuditLog.event_type == AuditEventType.DATA_EXPORT.value,
                        EnhancedAuditLog.event_type == AuditEventType.FILE_DOWNLOAD.value
                    )
                )
            ).count()
            
            if export_events >= self.thresholds['data_export_threshold']:
                confidence = min(export_events / self.thresholds['data_export_threshold'], 1.0)
                
                return AnomalyEvent(
                    anomaly_type=AnomalyType.DATA_EXFILTRATION,
                    threat_level=ThreatLevel.HIGH,
                    user_id=user_id,
                    ip_address=get_client_ip(request) if request else "unknown",
                    description=f"检测到可能的数据外泄行为，{self.thresholds['data_export_timeframe']/3600}小时内导出{export_events}次",
                    confidence_score=confidence,
                    evidence={
                        'export_count': export_events,
                        'timeframe_hours': self.thresholds['data_export_timeframe'] / 3600,
                        'threshold': self.thresholds['data_export_threshold']
                    },
                    timestamp=datetime.utcnow(),
                    risk_score=min(80 + export_events * 2, 100)
                )
        except Exception as e:
            current_app.logger.error(f"检测数据外泄失败: {str(e)}")
        
        return None
    
    def analyze_current_request(self) -> List[AnomalyEvent]:
        """分析当前请求的异常情况"""
        anomalies = []
        
        if not request:
            return anomalies
        
        try:
            ip = get_client_ip(request)
            user_id = getattr(g, 'current_user', None)
            user_id = user_id.id if user_id else None
            
            # 检测暴力破解攻击（针对登录失败）
            if (request.endpoint == 'auth.login' and 
                hasattr(g, 'login_failed') and g.login_failed):
                anomaly = self.detect_brute_force_attack(ip, user_id)
                if anomaly:
                    anomalies.append(anomaly)
            
            # 检测快速API调用
            anomaly = self.detect_rapid_api_calls(ip, user_id)
            if anomaly:
                anomalies.append(anomaly)
            
            # 如果是登录成功，检测其他异常
            if user_id and request.endpoint == 'auth.login':
                current_hour = datetime.utcnow().hour
                
                # 检测异常登录时间
                anomaly = self.detect_unusual_login_time(user_id, current_hour)
                if anomaly:
                    anomalies.append(anomaly)
                
                # 检测可疑IP
                anomaly = self.detect_suspicious_ip(user_id, ip)
                if anomaly:
                    anomalies.append(anomaly)
            
            # 如果是数据导出相关操作，检测数据外泄
            if (user_id and request.endpoint and 
                any(keyword in request.endpoint for keyword in ['export', 'download'])):
                anomaly = self.detect_data_exfiltration(user_id)
                if anomaly:
                    anomalies.append(anomaly)
            
        except Exception as e:
            current_app.logger.error(f"分析当前请求异常: {str(e)}")
        
        return anomalies
    
    def handle_anomaly_events(self, anomalies: List[AnomalyEvent]):
        """处理异常事件"""
        for anomaly in anomalies:
            try:
                # 记录到审计日志
                audit_logger.log_event(
                    event_type=AuditEventType.SUSPICIOUS_ACTIVITY,
                    severity=self._get_audit_severity(anomaly.threat_level),
                    operation_description=f"{anomaly.anomaly_type.value}: {anomaly.description}",
                    resource_type="SecurityEvent",
                    resource_id=anomaly.anomaly_type.value,
                    additional_context={
                        'anomaly_type': anomaly.anomaly_type.value,
                        'threat_level': anomaly.threat_level.value,
                        'confidence_score': anomaly.confidence_score,
                        'risk_score': anomaly.risk_score,
                        'evidence': anomaly.evidence
                    }
                )
                
                # 高威胁事件特殊处理
                if anomaly.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                    self._handle_high_threat_event(anomaly)
                
                current_app.logger.warning(
                    f"检测到异常行为: {anomaly.anomaly_type.value} - "
                    f"威胁级别: {anomaly.threat_level.value} - "
                    f"置信度: {anomaly.confidence_score:.2f}"
                )
                
            except Exception as e:
                current_app.logger.error(f"处理异常事件失败: {str(e)}")
    
    def _get_audit_severity(self, threat_level: ThreatLevel) -> AuditSeverity:
        """转换威胁级别为审计严重性"""
        mapping = {
            ThreatLevel.LOW: AuditSeverity.LOW,
            ThreatLevel.MEDIUM: AuditSeverity.MEDIUM,
            ThreatLevel.HIGH: AuditSeverity.HIGH,
            ThreatLevel.CRITICAL: AuditSeverity.CRITICAL
        }
        return mapping.get(threat_level, AuditSeverity.MEDIUM)
    
    def _handle_high_threat_event(self, anomaly: AnomalyEvent):
        """处理高威胁事件"""
        try:
            # 这里可以实现自动响应机制
            # 例如：临时锁定账户、发送告警通知、记录到安全事件表等
            
            if anomaly.anomaly_type == AnomalyType.BRUTE_FORCE_ATTACK:
                # 可以考虑临时封禁IP
                current_app.logger.critical(f"暴力破解攻击来自IP: {anomaly.ip_address}")
            
            elif anomaly.anomaly_type == AnomalyType.DATA_EXFILTRATION:
                # 可以考虑临时限制用户的导出权限
                current_app.logger.critical(f"检测到数据外泄行为，用户ID: {anomaly.user_id}")
            
        except Exception as e:
            current_app.logger.error(f"处理高威胁事件失败: {str(e)}")


# 全局异常检测器实例
anomaly_detector = AnomalyDetector()


def detect_anomalies():
    """异常检测中间件装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 执行原始函数
                result = f(*args, **kwargs)
                
                # 分析当前请求的异常情况
                anomalies = anomaly_detector.analyze_current_request()
                
                # 处理检测到的异常
                if anomalies:
                    anomaly_detector.handle_anomaly_events(anomalies)
                
                return result
                
            except Exception as e:
                # 即使异常检测失败，也不应该影响正常业务
                current_app.logger.error(f"异常检测中间件错误: {str(e)}")
                raise e
        
        return decorated_function
    return decorator


# 提供获取检测器实例的函数
def get_anomaly_detector():
    """获取异常检测器实例"""
    if not hasattr(get_anomaly_detector, '_instance'):
        get_anomaly_detector._instance = AnomalyDetector()
    return get_anomaly_detector._instance


# 为了向后兼容，提供一个全局变量
anomaly_detector = None