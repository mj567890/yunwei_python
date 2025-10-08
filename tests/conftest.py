"""
后端单元测试配置
"""
import os
import sys
import pytest
import tempfile
from app import create_app, db
from app.models import User, Role, Asset, MaintenanceRecord
from app.config import TestConfig

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='session')
def app():
    """创建测试应用实例"""
    app = create_app(TestConfig)
    
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """创建数据库会话"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建基础数据
        admin_role = Role(name='管理员', description='系统管理员')
        user_role = Role(name='普通用户', description='普通用户')
        
        admin_user = User(
            username='admin',
            email='admin@test.com',
            role=admin_role
        )
        admin_user.set_password('admin123')
        
        normal_user = User(
            username='user',
            email='user@test.com',
            role=user_role
        )
        normal_user.set_password('user123')
        
        db.session.add_all([admin_role, user_role, admin_user, normal_user])
        db.session.commit()
        
        yield db.session
        
        # 清理数据
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth_headers(client):
    """获取认证头信息"""
    def _get_auth_headers(username='admin', password='admin123'):
        response = client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
        data = response.get_json()
        token = data.get('token')
        return {'Authorization': f'Bearer {token}'}
    
    return _get_auth_headers


@pytest.fixture
def sample_asset(db_session):
    """创建示例资产"""
    asset = Asset(
        name='测试服务器',
        asset_code='SV001',
        category='服务器',
        brand='Dell',
        model='PowerEdge R740',
        serial_number='SN123456',
        status='正常',
        location='机房A-01',
        purchase_date='2023-01-01',
        warranty_date='2026-01-01',
        price=50000.00,
        description='测试用服务器'
    )
    db_session.add(asset)
    db_session.commit()
    return asset


@pytest.fixture
def sample_maintenance(db_session, sample_asset):
    """创建示例运维记录"""
    maintenance = MaintenanceRecord(
        asset_id=sample_asset.id,
        title='系统维护',
        description='定期系统维护',
        maintenance_type='preventive',
        status='pending',
        scheduled_date='2024-01-15',
        technician='张三',
        estimated_hours=2.0
    )
    db_session.add(maintenance)
    db_session.commit()
    return maintenance


def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "unit: 单元测试标记"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试标记"
    )
    config.addinivalue_line(
        "markers", "performance: 性能测试标记"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试标记"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项配置"""
    for item in items:
        # 为所有测试添加单元测试标记
        if "test_" in item.nodeid:
            item.add_marker(pytest.mark.unit)
            
        # 为集成测试添加标记
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            
        # 为性能测试添加标记
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)