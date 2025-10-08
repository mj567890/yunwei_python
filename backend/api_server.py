#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT运维系统完整API启动脚本
"""

import os
import sys
from flask import Flask, request, Response
from flask_cors import CORS

# 设置环境
os.environ['FLASK_ENV'] = 'development'

def create_simple_app():
    """创建简化的Flask应用"""
    app = Flask(__name__)
    
    # CORS配置
    CORS(app, 
         origins=["http://localhost:3000", "http://127.0.0.1:3000"],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    
    # 全局OPTIONS请求处理
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = Response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # 基础路由
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'IT运维系统运行正常'}
    
    @app.route('/api/health')
    def api_health():
        return {'success': True, 'data': {'status': 'healthy'}, 'message': 'API服务正常'}
    
    # 资产管理模拟API
    @app.route('/api/assets')
    def get_assets():
        return {
            'success': True,
            'data': {
                'list': [
                    {
                        'id': 1,
                        'asset_code': 'AS001',
                        'name': '交换机-01',
                        'brand': 'Cisco',
                        'model': 'WS-C2960',
                        'category': '交换机',
                        'status': '在用',
                        'user_name': '张三',
                        'ip_address': '192.168.1.10',
                        'warranty_status': '保修中',
                        'warranty_days_left': 365
                    },
                    {
                        'id': 2,
                        'asset_code': 'AS002',
                        'name': '路由器-01',
                        'brand': 'Huawei',
                        'model': 'AR2220',
                        'category': '路由器',
                        'status': '在用',
                        'user_name': '李四',
                        'ip_address': '192.168.1.1',
                        'warranty_status': '已过保',
                        'warranty_days_left': 0
                    }
                ],
                'total': 2,
                'page': 1,
                'page_size': 20,
                'total_pages': 1
            },
            'message': '获取资产列表成功'
        }
    
    @app.route('/api/assets/categories')  
    def get_categories():
        return {
            'success': True,
            'data': [
                {'id': 1, 'name': '交换机', 'code': 'SWITCH'},
                {'id': 2, 'name': '路由器', 'code': 'ROUTER'},
                {'id': 3, 'name': '防火墙', 'code': 'FIREWALL'},
                {'id': 4, 'name': '服务器', 'code': 'SERVER'},
                {'id': 5, 'name': '工作站', 'code': 'WORKSTATION'}
            ],
            'message': '获取类别列表成功'
        }
    
    @app.route('/api/statistics/overview')
    def get_statistics():
        return {
            'success': True,
            'data': {
                'total_assets': 2,
                'network_devices': 2,
                'online_devices': 1,
                'offline_devices': 1
            },
            'message': '获取统计信息成功'
        }
        
    @app.route('/api/locations/buildings')
    def get_buildings():
        return {
            'success': True,
            'data': [
                {'id': 1, 'name': 'A栋', 'description': '主办公楼'},
                {'id': 2, 'name': 'B栋', 'description': '数据中心'}
            ],
            'message': '获取楼宇列表成功'
        }
    
    return app

def main():
    print("=" * 60)
    print("IT运维系统完整API服务启动")
    print("=" * 60)
    
    try:
        app = create_simple_app()
        
        print("✓ Flask应用创建成功")
        print("✓ CORS配置完成")
        print("✓ 模拟API接口已注册")
        print("✓ 所有OPTIONS请求已处理")
        
        print(f"\n启动地址: http://localhost:5000")
        print(f"前端地址: http://localhost:3000") 
        print("按 Ctrl+C 停止服务")
        print("=" * 60)
        
        # 启动服务器
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # 避免重启问题
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        return False

if __name__ == '__main__':
    main()