"""
统一输入验证模块
实现全面的数据验证、清理和安全检查
"""
import re
import html
import json
import bleach
from typing import Any, Dict, List, Optional, Union
from marshmallow import Schema, fields, validate, ValidationError, post_load
from flask import current_app


class ValidationRules:
    """验证规则常量"""
    
    # 用户相关
    USERNAME = r'^[a-zA-Z0-9_\u4e00-\u9fa5]{3,20}$'
    PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$'
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE = r'^1[3-9]\d{9}$'
    ID_CARD = r'^\d{17}[\dXx]$'
    
    # 网络相关
    IP_ADDRESS = r'^(\d{1,3}\.){3}\d{1,3}$'
    MAC_ADDRESS = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    URL = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    
    # 系统相关
    ASSET_CODE = r'^[A-Z]{2}\d{8}$'
    VERSION = r'^\d+\.\d+\.\d+$'
    
    # 危险模式
    SQL_INJECTION_PATTERNS = [
        r'(union|select|insert|update|delete|drop|create|alter|exec|execute)',
        r'(script|javascript|vbscript|onload|onerror|onclick)',
        r'(<|>|&lt;|&gt;|%3C|%3E)',
        r'(\'|"|;|--|\/\*|\*\/)'
    ]
    
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>'
    ]


class SecurityValidator:
    """安全验证器"""
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """检查SQL注入"""
        if not isinstance(value, str):
            return False
            
        value_lower = value.lower()
        for pattern in ValidationRules.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def check_xss(value: str) -> bool:
        """检查XSS攻击"""
        if not isinstance(value, str):
            return False
            
        for pattern in ValidationRules.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def check_path_traversal(value: str) -> bool:
        """检查路径遍历攻击"""
        if not isinstance(value, str):
            return False
            
        dangerous_patterns = ['../', '..\\', '%2e%2e%2f', '%2e%2e%5c']
        value_lower = value.lower()
        
        return any(pattern in value_lower for pattern in dangerous_patterns)
    
    @staticmethod
    def sanitize_html(value: str, allowed_tags: List[str] = None) -> str:
        """清理HTML内容"""
        if not isinstance(value, str):
            return str(value)
        
        if allowed_tags is None:
            allowed_tags = []
        
        # 使用bleach清理HTML
        clean_value = bleach.clean(
            value, 
            tags=allowed_tags,
            attributes={},
            strip=True
        )
        
        return clean_value
    
    @staticmethod
    def escape_special_chars(value: str) -> str:
        """转义特殊字符"""
        if not isinstance(value, str):
            return str(value)
        
        # HTML转义
        escaped = html.escape(value, quote=True)
        
        # 额外的安全转义
        dangerous_chars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;',
            '\\': '&#x5C;',
            '\x00': '',  # NULL字符
        }
        
        for char, replacement in dangerous_chars.items():
            escaped = escaped.replace(char, replacement)
        
        return escaped


class EnhancedField(fields.Field):
    """增强的字段基类"""
    
    def __init__(self, *args, allow_sql_injection=False, allow_xss=False, 
                 allow_path_traversal=False, sanitize_html=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_sql_injection = allow_sql_injection
        self.allow_xss = allow_xss
        self.allow_path_traversal = allow_path_traversal
        self.sanitize_html = sanitize_html
    
    def _validate_security(self, value):
        """安全验证"""
        if not isinstance(value, str):
            return
        
        # SQL注入检查
        if not self.allow_sql_injection and SecurityValidator.check_sql_injection(value):
            raise ValidationError("输入包含潜在的SQL注入攻击代码")
        
        # XSS检查
        if not self.allow_xss and SecurityValidator.check_xss(value):
            raise ValidationError("输入包含潜在的XSS攻击代码")
        
        # 路径遍历检查
        if not self.allow_path_traversal and SecurityValidator.check_path_traversal(value):
            raise ValidationError("输入包含潜在的路径遍历攻击代码")
    
    def _deserialize(self, value, attr, data, **kwargs):
        """反序列化时进行安全检查"""
        # 先进行安全验证
        self._validate_security(value)
        
        # 调用父类方法
        result = super()._deserialize(value, attr, data, **kwargs)
        
        # HTML清理
        if isinstance(result, str) and self.sanitize_html:
            result = SecurityValidator.sanitize_html(result)
        
        return result


class SecureString(EnhancedField, fields.String):
    """安全字符串字段"""
    pass


class SecureEmail(EnhancedField, fields.Email):
    """安全邮箱字段"""
    
    def _validate_security(self, value):
        super()._validate_security(value)
        
        # 邮箱格式验证
        if not re.match(ValidationRules.EMAIL, value):
            raise ValidationError("邮箱格式不正确")


class SecurePhone(EnhancedField, fields.String):
    """安全手机号字段"""
    
    def _validate_security(self, value):
        super()._validate_security(value)
        
        # 手机号格式验证
        if not re.match(ValidationRules.PHONE, value):
            raise ValidationError("手机号格式不正确")


class SecurePassword(EnhancedField, fields.String):
    """安全密码字段"""
    
    def _validate_security(self, value):
        # 密码字段不进行XSS检查（因为可能包含特殊字符）
        if not self.allow_sql_injection and SecurityValidator.check_sql_injection(value):
            raise ValidationError("密码包含非法字符")
        
        # 密码强度验证
        if not re.match(ValidationRules.PASSWORD, value):
            raise ValidationError("密码必须包含大小写字母和数字，长度至少8位")


class SecureIPAddress(EnhancedField, fields.String):
    """安全IP地址字段"""
    
    def _validate_security(self, value):
        super()._validate_security(value)
        
        # IP地址格式验证
        if not re.match(ValidationRules.IP_ADDRESS, value):
            raise ValidationError("IP地址格式不正确")
        
        # 检查是否为私有IP或本地IP
        parts = value.split('.')
        if len(parts) == 4:
            try:
                first = int(parts[0])
                second = int(parts[1])
                
                # 检查保留地址
                if first == 0 or first == 127 or first >= 224:
                    raise ValidationError("不允许使用保留IP地址")
                
                # 可以根据需要添加更多IP限制
                
            except ValueError:
                raise ValidationError("IP地址格式不正确")


class CommonValidationSchema(Schema):
    """通用验证模式基类"""
    
    @post_load
    def make_secure(self, data, **kwargs):
        """后处理：额外的安全检查"""
        # 检查字段组合的安全性
        self._validate_field_combinations(data)
        
        # 记录验证日志
        if current_app:
            current_app.logger.debug(f"数据验证通过: {list(data.keys())}")
        
        return data
    
    def _validate_field_combinations(self, data):
        """验证字段组合的安全性"""
        # 可以在这里添加跨字段的安全验证逻辑
        pass


class UserRegistrationSchema(CommonValidationSchema):
    """用户注册验证模式"""
    
    username = SecureString(
        required=True,
        validate=validate.Regexp(ValidationRules.USERNAME, error="用户名只能包含字母、数字、下划线和中文，长度3-20位")
    )
    password = SecurePassword(required=True)
    confirm_password = SecureString(required=True)
    email = SecureEmail(required=True)
    phone = SecurePhone(allow_none=True)
    real_name = SecureString(
        allow_none=True,
        validate=validate.Length(max=50, error="真实姓名长度不能超过50位")
    )
    
    @post_load
    def validate_passwords(self, data, **kwargs):
        """验证密码确认"""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError({'confirm_password': ['密码确认不匹配']})
        
        # 移除确认密码字段
        data.pop('confirm_password', None)
        
        return super().make_secure(data, **kwargs)


class AssetCreateSchema(CommonValidationSchema):
    """资产创建验证模式"""
    
    asset_code = SecureString(
        allow_none=True,
        validate=validate.Regexp(ValidationRules.ASSET_CODE, error="资产编码格式不正确")
    )
    name = SecureString(
        required=True,
        validate=validate.Length(min=1, max=100, error="资产名称长度1-100位")
    )
    brand = SecureString(
        allow_none=True,
        validate=validate.Length(max=50, error="品牌长度不能超过50位")
    )
    model = SecureString(
        allow_none=True,
        validate=validate.Length(max=50, error="型号长度不能超过50位")
    )
    ip_address = SecureIPAddress(allow_none=True)
    mac_address = SecureString(
        allow_none=True,
        validate=validate.Regexp(ValidationRules.MAC_ADDRESS, error="MAC地址格式不正确")
    )


class NetworkDeviceSchema(CommonValidationSchema):
    """网络设备验证模式"""
    
    name = SecureString(required=True, validate=validate.Length(min=1, max=100))
    device_type = SecureString(required=True, validate=validate.Length(min=1, max=50))
    ip_address = SecureIPAddress(required=True)
    mac_address = SecureString(
        allow_none=True,
        validate=validate.Regexp(ValidationRules.MAC_ADDRESS, error="MAC地址格式不正确")
    )


def validate_request_data(schema_class: type, data: Dict) -> Dict:
    """
    验证请求数据
    
    Args:
        schema_class: 验证模式类
        data: 待验证的数据
        
    Returns:
        验证后的清理数据
        
    Raises:
        ValidationError: 验证失败
    """
    try:
        schema = schema_class()
        validated_data = schema.load(data)
        return validated_data
    except ValidationError as e:
        current_app.logger.warning(f"数据验证失败: {e.messages}")
        raise e
    except Exception as e:
        current_app.logger.error(f"数据验证异常: {str(e)}")
        raise ValidationError({"error": ["数据验证失败"]})


def sanitize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    清理查询参数
    
    Args:
        params: 查询参数字典
        
    Returns:
        清理后的参数字典
    """
    sanitized = {}
    
    for key, value in params.items():
        if isinstance(value, str):
            # 安全检查
            if SecurityValidator.check_sql_injection(value):
                current_app.logger.warning(f"查询参数包含SQL注入风险: {key}")
                continue
            
            if SecurityValidator.check_xss(value):
                current_app.logger.warning(f"查询参数包含XSS风险: {key}")
                continue
            
            # 清理和转义
            sanitized[key] = SecurityValidator.escape_special_chars(value)
        else:
            sanitized[key] = value
    
    return sanitized


def validate_json_structure(data: Any, max_depth: int = 10, max_keys: int = 100) -> bool:
    """
    验证JSON结构的安全性
    
    Args:
        data: JSON数据
        max_depth: 最大嵌套深度
        max_keys: 最大键数量
        
    Returns:
        是否安全
    """
    def count_depth(obj, current_depth=0):
        if current_depth > max_depth:
            return False
        
        if isinstance(obj, dict):
            if len(obj) > max_keys:
                return False
            return all(count_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if len(obj) > max_keys:
                return False
            return all(count_depth(item, current_depth + 1) for item in obj)
        else:
            return True
    
    return count_depth(data)