#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT运维系统 - 简化启动脚本（专门解决CORS问题）
确保前端3001端口可以正常访问后端5000端口的API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from datetime import datetime

def create_debug_app():
    """创建专门用于调试CORS问题的Flask应用"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'debug-secret-key'
    app.config['DEBUG'] = True
    
    # 配置CORS - 使用最宽松的配置来解决连接问题
    CORS(app, 
         # 允许所有源（开发环境）
         origins="*",
         # 允许凭证
         supports_credentials=False,  # 改为False避免某些浏览器问题
         # 允许的请求头
         allow_headers="*",
         # 允许的HTTP方法
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         # 暴露的响应头
         expose_headers="*"
    )
    
    # 根路径 - 基础检查
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'message': '🚀 IT运维系统后端服务正在运行',
            'version': '1.0.0',
            'status': 'OK',
            'cors_enabled': True,
            'api_base': '/api',
            'login_endpoint': '/api/auth/login',
            'test_credentials': {
                'username': 'admin',
                'password': 'admin123'
            }
        })
    
    # 全局请求拦截 - 记录所有请求
    @app.before_request
    def log_request():
        print(f"\n🔍 [请求] {request.method} {request.url}")
        print(f"   🌐 Origin: {request.headers.get('Origin', '未知')}")
        print(f"   📦 Headers: {dict(request.headers)}")
        if request.method in ['POST', 'PUT'] and request.get_data():
            try:
                print(f"   📝 Body: {request.get_json()}")
            except:
                print(f"   📝 Body: {request.get_data()[:200]}")
    
    # 全局响应拦截 - 添加CORS头
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
        
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        
        print(f"\n✅ [响应] {response.status_code} - CORS headers added")
        return response
    
    # API健康检查
    @app.route('/api/health', methods=['GET'])
    def api_health():
        return jsonify({
            'status': 'success',
            'service': 'IT运维管理系统API',
            'timestamp': datetime.now().isoformat(),
            'cors_headers_sent': True,
            'port': 5000
        })
    
    # 登录API - 简化版本
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def login():
        """登录接口"""
        print(f"\n🔑 [登录] 收到请求 - 方法: {request.method}")
        
        # 处理预检请求
        if request.method == 'OPTIONS':
            print("✅ 处理CORS预检请求")
            return jsonify({'status': 'preflight_ok'}), 200
        
        # 获取请求数据
        try:
            data = request.get_json() or {}
            print(f"📨 请求数据: {data}")
        except Exception as e:
            print(f"❌ 解析请求数据失败: {e}")
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '请求数据格式错误'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        print(f"🔐 登录尝试 - 用户名: {username}")
        
        # 验证登录信息
        if username == 'admin' and password == 'admin123':
            import secrets
            access_token = secrets.token_urlsafe(32)
            
            response_data = {
                'status': 'success',
                'code': 200,
                'message': '🎉 登录成功！',
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
            }
            
            print("✅ 登录验证成功，返回Token")
            return jsonify(response_data)
        else:
            print(f"❌ 登录失败 - 用户名: {username}")
            return jsonify({
                'status': 'error',
                'code': 401,
                'message': '用户名或密码错误',
                'timestamp': datetime.now().isoformat()
            }), 401
    
    # 其他认证API
    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '登出成功',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/auth/profile', methods=['GET'])
    def profile():
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取用户信息成功',
            'data': {
                'id': 1,
                'username': 'admin',
                'email': 'admin@example.com',
                'real_name': '系统管理员'
            }
        })
    
    @app.route('/api/auth/permissions', methods=['GET'])
    def permissions():
        return jsonify({
            'status': 'success',
            'code': 200,
            'data': {
                'permissions': ['admin:all', 'system:manage'],
                'roles': [{'code': 'admin', 'name': '管理员'}]
            }
        })
    
    # 全局错误处理
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            'status': 'error',
            'code': 404,
            'message': '请求的资源不存在',
            'available_endpoints': [
                '/',
                '/api/health', 
                '/api/auth/login',
                '/api/auth/logout'
            ]
        }), 404
    
    return app

def main():
    """启动服务"""
    print("=" * 70)
    print("🚀 IT运维系统 - 调试版后端服务启动中...")
    print("=" * 70)
    print("📋 服务信息:")
    print(f"   🌐 后端地址: http://localhost:5000")
    print(f"   🔗 前端地址: http://localhost:3001") 
    print(f"   🔑 默认账户: admin / admin123")
    print(f"   📡 CORS已启用，支持跨域访问")
    print(f"   🛡️  API频率限制: 5次/分钟")
    print("=" * 70)
    print("🔍 测试步骤:")
    print("   1. 访问 http://localhost:5000 检查后端状态")
    print("   2. 访问 http://localhost:3001 打开前端界面")
    print("   3. 使用 admin/admin123 进行登录测试")
    print("=" * 70)
    
    try:
        app = create_debug_app()
        # 启动服务 - 绑定所有地址
        app.run(
            host='0.0.0.0',  # 监听所有网络接口
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()