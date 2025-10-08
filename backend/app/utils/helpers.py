"""
工具函数模块
"""
import os
import uuid
import hashlib
import re
import magic
from datetime import datetime
from typing import Optional, List, Dict, Any
from werkzeug.utils import secure_filename


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    # 获取文件扩展名
    ext = os.path.splitext(original_filename)[1]
    # 生成UUID作为文件名
    unique_name = str(uuid.uuid4())
    return f"{unique_name}{ext}"


def get_file_hash(file_path: str) -> Optional[str]:
    """计算文件MD5哈希"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_ip_address(ip: str) -> bool:
    """验证IP地址格式"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)


def validate_mac_address(mac: str) -> bool:
    """验证MAC地址格式"""
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f}{size_names[i]}"


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """检查文件是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file_content(file_path: str, expected_extensions: set) -> bool:
    """验证文件内容与扩展名是否匹配"""
    try:
        # 使用python-magic检测文件真实类型
        file_type = magic.from_file(file_path, mime=True)
        
        # 定义MIME类型映射
        mime_to_ext = {
            'image/jpeg': {'jpg', 'jpeg'},
            'image/png': {'png'},
            'image/gif': {'gif'},
            'application/pdf': {'pdf'},
            'application/msword': {'doc'},
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {'docx'},
            'application/vnd.ms-excel': {'xls'},
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {'xlsx'},
            'text/plain': {'txt'},
        }
        
        # 检查MIME类型是否在允许列表中
        if file_type in mime_to_ext:
            detected_extensions = mime_to_ext[file_type]
            return bool(detected_extensions.intersection(expected_extensions))
        
        return False
    except Exception:
        # 如果python-magic不可用，返回True跳过检查
        return True


def check_file_size(file_path: str, max_size: int) -> bool:
    """检查文件大小"""
    try:
        return os.path.getsize(file_path) <= max_size
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除危险字符"""
    # 使用werkzeug的secure_filename
    filename = secure_filename(filename)
    
    # 进一步清理
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '..', '//', '\\\\']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    return filename


def generate_asset_code(category: str, count: int = None) -> str:
    """生成资产编码"""
    # 类别前缀映射
    category_prefix = {
        '服务器': 'SV',
        '工作站': 'WS', 
        '笔记本电脑': 'LT',
        '打印机': 'PR',
        '交换机': 'SW',
        '路由器': 'RT',
        '防火墙': 'FW'
    }
    
    prefix = category_prefix.get(category, 'AS')
    year = datetime.now().year
    
    if count is None:
        # 使用当前时间戳作为序号
        timestamp = int(datetime.now().timestamp())
        sequence = str(timestamp)[-6:]  # 取后6位
    else:
        sequence = str(count + 1).zfill(4)
    
    return f"{prefix}{year}{sequence}"


def generate_fault_code() -> str:
    """生成故障编号"""
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    time_str = now.strftime('%H%M%S')
    return f"FT{date_str}{time_str}"


def parse_ids_string(ids_str: str) -> List[int]:
    """解析ID字符串为整数列表"""
    if not ids_str:
        return []
    
    ids = []
    for id_str in ids_str.split(','):
        id_str = id_str.strip()
        if id_str.isdigit():
            ids.append(int(id_str))
    
    return ids


def format_duration(seconds: float) -> str:
    """格式化时长"""
    if seconds is None:
        return ""
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}小时{minutes}分钟"
    elif minutes > 0:
        return f"{minutes}分钟{seconds}秒"
    else:
        return f"{seconds}秒"


def sanitize_input(text: str, max_length: int = None) -> str:
    """清理用户输入"""
    if not text:
        return ""
    
    # 移除首尾空白
    text = text.strip()
    
    # 限制长度
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    # 移除危险字符
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text


def dict_to_query_params(params: Dict[str, Any]) -> str:
    """字典转查询参数字符串"""
    if not params:
        return ""
    
    param_list = []
    for key, value in params.items():
        if value is not None:
            param_list.append(f"{key}={value}")
    
    return "&".join(param_list)


def get_client_ip(request) -> str:
    """获取客户端IP地址"""
    # 检查代理头部
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or 'unknown'


def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """掩码敏感数据"""
    if not data or len(data) <= visible_chars:
        return data
    
    visible_part = data[:visible_chars]
    masked_part = mask_char * (len(data) - visible_chars)
    return visible_part + masked_part