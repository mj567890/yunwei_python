"""
用户认证相关测试
"""
import pytest
import json
from app.models import User, Role


class TestAuth:
    """认证测试类"""
    
    def test_user_registration(self, client, db_session):
        """测试用户注册"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'password123',
            'role': '普通用户'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == '用户注册成功'
        
        # 验证用户已创建
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@test.com'
    
    def test_user_login_success(self, client, db_session):
        """测试用户登录成功"""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert data['user']['username'] == 'admin'
    
    def test_user_login_invalid_credentials(self, client, db_session):
        """测试无效凭据登录"""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert '用户名或密码错误' in data['message']
    
    def test_user_login_nonexistent_user(self, client, db_session):
        """测试不存在的用户登录"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password'
        })
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client, db_session, auth_headers):
        """测试获取当前用户信息"""
        headers = auth_headers()
        response = client.get('/api/auth/me', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'admin'
        assert data['role']['name'] == '管理员'
    
    def test_get_current_user_without_token(self, client, db_session):
        """测试无Token获取用户信息"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client, db_session):
        """测试无效Token获取用户信息"""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/auth/me', headers=headers)
        
        assert response.status_code == 401
    
    def test_update_user_profile(self, client, db_session, auth_headers):
        """测试更新用户资料"""
        headers = auth_headers()
        response = client.put('/api/auth/profile', 
                            headers=headers,
                            json={
                                'email': 'updated@test.com',
                                'phone': '13800138000'
                            })
        
        assert response.status_code == 200
        
        # 验证更新成功
        user = User.query.filter_by(username='admin').first()
        assert user.email == 'updated@test.com'
        assert user.phone == '13800138000'
    
    def test_change_password(self, client, db_session, auth_headers):
        """测试修改密码"""
        headers = auth_headers()
        response = client.put('/api/auth/password',
                            headers=headers,
                            json={
                                'old_password': 'admin123',
                                'new_password': 'newpassword123'
                            })
        
        assert response.status_code == 200
        
        # 验证新密码可以登录
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'newpassword123'
        })
        assert response.status_code == 200
    
    def test_change_password_wrong_old_password(self, client, db_session, auth_headers):
        """测试错误的旧密码修改"""
        headers = auth_headers()
        response = client.put('/api/auth/password',
                            headers=headers,
                            json={
                                'old_password': 'wrongpassword',
                                'new_password': 'newpassword123'
                            })
        
        assert response.status_code == 400
    
    def test_logout(self, client, db_session, auth_headers):
        """测试用户登出"""
        headers = auth_headers()
        response = client.post('/api/auth/logout', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == '退出登录成功'


class TestUserManagement:
    """用户管理测试类"""
    
    def test_get_users_list(self, client, db_session, auth_headers):
        """测试获取用户列表"""
        headers = auth_headers()
        response = client.get('/api/users', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'total' in data
        assert len(data['data']) >= 2  # 至少有admin和user两个用户
    
    def test_get_user_by_id(self, client, db_session, auth_headers):
        """测试根据ID获取用户"""
        headers = auth_headers()
        user = User.query.filter_by(username='admin').first()
        
        response = client.get(f'/api/users/{user.id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'admin'
    
    def test_create_user(self, client, db_session, auth_headers):
        """测试创建用户"""
        headers = auth_headers()
        response = client.post('/api/users',
                             headers=headers,
                             json={
                                 'username': 'testuser',
                                 'email': 'testuser@test.com',
                                 'password': 'password123',
                                 'role': '普通用户',
                                 'phone': '13800138001'
                             })
        
        assert response.status_code == 201
        
        # 验证用户已创建
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'testuser@test.com'
    
    def test_update_user(self, client, db_session, auth_headers):
        """测试更新用户"""
        headers = auth_headers()
        user = User.query.filter_by(username='user').first()
        
        response = client.put(f'/api/users/{user.id}',
                            headers=headers,
                            json={
                                'email': 'updated_user@test.com',
                                'phone': '13800138002'
                            })
        
        assert response.status_code == 200
        
        # 验证更新成功
        updated_user = User.query.get(user.id)
        assert updated_user.email == 'updated_user@test.com'
        assert updated_user.phone == '13800138002'
    
    def test_delete_user(self, client, db_session, auth_headers):
        """测试删除用户"""
        headers = auth_headers()
        
        # 创建一个测试用户
        test_user = User(
            username='todelete',
            email='delete@test.com'
        )
        test_user.set_password('password')
        db_session.add(test_user)
        db_session.commit()
        
        response = client.delete(f'/api/users/{test_user.id}', headers=headers)
        
        assert response.status_code == 200
        
        # 验证用户已删除
        deleted_user = User.query.get(test_user.id)
        assert deleted_user is None
    
    def test_non_admin_cannot_manage_users(self, client, db_session, auth_headers):
        """测试非管理员无法管理用户"""
        headers = auth_headers('user', 'user123')
        
        response = client.get('/api/users', headers=headers)
        assert response.status_code == 403
        
        response = client.post('/api/users',
                             headers=headers,
                             json={
                                 'username': 'newuser',
                                 'email': 'new@test.com',
                                 'password': 'password'
                             })
        assert response.status_code == 403