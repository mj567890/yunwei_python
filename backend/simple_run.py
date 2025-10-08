"""
简化的系统启动脚本，用于开发测试
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'development')

def create_simple_app():
    """创建简化的Flask应用用于测试"""
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    
    # 创建Flask应用
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = True
    
    # 启用CORS - 支持前端开发服务器
    CORS(app, 
         origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3002", "http://127.0.0.1:3002", "http://localhost:3003", "http://127.0.0.1:3003"],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
    # 根路径端点
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'message': '欢迎使用IT运维综合管理系统',
            'version': '1.0.0',
            'status': 'running',
            'available_endpoints': {
                'health': '/health',
                'api_health': '/api/health',
                'security_test': '/api/test/security',
                'monitoring_test': '/api/test/monitoring'
            },
            'documentation': {
                'swagger': '/api/docs',
                'redoc': '/api/redoc'
            }
        })
    
    # favicon端点
    @app.route('/favicon.ico', methods=['GET'])
    def favicon():
        return '', 204  # 返回空内容，状态码204
    
    # 基础健康检查端点
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'IT运维系统正在运行',
            'version': '1.0.0',
            'timestamp': os.environ.get('FLASK_ENV', 'development')
        })
    
    # API根端点
    @app.route('/api', methods=['GET'])
    @app.route('/api/', methods=['GET'])
    def api_index():
        return jsonify({
            'status': 'success',
            'message': 'IT运维系统API服务',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'security_test': '/api/test/security',
                'monitoring_test': '/api/test/monitoring'
            }
        })
    
    # API根端点
    @app.route('/api/health', methods=['GET'])
    def api_health_check():
        return jsonify({
            'status': 'success',
            'data': {
                'service': 'IT运维综合管理系统',
                'status': 'running',
                'environment': os.environ.get('FLASK_ENV', 'development'),
                'security_features': {
                    'api_signature': os.environ.get('ENABLE_API_SIGNATURE', 'false') == 'true',
                    'anomaly_detection': os.environ.get('ENABLE_ANOMALY_DETECTION', 'false') == 'true',
                    'performance_monitoring': os.environ.get('PERFORMANCE_MONITORING', 'true') == 'true'
                }
            },
            'message': '系统健康检查通过'
        })
    
    # 测试安全功能
    @app.route('/api/test/security', methods=['GET'])
    def test_security():
        import hashlib
        import hmac
        import secrets
        
        # 测试基础加密功能
        test_data = "security_test_data"
        
        results = {
            'sha256_hash': hashlib.sha256(test_data.encode()).hexdigest()[:16] + "...",
            'hmac_signature': hmac.new(
                secrets.token_bytes(32), 
                test_data.encode(), 
                hashlib.sha256
            ).hexdigest()[:16] + "...",
            'random_token': secrets.token_urlsafe(16),
            'timestamp': str(int(__import__('time').time()))
        }
        
        return jsonify({
            'status': 'success',
            'data': results,
            'message': '安全功能测试通过'
        })
    
    # 测试认证API
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def test_login():
        # 处理预检请求
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')
        
        # 简单验证（仅用于测试）
        if username == 'admin' and password == 'admin123':
            import secrets
            access_token = secrets.token_urlsafe(32)
            
            return jsonify({
                'status': 'success',
                'code': 200,
                'message': '登录成功',
                'data': {
                    'access_token': access_token,
                    'refresh_token': secrets.token_urlsafe(32),
                    'user': {
                        'id': 1,
                        'username': username,
                        'email': 'admin@example.com',
                        'real_name': '系统管理员',
                        'roles': [{
                            'id': 1,
                            'name': '管理员',
                            'code': 'admin'
                        }]
                    },
                    'expires_in': 86400
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'code': 401,
                'message': '用户名或密码错误',
                'timestamp': datetime.now().isoformat()
            }), 401
    
    @app.route('/api/auth/logout', methods=['POST'])
    def test_logout():
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '登出成功',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/auth/profile', methods=['GET'])
    def test_profile():
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取用户信息成功',
            'data': {
                'id': 1,
                'username': 'admin',
                'email': 'admin@example.com',
                'real_name': '系统管理员',
                'roles': [{
                    'id': 1,
                    'name': '管理员',
                    'code': 'admin'
                }]
            },
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/auth/permissions', methods=['GET'])
    def test_permissions():
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取用户权限成功',
            'data': {
                'permissions': [
                    'system:view', 'system:manage',
                    'user:view', 'user:create', 'user:edit', 'user:delete',
                    'asset:view', 'asset:create', 'asset:edit', 'asset:delete',
                    'network:view', 'network:manage',
                    'statistics:view'
                ],
                'roles': [{
                    'id': 1,
                    'name': '管理员',
                    'code': 'admin'
                }]
            },
            'timestamp': datetime.now().isoformat()
        })
    @app.route('/api/test/monitoring', methods=['GET'])
    def test_monitoring():
        try:
            import psutil
            
            system_info = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('.' if sys.platform != 'win32' else 'C:').used / psutil.disk_usage('.' if sys.platform != 'win32' else 'C:').total * 100,
                'process_count': len(psutil.pids())
            }
            
            return jsonify({
                'status': 'success',
                'data': system_info,
                'message': '系统监控功能正常'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'监控功能测试失败: {str(e)}'
            })
    
    # 404错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'status': 'error',
            'code': 404,
            'message': '请求的资源未找到',
            'available_endpoints': {
                '根路径': '/',
                '健康检查': '/health',
                'API根目录': '/api',
                'API健康检查': '/api/health',
                '安全功能测试': '/api/test/security',
                '监控功能测试': '/api/test/monitoring'
            }
        }), 404
    
    # 500错误处理
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '内部服务器错误',
            'details': '请检查服务器日志获取更多信息'
        }), 500
    
    return app


def add_demo_apis(app):
    """添加演示用的API端点"""
    
    # 测试仪表板API
    @app.route('/api/dashboard/stats', methods=['GET'])
    def dashboard_stats():
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取仪表板数据成功',
            'data': {
                'summary': {
                    'total_assets': 156,
                    'online_assets': 142,
                    'offline_assets': 14,
                    'warning_assets': 8,
                    'total_users': 25,
                    'active_users': 18,
                    'system_health': 95.2
                }
            },
            'timestamp': datetime.now().isoformat()
        })

def main():
    """主函数"""
    print("="*60)
    print("IT运维系统简化启动测试")
    print("="*60)
    
    try:
        app = create_simple_app()
        add_demo_apis(app)  # 添加演示用API
        print("✓ Flask应用创建成功")
        print("✓ 基础功能加载完成")
        print()
        print("可用端点:")
        print("  - GET  /health          - 基础健康检查")
        print("  - GET  /api/health      - API健康检查") 
        print("  - GET  /api/test/security   - 安全功能测试")
        print("  - GET  /api/test/monitoring - 监控功能测试")
        print()
        print("启动地址: http://localhost:5000")
        print("按 Ctrl+C 停止服务")
        print("="*60)
        
        # 启动应用
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n✓ 系统已停止")
    except Exception as e:
        print(f"✗ 启动失败: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    main()