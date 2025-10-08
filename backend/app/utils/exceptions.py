"""
异常处理模块
"""
from flask import current_app, request
from app.utils.response import ApiResponse
from app.utils.helpers import get_client_ip


class ITOpsException(Exception):
    """IT运维系统自定义异常基类"""
    
    def __init__(self, message: str, code: int = 400, data=None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)


class ValidationError(ITOpsException):
    """参数验证异常"""
    
    def __init__(self, message: str = "参数验证失败", errors=None):
        super().__init__(message, 422, errors)


class AuthenticationError(ITOpsException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, 401)


class AuthorizationError(ITOpsException):
    """授权异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, 403)


class ResourceNotFoundError(ITOpsException):
    """资源不存在异常"""
    
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, 404)


class BusinessError(ITOpsException):
    """业务异常"""
    
    def __init__(self, message: str = "业务处理失败"):
        super().__init__(message, 400)


class DatabaseError(ITOpsException):
    """数据库异常"""
    
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, 500)


class FileError(ITOpsException):
    """文件操作异常"""
    
    def __init__(self, message: str = "文件操作失败"):
        super().__init__(message, 400)


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(ITOpsException)
    def handle_itops_exception(error):
        """处理自定义异常"""
        current_app.logger.error(f"ITOps异常: {error.message}")
        return ApiResponse.error(error.message, error.code, error.data)
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """处理验证异常"""
        current_app.logger.warning(f"参数验证异常: {error.message}")
        return ApiResponse.validation_error(error.message, error.data)
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        """处理认证异常"""
        current_app.logger.warning(f"认证失败: {error.message} - IP: {get_client_ip(request)}")
        return ApiResponse.unauthorized(error.message)
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        """处理授权异常"""
        current_app.logger.warning(f"权限不足: {error.message} - IP: {get_client_ip(request)}")
        return ApiResponse.forbidden(error.message)
    
    @app.errorhandler(ResourceNotFoundError)
    def handle_not_found_error(error):
        """处理资源不存在异常"""
        current_app.logger.info(f"资源不存在: {error.message}")
        return ApiResponse.not_found(error.message)
    
    @app.errorhandler(404)
    def handle_404_error(error):
        """处理404异常"""
        return ApiResponse.not_found("请求的资源不存在")
    
    @app.errorhandler(405)
    def handle_405_error(error):
        """处理方法不允许异常"""
        return ApiResponse.error("请求方法不被允许", 405)
    
    @app.errorhandler(500)
    def handle_500_error(error):
        """处理服务器内部异常"""
        current_app.logger.error(f"服务器内部错误: {str(error)}")
        return ApiResponse.error("服务器内部错误", 500)
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """处理通用异常"""
        current_app.logger.error(f"未处理的异常: {str(error)}", exc_info=True)
        
        # 开发环境显示详细错误
        if app.debug:
            return ApiResponse.error(f"系统错误: {str(error)}", 500)
        else:
            return ApiResponse.error("系统暂时不可用，请稍后再试", 500)