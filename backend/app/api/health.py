"""
健康检查API
"""
from flask import Blueprint, jsonify
from datetime import datetime
from app.utils.response import ApiResponse
from app import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """系统健康检查"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'services': {
                'database': 'ok',
                'api': 'ok'
            }
        }
        
        return ApiResponse.success(health_data, "系统运行正常")
        
    except Exception as e:
        health_data = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'error': str(e),
            'services': {
                'database': 'error',
                'api': 'ok'
            }
        }
        
        return ApiResponse.error("系统异常", 503, health_data)


@health_bp.route('/ping', methods=['GET'])
def ping():
    """简单的ping检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })