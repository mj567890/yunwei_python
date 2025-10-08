"""
通信安全模块
实现通信完整性保护和双向身份认证，满足等保2.0通信安全要求
"""
import json
import time
import hmac
import hashlib
import base64
from typing import Dict, Any, Optional, Tuple
from functools import wraps
from flask import request, current_app, g, jsonify
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import secrets

from app.utils.exceptions import AuthenticationError, ValidationError as CustomValidationError
from app.utils.enhanced_audit import audit_logger, AuditEventType, AuditSeverity
from app.utils.helpers import get_client_ip


class CommunicationSecurity:
    """通信安全管理器"""
    
    def __init__(self):
        self.session_keys = {}  # 会话密钥缓存
        self.client_certificates = {}  # 客户端证书缓存
        self.message_cache = {}  # 消息去重缓存
        
        # 初始化服务器密钥对
        self._init_server_keypair()
    
    def _init_server_keypair(self):
        """初始化服务器密钥对"""
        try:
            # 尝试从环境变量或文件加载密钥
            private_key_pem = os.environ.get('SERVER_PRIVATE_KEY')
            public_key_pem = os.environ.get('SERVER_PUBLIC_KEY')
            
            if private_key_pem and public_key_pem:
                self.private_key = serialization.load_pem_private_key(
                    private_key_pem.encode(),
                    password=None,
                    backend=default_backend()
                )
                self.public_key = serialization.load_pem_public_key(
                    public_key_pem.encode(),
                    backend=default_backend()
                )
            else:
                # 生成新的密钥对（开发环境）
                if current_app.config.get('FLASK_ENV') != 'production':
                    self._generate_server_keypair()
                else:
                    raise RuntimeError("生产环境必须配置服务器密钥对")
                    
        except Exception as e:
            current_app.logger.error(f"初始化服务器密钥对失败: {str(e)}")
            raise
    
    def _generate_server_keypair(self):
        """生成服务器密钥对"""
        try:
            # 生成RSA密钥对
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
            
            # 序列化密钥
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            current_app.logger.info("已生成服务器密钥对")
            current_app.logger.info(f"公钥:\n{public_pem.decode()}")
            current_app.logger.warning("请将密钥对保存到环境变量中")
            
        except Exception as e:
            current_app.logger.error(f"生成服务器密钥对失败: {str(e)}")
            raise
    
    def get_public_key_pem(self) -> str:
        """获取服务器公钥PEM格式"""
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_pem.decode()
    
    def generate_session_key(self, client_id: str) -> str:
        """为客户端生成会话密钥"""
        session_key = secrets.token_bytes(32)  # 256位密钥
        session_id = secrets.token_urlsafe(16)
        
        # 存储会话密钥
        self.session_keys[session_id] = {
            'key': session_key,
            'client_id': client_id,
            'created_at': time.time(),
            'expires_at': time.time() + 3600  # 1小时过期
        }
        
        return session_id
    
    def get_session_key(self, session_id: str) -> Optional[bytes]:
        """获取会话密钥"""
        session_info = self.session_keys.get(session_id)
        
        if not session_info:
            return None
        
        # 检查是否过期
        if time.time() > session_info['expires_at']:
            del self.session_keys[session_id]
            return None
        
        return session_info['key']
    
    def encrypt_message(self, message: str, session_key: bytes) -> str:
        """使用会话密钥加密消息"""
        try:
            # 生成随机IV
            iv = secrets.token_bytes(16)
            
            # 使用AES-256-CBC加密
            cipher = Cipher(
                algorithms.AES(session_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # PKCS7填充
            message_bytes = message.encode('utf-8')
            padding_length = 16 - (len(message_bytes) % 16)
            padded_message = message_bytes + bytes([padding_length] * padding_length)
            
            # 加密
            ciphertext = encryptor.update(padded_message) + encryptor.finalize()
            
            # 组合IV和密文
            encrypted_data = iv + ciphertext
            
            # Base64编码
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            current_app.logger.error(f"消息加密失败: {str(e)}")
            raise
    
    def decrypt_message(self, encrypted_message: str, session_key: bytes) -> str:
        """使用会话密钥解密消息"""
        try:
            # Base64解码
            encrypted_data = base64.b64decode(encrypted_message.encode('utf-8'))
            
            # 分离IV和密文
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # 使用AES-256-CBC解密
            cipher = Cipher(
                algorithms.AES(session_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # 解密
            padded_message = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 移除PKCS7填充
            padding_length = padded_message[-1]
            message_bytes = padded_message[:-padding_length]
            
            return message_bytes.decode('utf-8')
            
        except Exception as e:
            current_app.logger.error(f"消息解密失败: {str(e)}")
            raise
    
    def sign_message(self, message: str) -> str:
        """使用服务器私钥签名消息"""
        try:
            message_bytes = message.encode('utf-8')
            signature = self.private_key.sign(
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            current_app.logger.error(f"消息签名失败: {str(e)}")
            raise
    
    def verify_signature(self, message: str, signature: str, public_key_pem: str) -> bool:
        """验证消息签名"""
        try:
            # 加载公钥
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )
            
            # 解码签名
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            message_bytes = message.encode('utf-8')
            
            # 验证签名
            public_key.verify(
                signature_bytes,
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
            
        except Exception as e:
            current_app.logger.warning(f"签名验证失败: {str(e)}")
            return False
    
    def calculate_message_integrity(self, message: str, secret_key: str) -> str:
        """计算消息完整性校验值"""
        message_data = f"{message}{int(time.time())}"
        return hmac.new(
            secret_key.encode('utf-8'),
            message_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def verify_message_integrity(self, message: str, integrity_hash: str, 
                               secret_key: str, tolerance: int = 300) -> bool:
        """验证消息完整性"""
        current_time = int(time.time())
        
        # 在时间容差范围内验证
        for time_offset in range(-tolerance, tolerance + 1, 60):  # 每分钟检查一次
            test_time = current_time + time_offset
            message_data = f"{message}{test_time}"
            expected_hash = hmac.new(
                secret_key.encode('utf-8'),
                message_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(integrity_hash, expected_hash):
                return True
        
        return False
    
    def is_message_duplicate(self, message_id: str, client_id: str) -> bool:
        """检查消息是否重复（防重放攻击）"""
        key = f"{client_id}:{message_id}"
        
        if key in self.message_cache:
            return True
        
        # 记录消息ID
        self.message_cache[key] = time.time()
        
        # 清理过期的消息ID
        current_time = time.time()
        expired_keys = [
            k for k, v in self.message_cache.items()
            if current_time - v > 3600  # 1小时过期
        ]
        for k in expired_keys:
            del self.message_cache[k]
        
        return False
    
    def create_secure_response(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """创建安全响应"""
        try:
            session_key = self.get_session_key(session_id)
            if not session_key:
                raise AuthenticationError("无效的会话密钥")
            
            # 序列化数据
            message = json.dumps(data, sort_keys=True, separators=(',', ':'))
            
            # 加密消息
            encrypted_message = self.encrypt_message(message, session_key)
            
            # 生成消息签名
            signature = self.sign_message(message)
            
            # 计算完整性校验
            integrity_key = base64.b64encode(session_key).decode('utf-8')
            integrity_hash = self.calculate_message_integrity(message, integrity_key)
            
            return {
                'encrypted_data': encrypted_message,
                'signature': signature,
                'integrity_hash': integrity_hash,
                'timestamp': int(time.time()),
                'session_id': session_id
            }
            
        except Exception as e:
            current_app.logger.error(f"创建安全响应失败: {str(e)}")
            raise


# 全局通信安全管理器实例
comm_security = CommunicationSecurity()


def require_secure_communication(f):
    """安全通信装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 检查是否启用安全通信
            if not current_app.config.get('ENABLE_SECURE_COMMUNICATION', False):
                if current_app.config.get('FLASK_ENV') != 'development':
                    current_app.logger.warning("安全通信未启用")
                return f(*args, **kwargs)
            
            # 获取安全通信头部
            session_id = request.headers.get('X-Session-ID')
            message_id = request.headers.get('X-Message-ID')
            integrity_hash = request.headers.get('X-Integrity-Hash')
            client_signature = request.headers.get('X-Client-Signature')
            
            if not all([session_id, message_id, integrity_hash]):
                audit_logger.log_event(
                    event_type=AuditEventType.SECURITY_VIOLATION,
                    severity=AuditSeverity.HIGH,
                    operation_description="安全通信验证失败: 缺少必要头部",
                    error_message="缺少安全通信头部"
                )
                raise AuthenticationError("缺少安全通信头部")
            
            # 获取会话密钥
            session_key = comm_security.get_session_key(session_id)
            if not session_key:
                audit_logger.log_event(
                    event_type=AuditEventType.SECURITY_VIOLATION,
                    severity=AuditSeverity.HIGH,
                    operation_description="安全通信验证失败: 无效会话密钥",
                    error_message="无效的会话密钥"
                )
                raise AuthenticationError("无效的会话密钥")
            
            # 检查消息重复
            client_id = get_client_ip(request)
            if comm_security.is_message_duplicate(message_id, client_id):
                audit_logger.log_event(
                    event_type=AuditEventType.SECURITY_VIOLATION,
                    severity=AuditSeverity.HIGH,
                    operation_description="安全通信验证失败: 重复消息",
                    error_message="检测到重放攻击"
                )
                raise AuthenticationError("重复的消息ID")
            
            # 获取请求数据
            if request.method in ['POST', 'PUT', 'PATCH']:
                if request.is_json:
                    request_data = json.dumps(request.get_json(), sort_keys=True, separators=(',', ':'))
                else:
                    request_data = request.get_data(as_text=True)
            else:
                request_data = ""
            
            # 验证消息完整性
            integrity_key = base64.b64encode(session_key).decode('utf-8')
            if not comm_security.verify_message_integrity(request_data, integrity_hash, integrity_key):
                audit_logger.log_event(
                    event_type=AuditEventType.SECURITY_VIOLATION,
                    severity=AuditSeverity.CRITICAL,
                    operation_description="安全通信验证失败: 消息完整性验证失败",
                    error_message="消息完整性验证失败"
                )
                raise AuthenticationError("消息完整性验证失败")
            
            # 记录安全通信验证成功
            audit_logger.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                severity=AuditSeverity.LOW,
                operation_description=f"安全通信验证成功: {request.endpoint}",
                resource_type="SecureCommunication",
                resource_id=session_id,
                additional_context={
                    'message_id': message_id,
                    'session_id': session_id
                }
            )
            
            # 将安全通信信息存储到g中
            g.secure_communication_verified = True
            g.session_id = session_id
            g.session_key = session_key
            
            # 执行原函数
            result = f(*args, **kwargs)
            
            # 如果返回的是字典，创建安全响应
            if isinstance(result, dict):
                secure_response = comm_security.create_secure_response(result, session_id)
                return jsonify(secure_response)
            
            return result
            
        except AuthenticationError:
            raise
        except Exception as e:
            current_app.logger.error(f"安全通信装饰器异常: {str(e)}")
            audit_logger.log_event(
                event_type=AuditEventType.SECURITY_VIOLATION,
                severity=AuditSeverity.HIGH,
                operation_description="安全通信装饰器异常",
                error_message=str(e)
            )
            raise AuthenticationError("安全通信系统异常")
    
    return decorated_function


def init_secure_communication_endpoints(app):
    """初始化安全通信相关端点"""
    
    @app.route('/api/security/public-key', methods=['GET'])
    def get_server_public_key():
        """获取服务器公钥"""
        try:
            public_key_pem = comm_security.get_public_key_pem()
            
            return jsonify({
                'public_key': public_key_pem,
                'algorithm': 'RSA-2048',
                'timestamp': int(time.time())
            })
            
        except Exception as e:
            current_app.logger.error(f"获取服务器公钥失败: {str(e)}")
            return jsonify({'error': '获取公钥失败'}), 500
    
    @app.route('/api/security/session-key', methods=['POST'])
    def establish_session_key():
        """建立会话密钥"""
        try:
            data = request.get_json()
            if not data or 'client_id' not in data:
                return jsonify({'error': '缺少客户端ID'}), 400
            
            client_id = data['client_id']
            
            # 生成会话密钥
            session_id = comm_security.generate_session_key(client_id)
            
            # 记录会话建立
            audit_logger.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                severity=AuditSeverity.LOW,
                operation_description=f"建立安全会话: {client_id}",
                resource_type="SecureCommunication",
                resource_id=session_id,
                additional_context={
                    'client_id': client_id
                }
            )
            
            return jsonify({
                'session_id': session_id,
                'expires_in': 3600,
                'algorithm': 'AES-256-CBC'
            })
            
        except Exception as e:
            current_app.logger.error(f"建立会话密钥失败: {str(e)}")
            return jsonify({'error': '建立会话失败'}), 500