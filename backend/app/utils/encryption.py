"""
数据加密工具模块
实现敏感数据的加密存储和解密读取
"""
import os
import base64
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app
from sqlalchemy import TypeDecorator, String, Text


class DataEncryption:
    """数据加密解密工具类"""
    
    _instance = None
    _fernet = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._fernet is None:
            self._init_encryption()
    
    def _init_encryption(self):
        """初始化加密器"""
        # 从配置获取加密密钥，如果没有则生成
        encryption_key = os.environ.get('DATA_ENCRYPTION_KEY')
        
        if not encryption_key:
            if os.environ.get('FLASK_ENV') == 'production':
                raise RuntimeError("生产环境必须设置DATA_ENCRYPTION_KEY环境变量")
            else:
                # 开发环境使用固定密钥（仅用于开发测试）
                password = b"dev-encryption-key-change-in-production"
                salt = b"dev-salt-12345678"  # 生产环境应使用随机盐值
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(password))
                encryption_key = key.decode()
        
        self._fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    def encrypt(self, data: str) -> str:
        """加密数据"""
        if not data:
            return data
        
        try:
            encrypted_data = self._fernet.encrypt(data.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            current_app.logger.error(f"数据加密失败: {str(e)}")
            raise e
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            current_app.logger.error(f"数据解密失败: {str(e)}")
            raise e
    
    @staticmethod
    def generate_key() -> str:
        """生成新的加密密钥"""
        return Fernet.generate_key().decode()


# 全局加密器实例
encryptor = DataEncryption()


class EncryptedType(TypeDecorator):
    """SQLAlchemy加密字段类型"""
    
    impl = Text
    cache_ok = True
    
    def __init__(self, *args, **kwargs):
        self.encryptor = encryptor
        super().__init__(*args, **kwargs)
    
    def process_bind_param(self, value, dialect):
        """存储时加密"""
        if value is not None:
            return self.encryptor.encrypt(str(value))
        return value
    
    def process_result_value(self, value, dialect):
        """读取时解密"""
        if value is not None:
            try:
                return self.encryptor.decrypt(value)
            except Exception as e:
                # 如果解密失败，可能是未加密的旧数据，直接返回
                current_app.logger.warning(f"解密失败，可能是未加密数据: {str(e)}")
                return value
        return value


class PartialEncryptedType(TypeDecorator):
    """部分加密字段类型（如手机号、邮箱等）"""
    
    impl = String(255)
    cache_ok = True
    
    def __init__(self, *args, **kwargs):
        self.encryptor = encryptor
        super().__init__(*args, **kwargs)
    
    def process_bind_param(self, value, dialect):
        """存储时加密"""
        if value is not None:
            return self.encryptor.encrypt(str(value))
        return value
    
    def process_result_value(self, value, dialect):
        """读取时解密"""
        if value is not None:
            try:
                return self.encryptor.decrypt(value)
            except Exception:
                # 解密失败，可能是未加密的旧数据
                return value
        return value


def mask_sensitive_data(data: str, mask_char: str = '*', visible_start: int = 3, visible_end: int = 3) -> str:
    """
    掩码敏感数据显示
    
    Args:
        data: 原始数据
        mask_char: 掩码字符
        visible_start: 开始显示的字符数
        visible_end: 结尾显示的字符数
    
    Returns:
        掩码后的数据
    """
    if not data or len(data) <= visible_start + visible_end:
        return mask_char * len(data) if data else ""
    
    start_part = data[:visible_start]
    end_part = data[-visible_end:] if visible_end > 0 else ""
    middle_part = mask_char * (len(data) - visible_start - visible_end)
    
    return start_part + middle_part + end_part


def is_sensitive_field(field_name: str) -> bool:
    """
    判断字段是否为敏感字段
    
    Args:
        field_name: 字段名称
    
    Returns:
        是否为敏感字段
    """
    sensitive_fields = {
        'password', 'password_hash', 'phone', 'email', 'id_card', 
        'bank_account', 'credit_card', 'ssn', 'tax_id', 'private_key',
        'secret_key', 'api_key', 'token', 'session_id'
    }
    
    return field_name.lower() in sensitive_fields or any(
        sensitive in field_name.lower() 
        for sensitive in ['password', 'secret', 'private', 'key', 'token']
    )