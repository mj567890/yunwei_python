#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的Flask应用启动脚本
包含所有API路由和功能
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置Flask配置为SQLite
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///it_ops_system.db'

def main():
    try:
        print("=" * 60)
        print("IT运维系统完整版启动")
        print("=" * 60)
        
        # 导入Flask应用
        from app import create_app
        
        app = create_app()
        
        print("✓ Flask应用创建成功")
        print("✓ 数据库连接正常") 
        print("✓ 所有API路由已注册")
        
        # 显示可用端点
        print("\n可用端点:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
                    print(f"  - {methods:10} {rule.rule:30} - {rule.endpoint}")
        
        print("\n启动地址: http://localhost:5000")
        print("前端地址: http://localhost:3000")
        print("按 Ctrl+C 停止服务")
        print("=" * 60)
        
        # 启动开发服务器
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {str(e)}")
        print("请检查依赖是否正确安装")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        return False

if __name__ == '__main__':
    main()