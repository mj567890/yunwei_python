"""
资产管理相关测试
"""
import pytest
import json
import io
from app.models import Asset, Location


class TestAssets:
    """资产管理测试类"""
    
    def test_get_assets_list(self, client, db_session, auth_headers, sample_asset):
        """测试获取资产列表"""
        headers = auth_headers()
        response = client.get('/api/assets', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'total' in data
        assert len(data['data']) >= 1
        assert data['data'][0]['name'] == '测试服务器'
    
    def test_get_asset_by_id(self, client, db_session, auth_headers, sample_asset):
        """测试根据ID获取资产"""
        headers = auth_headers()
        response = client.get(f'/api/assets/{sample_asset.id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == '测试服务器'
        assert data['asset_code'] == 'SV001'
        assert data['category'] == '服务器'
    
    def test_create_asset(self, client, db_session, auth_headers):
        """测试创建资产"""
        headers = auth_headers()
        asset_data = {
            'name': '新服务器',
            'asset_code': 'SV002',
            'category': '服务器',
            'brand': 'HP',
            'model': 'ProLiant DL380',
            'serial_number': 'SN789012',
            'status': '正常',
            'location': '机房B-01',
            'purchase_date': '2024-01-01',
            'warranty_date': '2027-01-01',
            'price': 60000.00,
            'description': '新采购服务器'
        }
        
        response = client.post('/api/assets', headers=headers, json=asset_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == '新服务器'
        assert data['asset_code'] == 'SV002'
        
        # 验证资产已创建
        asset = Asset.query.filter_by(asset_code='SV002').first()
        assert asset is not None
        assert asset.name == '新服务器'
    
    def test_create_asset_duplicate_code(self, client, db_session, auth_headers, sample_asset):
        """测试创建重复编码的资产"""
        headers = auth_headers()
        asset_data = {
            'name': '重复编码资产',
            'asset_code': 'SV001',  # 与sample_asset相同
            'category': '服务器',
            'brand': 'HP',
            'model': 'ProLiant DL380',
            'serial_number': 'SN999999',
            'status': '正常',
            'location': '机房C-01',
            'purchase_date': '2024-01-01',
            'price': 50000.00
        }
        
        response = client.post('/api/assets', headers=headers, json=asset_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert '资产编码已存在' in data['message']
    
    def test_update_asset(self, client, db_session, auth_headers, sample_asset):
        """测试更新资产"""
        headers = auth_headers()
        update_data = {
            'name': '更新后的服务器',
            'status': '维修中',
            'location': '机房A-02',
            'price': 55000.00
        }
        
        response = client.put(f'/api/assets/{sample_asset.id}', 
                            headers=headers, 
                            json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == '更新后的服务器'
        assert data['status'] == '维修中'
        
        # 验证数据库中的更新
        updated_asset = Asset.query.get(sample_asset.id)
        assert updated_asset.name == '更新后的服务器'
        assert updated_asset.status == '维修中'
        assert updated_asset.location == '机房A-02'
        assert float(updated_asset.price) == 55000.00
    
    def test_delete_asset(self, client, db_session, auth_headers, sample_asset):
        """测试删除资产"""
        headers = auth_headers()
        asset_id = sample_asset.id
        
        response = client.delete(f'/api/assets/{asset_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == '资产删除成功'
        
        # 验证资产已删除
        deleted_asset = Asset.query.get(asset_id)
        assert deleted_asset is None
    
    def test_search_assets(self, client, db_session, auth_headers, sample_asset):
        """测试搜索资产"""
        headers = auth_headers()
        
        # 按名称搜索
        response = client.get('/api/assets?search=测试', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) >= 1
        assert '测试' in data['data'][0]['name']
        
        # 按类别筛选
        response = client.get('/api/assets?category=服务器', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) >= 1
        assert data['data'][0]['category'] == '服务器'
        
        # 按状态筛选
        response = client.get('/api/assets?status=正常', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) >= 1
        assert data['data'][0]['status'] == '正常'
    
    def test_get_asset_statistics(self, client, db_session, auth_headers, sample_asset):
        """测试获取资产统计信息"""
        headers = auth_headers()
        response = client.get('/api/assets/statistics', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total' in data
        assert 'by_category' in data
        assert 'by_status' in data
        assert 'by_location' in data
        assert data['total'] >= 1
    
    def test_export_assets(self, client, db_session, auth_headers, sample_asset):
        """测试导出资产"""
        headers = auth_headers()
        response = client.get('/api/assets/export', headers=headers)
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert 'attachment' in response.headers['Content-Disposition']
    
    def test_import_assets(self, client, db_session, auth_headers):
        """测试导入资产"""
        headers = auth_headers()
        
        # 创建测试CSV数据
        csv_data = """name,asset_code,category,brand,model,serial_number,status,location,price
测试导入服务器1,SV003,服务器,Dell,R750,SN11111,正常,机房D-01,70000
测试导入服务器2,SV004,服务器,HP,DL360,SN22222,正常,机房D-02,65000"""
        
        data = {
            'file': (io.BytesIO(csv_data.encode('utf-8')), 'assets.csv')
        }
        
        response = client.post('/api/assets/import', 
                             headers=headers,
                             data=data,
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['imported_count'] == 2
        assert result['failed_count'] == 0
        
        # 验证导入的资产
        imported_assets = Asset.query.filter(Asset.asset_code.in_(['SV003', 'SV004'])).all()
        assert len(imported_assets) == 2
    
    def test_generate_qr_code(self, client, db_session, auth_headers, sample_asset):
        """测试生成二维码"""
        headers = auth_headers()
        response = client.get(f'/api/assets/{sample_asset.id}/qrcode', headers=headers)
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'image/png'
        assert len(response.data) > 0  # 确保有图片数据
    
    def test_scan_qr_code(self, client, db_session, auth_headers, sample_asset):
        """测试扫描二维码"""
        headers = auth_headers()
        qr_data = f"asset:{sample_asset.id}"
        
        response = client.post('/api/assets/scan', 
                             headers=headers,
                             json={'qr_data': qr_data})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_asset.id
        assert data['name'] == sample_asset.name
    
    def test_unauthorized_access(self, client, db_session):
        """测试未授权访问"""
        response = client.get('/api/assets')
        assert response.status_code == 401
        
        response = client.post('/api/assets', json={'name': 'test'})
        assert response.status_code == 401


class TestLocations:
    """位置管理测试类"""
    
    def test_get_locations(self, client, db_session, auth_headers):
        """测试获取位置列表"""
        # 创建测试位置
        location = Location(
            name='机房A',
            code='RoomA',
            type='机房',
            description='主机房A'
        )
        db_session.add(location)
        db_session.commit()
        
        headers = auth_headers()
        response = client.get('/api/locations', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]['name'] == '机房A'
    
    def test_create_location(self, client, db_session, auth_headers):
        """测试创建位置"""
        headers = auth_headers()
        location_data = {
            'name': '机房B',
            'code': 'RoomB',
            'type': '机房',
            'description': '备用机房B',
            'address': '北京市朝阳区'
        }
        
        response = client.post('/api/locations', headers=headers, json=location_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == '机房B'
        assert data['code'] == 'RoomB'
        
        # 验证位置已创建
        location = Location.query.filter_by(code='RoomB').first()
        assert location is not None
        assert location.name == '机房B'