"""
使用SQLite数据库的完整服务器
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import sqlite3

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'development')

def create_full_app():
    """创建连接SQLite数据库的完整Flask应用"""
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    
    # 创建Flask应用
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = True
    
    # 启用CORS
    CORS(app, 
         origins=["http://localhost:3000", "http://127.0.0.1:3000"],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
    # SQLite数据库路径
    DB_PATH = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
    
    def get_db_connection():
        """获取数据库连接"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 返回字典格式
        return conn
    
    # 基础健康检查端点
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'IT运维系统正在运行',
            'version': '1.0.0',
            'timestamp': os.environ.get('FLASK_ENV', 'development')
        })
    
    # API健康检查
    @app.route('/api/health', methods=['GET'])
    def api_health_check():
        return jsonify({
            'status': 'success',
            'data': {
                'service': 'IT运维综合管理系统',
                'status': 'running',
                'database': 'SQLite',
                'database_path': DB_PATH
            },
            'message': '系统健康检查通过'
        })
    
    # 登录API
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def login():
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')
        
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
                        'roles': [{'id': 1, 'name': '管理员', 'code': 'admin'}]
                    },
                    'expires_in': 86400
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'code': 401,
                'message': '用户名或密码错误'
            }), 401
    
    # 获取用户信息
    @app.route('/api/auth/profile', methods=['GET'])
    def get_profile():
        return jsonify({
            'status': 'success',
            'code': 200,
            'data': {
                'id': 1,
                'username': 'admin',
                'email': 'admin@example.com',
                'real_name': '系统管理员'
            }
        })
    
    # 获取用户权限
    @app.route('/api/auth/permissions', methods=['GET'])
    def get_permissions():
        return jsonify({
            'status': 'success',
            'code': 200,
            'data': {
                'permissions': [
                    'system:view', 'system:manage',
                    'user:view', 'user:create', 'user:edit', 'user:delete',
                    'asset:view', 'asset:create', 'asset:edit', 'asset:delete'
                ],
                'roles': [{'id': 1, 'name': '管理员', 'code': 'admin'}]
            }
        })
    
    # 登出
    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '登出成功'
        })
    
    # 仪表板统计数据
    @app.route('/api/dashboard/stats', methods=['GET'])
    def dashboard_stats():
        return get_dashboard_statistics()
    
    # 统计概览API（前端兼容）
    @app.route('/api/statistics/overview', methods=['GET'])
    def statistics_overview():
        return get_dashboard_statistics()
    
    def get_dashboard_statistics():
        """获取仪表盘统计数据的共通函数"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 查询资产统计
            cursor.execute('SELECT COUNT(*) as total FROM it_asset WHERE 1=1')
            total_assets = cursor.fetchone()['total']
            
            # 查询在线设备数（假设根据状态判断）
            cursor.execute("SELECT COUNT(*) as online FROM it_asset WHERE status = '在用'")
            online_assets = cursor.fetchone()['online']
            
            # 查询离线设备数
            cursor.execute("SELECT COUNT(*) as offline FROM it_asset WHERE status != '在用'")
            offline_assets = cursor.fetchone()['offline']
            
            # 查询端口统计
            cursor.execute('SELECT COUNT(*) as total FROM asset_port')
            total_ports = cursor.fetchone()['total']
            
            cursor.execute('SELECT COUNT(*) as connected FROM asset_port WHERE is_connected = 1')
            connected_ports = cursor.fetchone()['connected']
            
            # 查询用户统计（如果有用户表）
            try:
                cursor.execute('SELECT COUNT(*) as total FROM sys_user')
                total_users = cursor.fetchone()['total']
            except:
                total_users = 0
            
            # 查询网络设备统计
            cursor.execute("SELECT COUNT(*) as total FROM it_asset WHERE category IN ('交换机', '路由器', '防火墙', '网络设备')")
            device_count = cursor.fetchone()['total']
            
            # 查询运维记录统计（如果有表）
            try:
                cursor.execute('SELECT COUNT(*) as total FROM maintenance_record')
                maintenance_count = cursor.fetchone()['total']
            except:
                maintenance_count = 0
            
            # 查询故障记录统计（如果有表）
            try:
                cursor.execute('SELECT COUNT(*) as total FROM fault_record')
                fault_count = cursor.fetchone()['total']
            except:
                fault_count = 0
            
            conn.close()
            
            return jsonify({
                'success': True,
                'status': 'success',
                'code': 200,
                'message': '获取仪表板数据成功',
                'data': {
                    'total_assets': total_assets,
                    'online_assets': online_assets,
                    'offline_assets': offline_assets,
                    'warning_assets': max(0, total_assets - online_assets - offline_assets),
                    'total_users': total_users,
                    'active_users': max(1, total_users),
                    'total_ports': total_ports,
                    'connected_ports': connected_ports,
                    'device_count': device_count,
                    'maintenance_count': maintenance_count,
                    'fault_count': fault_count,
                    'system_health': round(95.0 + (connected_ports / max(total_ports, 1)) * 5, 1),
                    'summary': {
                        'total_assets': total_assets,
                        'online_assets': online_assets,
                        'offline_assets': offline_assets,
                        'warning_assets': max(0, total_assets - online_assets - offline_assets),
                        'total_users': total_users,
                        'active_users': max(1, total_users),
                        'total_ports': total_ports,
                        'connected_ports': connected_ports,
                        'system_health': round(95.0 + (connected_ports / max(total_ports, 1)) * 5, 1)
                    }
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'status': 'error',
                'code': 500,
                'message': f'获取统计数据失败: {str(e)}'
            }), 500
    
    # 资产列表API
    @app.route('/api/assets', methods=['GET'])
    def get_assets():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            offset = (page - 1) * per_page
            
            # 查询总数
            cursor.execute('SELECT COUNT(*) as total FROM it_asset')
            total = cursor.fetchone()['total']
            
            # 查询数据
            cursor.execute('''
                SELECT id, asset_code, name, brand, model, category, 
                       status, user_name, user_department, ip_address,
                       created_at
                FROM it_asset 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (per_page, offset))
            
            assets = []
            for row in cursor.fetchall():
                assets.append(dict(row))
            
            conn.close()
            
            return jsonify({
                'status': 'success',
                'code': 200,
                'data': {
                    'list': assets,
                    'pagination': {
                        'current_page': page,
                        'per_page': per_page,
                        'total': total,
                        'total_pages': (total + per_page - 1) // per_page
                    }
                },
                'message': '获取资产列表成功'
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'code': 500,
                'message': f'获取资产列表失败: {str(e)}'
            }), 500
    
    # 网络设备列表
    @app.route('/api/network/devices', methods=['GET'])
    def get_network_devices():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 查询网络设备（根据category或者特定条件）
            cursor.execute('''
                SELECT id, asset_code, name, brand, model, category, 
                       status, ip_address, mac_address
                FROM it_asset 
                WHERE category IN ('交换机', '路由器', '防火墙', '网络设备')
                ORDER BY created_at DESC
            ''')
            
            devices = []
            for row in cursor.fetchall():
                devices.append(dict(row))
            
            conn.close()
            
            return jsonify({
                'status': 'success',
                'code': 200,
                'data': devices,
                'message': '获取网络设备列表成功'
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'code': 500,
                'message': f'获取网络设备列表失败: {str(e)}'
            }), 500
    
    # 404错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'status': 'error',
            'code': 404,
            'message': '请求的资源未找到'
        }), 404
    
    return app

def main():
    """主函数"""
    print("="*60)
    print("IT运维系统完整服务器启动（SQLite版本）")
    print("="*60)
    
    try:
        app = create_full_app()
        print("✓ Flask应用创建成功")
        print("✓ SQLite数据库连接配置完成")
        print()
        print("可用API端点:")
        print("  - GET  /api/health             - API健康检查")
        print("  - POST /api/auth/login         - 用户登录") 
        print("  - GET  /api/auth/profile       - 获取用户信息")
        print("  - GET  /api/dashboard/stats    - 仪表板统计")
        print("  - GET  /api/assets             - 资产列表")
        print("  - GET  /api/network/devices    - 网络设备列表")
        print()
        print("启动地址: http://localhost:5000")
        print("前端地址: http://localhost:3000")
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