"""
文件安全验证工具模块
实现文件类型验证、内容检查和安全扫描
"""
import os
import mimetypes
from typing import Optional, Tuple, List
from werkzeug.datastructures import FileStorage
from flask import current_app

try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


class FileSecurityValidator:
    """文件安全验证器"""
    
    # 允许的文件扩展名和对应的MIME类型
    ALLOWED_FILE_TYPES = {
        # 图片文件
        '.png': ['image/png'],
        '.jpg': ['image/jpeg'],
        '.jpeg': ['image/jpeg'],
        '.gif': ['image/gif'],
        '.webp': ['image/webp'],
        
        # 文档文件
        '.pdf': ['application/pdf'],
        '.doc': ['application/msword'],
        '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        '.xls': ['application/vnd.ms-excel'],
        '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
        '.txt': ['text/plain'],
        
        # 压缩文件
        '.zip': ['application/zip'],
        '.rar': ['application/x-rar-compressed'],
        '.7z': ['application/x-7z-compressed'],
    }
    
    # 危险文件扩展名黑名单
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.vbs', '.js', '.jar',
        '.php', '.asp', '.aspx', '.jsp', '.py', '.rb', '.pl', '.sh', '.ps1'
    }
    
    # 文件大小限制 (字节)
    MAX_FILE_SIZES = {
        'image': 10 * 1024 * 1024,    # 10MB
        'document': 50 * 1024 * 1024,  # 50MB
        'archive': 100 * 1024 * 1024,  # 100MB
        'default': 20 * 1024 * 1024    # 20MB
    }

    @classmethod
    def validate_file(cls, file: FileStorage, allowed_types: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        验证上传文件的安全性
        
        Args:
            file: 上传的文件对象
            allowed_types: 允许的文件类型列表，如果为None则使用默认配置
            
        Returns:
            Tuple[bool, str]: (是否通过验证, 错误信息)
        """
        if not file or not file.filename:
            return False, "未选择文件"
        
        filename = file.filename.lower()
        
        # 1. 检查文件名安全性
        is_safe, msg = cls._validate_filename(filename)
        if not is_safe:
            return False, msg
        
        # 2. 检查文件扩展名
        is_safe, msg = cls._validate_extension(filename, allowed_types)
        if not is_safe:
            return False, msg
        
        # 3. 检查文件大小
        is_safe, msg = cls._validate_file_size(file, filename)
        if not is_safe:
            return False, msg
        
        # 4. 检查文件内容类型
        is_safe, msg = cls._validate_mime_type(file, filename)
        if not is_safe:
            return False, msg
        
        # 5. 检查文件内容安全性
        is_safe, msg = cls._validate_file_content(file)
        if not is_safe:
            return False, msg
        
        return True, "文件验证通过"
    
    @classmethod
    def _validate_filename(cls, filename: str) -> Tuple[bool, str]:
        """验证文件名安全性"""
        # 检查文件名长度
        if len(filename) > 255:
            return False, "文件名过长"
        
        # 检查危险字符
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/', '\x00']
        for char in dangerous_chars:
            if char in filename:
                return False, f"文件名包含非法字符: {char}"
        
        # 检查路径遍历攻击
        if '..' in filename or filename.startswith('.'):
            return False, "文件名格式不合法"
        
        return True, ""
    
    @classmethod
    def _validate_extension(cls, filename: str, allowed_types: Optional[List[str]]) -> Tuple[bool, str]:
        """验证文件扩展名"""
        ext = os.path.splitext(filename)[1].lower()
        
        if not ext:
            return False, "文件必须有扩展名"
        
        # 检查是否在危险扩展名黑名单中
        if ext in cls.DANGEROUS_EXTENSIONS:
            return False, f"不允许上传 {ext} 类型文件"
        
        # 检查是否在允许的类型中
        if allowed_types:
            if ext not in [f'.{t}' for t in allowed_types]:
                return False, f"不支持 {ext} 文件类型"
        else:
            if ext not in cls.ALLOWED_FILE_TYPES:
                return False, f"不支持 {ext} 文件类型"
        
        return True, ""
    
    @classmethod
    def _validate_file_size(cls, file: FileStorage, filename: str) -> Tuple[bool, str]:
        """验证文件大小"""
        # 移动到文件末尾获取大小
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)  # 重置到开始位置
        
        if file_size == 0:
            return False, "文件为空"
        
        # 根据文件类型确定大小限制
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            max_size = cls.MAX_FILE_SIZES['image']
            size_type = "图片"
        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt']:
            max_size = cls.MAX_FILE_SIZES['document']
            size_type = "文档"
        elif ext in ['.zip', '.rar', '.7z']:
            max_size = cls.MAX_FILE_SIZES['archive']
            size_type = "压缩"
        else:
            max_size = cls.MAX_FILE_SIZES['default']
            size_type = "默认"
        
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f"{size_type}文件大小不能超过 {max_size_mb:.1f}MB"
        
        return True, ""
    
    @classmethod
    def _validate_mime_type(cls, file: FileStorage, filename: str) -> Tuple[bool, str]:
        """验证文件MIME类型"""
        ext = os.path.splitext(filename)[1].lower()
        expected_mimes = cls.ALLOWED_FILE_TYPES.get(ext, [])
        
        if not expected_mimes:
            return True, ""  # 如果没有预期的MIME类型，跳过检查
        
        # 使用python-magic检查真实的MIME类型
        if HAS_MAGIC:
            file.seek(0)
            file_data = file.read(1024)  # 读取前1KB用于检测
            file.seek(0)  # 重置位置
            
            detected_mime = magic.from_buffer(file_data, mime=True)
            
            if detected_mime not in expected_mimes:
                current_app.logger.warning(
                    f"文件MIME类型不匹配: 文件名={filename}, "
                    f"预期={expected_mimes}, 检测到={detected_mime}"
                )
                return False, f"文件类型验证失败，检测到的类型与扩展名不匹配"
        
        # 使用标准库的mimetypes作为备选方案
        else:
            guessed_mime, _ = mimetypes.guess_type(filename)
            if guessed_mime and guessed_mime not in expected_mimes:
                return False, f"文件类型验证失败"
        
        return True, ""
    
    @classmethod
    def _validate_file_content(cls, file: FileStorage) -> Tuple[bool, str]:
        """验证文件内容安全性"""
        file.seek(0)
        
        # 读取文件头部进行基础检查
        header = file.read(512)
        file.seek(0)  # 重置位置
        
        # 检查是否包含可疑的脚本内容
        suspicious_patterns = [
            b'<script', b'javascript:', b'vbscript:', b'onload=', b'onerror=',
            b'<?php', b'<%', b'#!/bin/', b'#!/usr/bin/', b'cmd.exe', b'powershell'
        ]
        
        header_lower = header.lower()
        for pattern in suspicious_patterns:
            if pattern in header_lower:
                return False, "文件内容包含可疑代码"
        
        return True, ""
    
    @classmethod
    def get_safe_filename(cls, filename: str) -> str:
        """生成安全的文件名"""
        import uuid
        import time
        
        # 获取文件扩展名
        name, ext = os.path.splitext(filename)
        
        # 生成唯一的安全文件名
        timestamp = str(int(time.time()))
        unique_id = str(uuid.uuid4().hex[:8])
        
        # 清理原始文件名
        safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_'))[:20]
        if not safe_name:
            safe_name = "file"
        
        return f"{safe_name}_{timestamp}_{unique_id}{ext.lower()}"