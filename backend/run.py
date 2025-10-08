"""
IT运维综合管理系统 Flask应用程序入口
"""
from app import create_app
from config.config import DevelopmentConfig

app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)