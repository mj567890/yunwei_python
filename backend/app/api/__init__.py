"""
API蓝图初始化
"""
from flask import Blueprint


def init_api(app):
    """初始化所有API蓝图"""
    
    # 创建API主蓝图
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    
    # 注册各模块蓝图
    from app.api.auth import auth_bp
    from app.api.user import user_bp
    from app.api.location import location_bp
    from app.api.asset import asset_bp
    from app.api.network import network_bp
    from app.api.maintenance import maintenance_bp
    from app.api.fault import fault_bp
    from app.api.statistics import statistics_bp
    from app.api.file import file_bp
    from app.api.health import health_bp
    from app.api.monitor import monitor_bp
    from app.api.asset_port import port_bp
    from app.api.category import category_bp
    
    # 注册子蓝图
    api_bp.register_blueprint(auth_bp, url_prefix='/auth')
    api_bp.register_blueprint(user_bp, url_prefix='/users')
    api_bp.register_blueprint(location_bp, url_prefix='/locations')
    api_bp.register_blueprint(asset_bp, url_prefix='/assets')
    api_bp.register_blueprint(network_bp, url_prefix='/network')
    api_bp.register_blueprint(maintenance_bp, url_prefix='/maintenance')
    api_bp.register_blueprint(fault_bp, url_prefix='/faults')
    api_bp.register_blueprint(statistics_bp, url_prefix='/statistics')
    api_bp.register_blueprint(file_bp, url_prefix='/files')
    api_bp.register_blueprint(monitor_bp, url_prefix='/monitor')
    api_bp.register_blueprint(port_bp)  # 端口管理API
    api_bp.register_blueprint(category_bp, url_prefix='/categories')  # 类别管理API
    
    # 注册健康检查蓝图（直接在根路径下）
    app.register_blueprint(health_bp)
    
    # 注册主蓝图到应用
    app.register_blueprint(api_bp)
    
    # 注册错误处理器
    from app.utils.exceptions import register_error_handlers
    register_error_handlers(app)
    
    # 添加健康检查接口
    @api_bp.route('/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        from app.utils.response import ApiResponse
        return ApiResponse.success({"status": "healthy", "service": "IT运维综合管理系统"}, "服务正常运行")
    
    return api_bp