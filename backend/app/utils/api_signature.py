"""
API签名验证模块
实现基于HMAC-SHA256的API请求签名机制，满足等保2.0通信完整性要求
"""
import hmac
import hashlib
import base64
import time
import json
import uuid
from typing import Dict, Optional, Tuple, Any
from functools import wraps
from flask import request, current_app, g
from app.utils.exceptions import AuthenticationError, ValidationError as CustomValidationError
from app.utils.helpers import get_client_ip
from app.utils.enhanced_audit import audit_logger, AuditEventType, AuditSeverity


class APISignatureManager:
    """API签名管理器"""
    
    def __init__(self):
        self.signature_expiry = 300  # 签名有效期5分钟
        self.nonce_cache = {}  # 简单的nonce缓存，生产环境应使用Redis
        self.cache_cleanup_interval = 600  # 缓存清理间隔10分钟
        self.last_cleanup_time = time.time()
    
    def generate_signature(self, method: str, url: str, timestamp: str, 
                          nonce: str, body: str = "", api_secret: str = None) -> str:
        """
        生成API请求签名
        
        Args:
            method: HTTP方法
            url: 请求URL
            timestamp: 时间戳
            nonce: 随机数
            body: 请求体
            api_secret: API密钥
            
        Returns:
            签名字符串
        """
        if not api_secret:
            api_secret = current_app.config.get('API_SECRET_KEY', 'default-api-secret')
        
        # 构建签名字符串
        sign_string = f"{method}\n{url}\n{timestamp}\n{nonce}\n{body}"
        
        # 生成HMAC-SHA256签名
        signature = hmac.new(
            api_secret.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, method: str, url: str, timestamp: str,
                        nonce: str, signature: str, body: str = "",
                        api_secret: str = None) -> Tuple[bool, str]:
        """
        验证API请求签名
        
        Args:
            method: HTTP方法
            url: 请求URL
            timestamp: 时间戳
            nonce: 随机数
            signature: 客户端签名
            body: 请求体
            api_secret: API密钥
            
        Returns:
            (验证结果, 错误信息)
        """
        try:
            # 1. 验证时间戳
            current_time = int(time.time())
            request_time = int(timestamp)
            
            if abs(current_time - request_time) > self.signature_expiry:
                return False, "请求已过期"
            
            # 2. 验证nonce（防重放攻击）
            if self._is_nonce_used(nonce, request_time):
                return False, "重复的请求标识"
            
            # 3. 生成期望的签名
            expected_signature = self.generate_signature(
                method, url, timestamp, nonce, body, api_secret
            )
            
            # 4. 比较签名
            if not hmac.compare_digest(signature, expected_signature):
                return False, "签名验证失败"
            
            # 5. 记录nonce
            self._record_nonce(nonce, request_time)
            
            # 6. 清理过期的nonce
            self._cleanup_expired_nonces()
            
            return True, "签名验证成功"
            
        except Exception as e:
            current_app.logger.error(f"签名验证异常: {str(e)}")
            return False, "签名验证异常"
    
    def _is_nonce_used(self, nonce: str, timestamp: int) -> bool:
        """检查nonce是否已使用"""
        return nonce in self.nonce_cache
    
    def _record_nonce(self, nonce: str, timestamp: int):
        """记录已使用的nonce"""
        self.nonce_cache[nonce] = timestamp
    
    def _cleanup_expired_nonces(self):
        """清理过期的nonce"""
        current_time = time.time()
        
        # 只在间隔时间后才执行清理
        if current_time - self.last_cleanup_time < self.cache_cleanup_interval:
            return
        
        expired_nonces = []
        expiry_time = current_time - self.signature_expiry
        
        for nonce, timestamp in self.nonce_cache.items():
            if timestamp < expiry_time:
                expired_nonces.append(nonce)
        
        for nonce in expired_nonces:
            del self.nonce_cache[nonce]
        
        self.last_cleanup_time = current_time
        
        if expired_nonces:
            current_app.logger.debug(f"清理过期nonce: {len(expired_nonces)}个")
    
    def generate_client_signature_info(self, method: str, url: str, 
                                     body: str = "") -> Dict[str, str]:
        """
        为客户端生成签名信息（用于测试和文档）
        
        Args:
            method: HTTP方法
            url: 请求URL
            body: 请求体
            
        Returns:
            签名信息字典
        """
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4()).replace('-', '')
        
        signature = self.generate_signature(method, url, timestamp, nonce, body)
        
        return {
            'timestamp': timestamp,
            'nonce': nonce,
            'signature': signature,
            'method': method,
            'url': url
        }


# 全局签名管理器实例
signature_manager = APISignatureManager()


def require_api_signature(sensitive_level: str = "HIGH"):
    """
    API签名验证装饰器
    
    Args:
        sensitive_level: 敏感级别 HIGH/MEDIUM/LOW
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 检查是否启用签名验证
                if not current_app.config.get('ENABLE_API_SIGNATURE', False):
                    # 开发环境可以关闭签名验证
                    if current_app.config.get('FLASK_ENV') != 'development':
                        current_app.logger.warning("API签名验证未启用")
                    return f(*args, **kwargs)
                
                # 获取签名相关头部
                timestamp = request.headers.get('X-Timestamp')
                nonce = request.headers.get('X-Nonce')
                signature = request.headers.get('X-Signature')
                
                if not all([timestamp, nonce, signature]):
                    audit_logger.log_event(
                        event_type=AuditEventType.SECURITY_VIOLATION,
                        severity=AuditSeverity.HIGH,
                        operation_description="API签名验证失败: 缺少必要头部",
                        error_message="缺少签名验证头部"
                    )
                    raise AuthenticationError("缺少签名验证头部")
                
                # 获取请求信息
                method = request.method
                url = request.url
                body = ""
                
                if request.method in ['POST', 'PUT', 'PATCH']:
                    if request.is_json:
                        body = json.dumps(request.get_json(), sort_keys=True, separators=(',', ':'))
                    else:
                        body = request.get_data(as_text=True)
                
                # 验证签名
                is_valid, error_msg = signature_manager.verify_signature(
                    method, url, timestamp, nonce, signature, body
                )
                
                if not is_valid:
                    # 记录签名验证失败
                    audit_logger.log_event(
                        event_type=AuditEventType.SECURITY_VIOLATION,
                        severity=AuditSeverity.CRITICAL if sensitive_level == "HIGH" else AuditSeverity.HIGH,
                        operation_description=f"API签名验证失败: {error_msg}",
                        resource_type="API",
                        resource_id=request.endpoint,
                        error_message=error_msg,
                        additional_context={
                            'timestamp': timestamp,
                            'nonce': nonce,
                            'signature': signature[:10] + "...",  # 只记录签名前10位
                            'sensitive_level': sensitive_level
                        }
                    )
                    raise AuthenticationError(f"签名验证失败: {error_msg}")
                
                # 签名验证成功，记录审计日志
                audit_logger.log_event(
                    event_type=AuditEventType.DATA_ACCESS,
                    severity=AuditSeverity.LOW,
                    operation_description=f"API签名验证成功: {request.endpoint}",
                    resource_type="API",
                    resource_id=request.endpoint,
                    additional_context={
                        'sensitive_level': sensitive_level
                    }
                )
                
                # 将签名信息存储到g中，供后续使用
                g.api_signature_verified = True
                g.api_signature_timestamp = timestamp
                g.api_signature_nonce = nonce
                
                return f(*args, **kwargs)
                
            except AuthenticationError:
                raise
            except Exception as e:
                current_app.logger.error(f"API签名验证装饰器异常: {str(e)}")
                audit_logger.log_event(
                    event_type=AuditEventType.SECURITY_VIOLATION,
                    severity=AuditSeverity.HIGH,
                    operation_description="API签名验证装饰器异常",
                    error_message=str(e)
                )
                raise AuthenticationError("签名验证系统异常")
        
        return decorated_function
    return decorator


def generate_api_key_pair() -> Dict[str, str]:
    """
    生成API密钥对（用于客户端配置）
    
    Returns:
        包含API ID和密钥的字典
    """
    api_id = f"API_{uuid.uuid4().hex[:16].upper()}"
    api_secret = base64.urlsafe_b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes).decode('utf-8')
    
    return {
        'api_id': api_id,
        'api_secret': api_secret,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'note': '请妥善保管API密钥，系统不会再次显示完整密钥'
    }


class APISignatureClient:
    """API签名客户端（用于测试和集成）"""
    
    def __init__(self, api_secret: str):
        self.api_secret = api_secret
        self.signature_manager = APISignatureManager()
    
    def sign_request(self, method: str, url: str, body: str = "") -> Dict[str, str]:
        """
        为请求生成签名头部
        
        Args:
            method: HTTP方法
            url: 请求URL
            body: 请求体
            
        Returns:
            签名头部字典
        """
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4()).replace('-', '')
        
        signature = self.signature_manager.generate_signature(
            method, url, timestamp, nonce, body, self.api_secret
        )
        
        return {
            'X-Timestamp': timestamp,
            'X-Nonce': nonce,
            'X-Signature': signature
        }
    
    def make_signed_request(self, method: str, url: str, data: Dict = None) -> Dict[str, str]:
        """
        创建带签名的请求头部
        
        Args:
            method: HTTP方法
            url: 请求URL
            data: 请求数据
            
        Returns:
            完整的请求头部
        """
        body = ""
        if data and method in ['POST', 'PUT', 'PATCH']:
            body = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        signature_headers = self.sign_request(method, url, body)
        
        headers = {
            'Content-Type': 'application/json',
            **signature_headers
        }
        
        return headers


def validate_signature_headers(headers: Dict[str, str]) -> Tuple[bool, str]:
    """
    验证签名头部格式
    
    Args:
        headers: 请求头部字典
        
    Returns:
        (验证结果, 错误信息)
    """
    required_headers = ['X-Timestamp', 'X-Nonce', 'X-Signature']
    
    # 检查必需的头部
    for header in required_headers:
        if header not in headers:
            return False, f"缺少必需的头部: {header}"
    
    # 验证时间戳格式
    try:
        timestamp = int(headers['X-Timestamp'])
        current_time = int(time.time())
        
        # 时间戳不能是未来时间
        if timestamp > current_time + 60:  # 允许1分钟的时钟误差
            return False, "时间戳不能是未来时间"
        
        # 时间戳不能太老
        if current_time - timestamp > 3600:  # 1小时
            return False, "时间戳过期"
            
    except ValueError:
        return False, "时间戳格式不正确"
    
    # 验证nonce格式
    nonce = headers['X-Nonce']
    if len(nonce) < 16 or len(nonce) > 64:
        return False, "随机数长度不正确"
    
    # 验证签名格式
    signature = headers['X-Signature']
    if len(signature) != 64:  # SHA256十六进制字符串长度
        return False, "签名格式不正确"
    
    # 检查签名是否为有效的十六进制
    try:
        int(signature, 16)
    except ValueError:
        return False, "签名不是有效的十六进制字符串"
    
    return True, "头部格式验证通过"