"""
响应工具类
"""
from flask import jsonify
from typing import Any, Dict, Optional


class ApiResponse:
    """API响应格式化工具"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200) -> Dict:
        """成功响应"""
        response = {
            "code": code,
            "success": True,
            "message": message,
            "data": data,
            "timestamp": __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(response)
    
    @staticmethod
    def error(message: str = "操作失败", code: int = 400, data: Any = None) -> Dict:
        """错误响应"""
        response = {
            "code": code,
            "success": False,
            "message": message,
            "data": data,
            "timestamp": __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(response)
    
    @staticmethod
    def page_success(data: list, total: int, page: int = 1, page_size: int = 20, 
                    message: str = "查询成功") -> Dict:
        """分页成功响应"""
        response = {
            "code": 200,
            "success": True,
            "message": message,
            "data": {
                "list": data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            },
            "timestamp": __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(response)
    
    @staticmethod
    def unauthorized(message: str = "未授权访问") -> Dict:
        """未授权响应"""
        return ApiResponse.error(message, 401)
    
    @staticmethod
    def forbidden(message: str = "权限不足") -> Dict:
        """禁止访问响应"""
        return ApiResponse.error(message, 403)
    
    @staticmethod
    def not_found(message: str = "资源不存在") -> Dict:
        """资源不存在响应"""
        return ApiResponse.error(message, 404)
    
    @staticmethod
    def validation_error(message: str = "参数验证失败", errors: Dict = None) -> Dict:
        """参数验证错误响应"""
        return ApiResponse.error(message, 422, errors)