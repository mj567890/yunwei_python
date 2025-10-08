"""
性能测试
"""
import pytest
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.models import Asset, User


@pytest.mark.performance
class TestPerformance:
    """性能测试类"""
    
    def test_database_query_performance(self, client, db_session, auth_headers):
        """测试数据库查询性能"""
        headers = auth_headers()
        
        # 创建大量测试数据
        assets = []
        for i in range(1000):
            asset = Asset(
                name=f'性能测试资产{i}',
                asset_code=f'PERF{i:04d}',
                category='服务器',
                brand='测试品牌',
                model='测试型号',
                serial_number=f'SN{i:06d}',
                status='正常',
                location=f'机房{i % 10}',
                price=50000.00
            )
            assets.append(asset)
        
        db_session.add_all(assets)
        db_session.commit()
        
        # 测试查询性能
        start_time = time.time()
        response = client.get('/api/assets?page=1&page_size=100', headers=headers)
        query_time = time.time() - start_time
        
        assert response.status_code == 200
        assert query_time < 1.0  # 查询时间应小于1秒
        
        data = response.get_json()
        assert data['total'] >= 1000
        assert len(data['data']) == 100
    
    def test_api_response_time(self, client, db_session, auth_headers, sample_asset):
        """测试API响应时间"""
        headers = auth_headers()
        
        # 测试各个端点的响应时间
        endpoints = [
            '/api/assets',
            '/api/users',
            '/api/maintenance',
            '/api/faults',
            '/api/network/devices'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint, headers=headers)
            response_time = time.time() - start_time
            
            assert response.status_code in [200, 404]  # 404可能因为没有数据
            assert response_time < 0.5  # 响应时间应小于500ms
    
    def test_concurrent_users(self, client, db_session, auth_headers):
        """测试并发用户访问"""
        headers = auth_headers()
        
        def make_request():
            """单个请求函数"""
            response = client.get('/api/assets', headers=headers)
            return response.status_code == 200
        
        # 模拟50个并发用户
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        # 检查成功率
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.95  # 成功率应大于95%
    
    def test_memory_usage(self, client, db_session, auth_headers):
        """测试内存使用情况"""
        import psutil
        import os
        
        headers = auth_headers()
        process = psutil.Process(os.getpid())
        
        # 记录初始内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行大量请求
        for i in range(100):
            response = client.get('/api/assets', headers=headers)
            assert response.status_code == 200
        
        # 记录最终内存使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 内存增长应该控制在合理范围内
        memory_growth = final_memory - initial_memory
        assert memory_growth < 50  # 内存增长应小于50MB
    
    def test_large_data_export(self, client, db_session, auth_headers):
        """测试大数据量导出性能"""
        headers = auth_headers()
        
        # 创建大量测试数据
        assets = []
        for i in range(5000):
            asset = Asset(
                name=f'导出测试资产{i}',
                asset_code=f'EXP{i:05d}',
                category='服务器',
                brand='测试品牌',
                model='测试型号',
                serial_number=f'SN{i:07d}',
                status='正常',
                location=f'机房{i % 20}',
                price=50000.00
            )
            assets.append(asset)
        
        db_session.add_all(assets)
        db_session.commit()
        
        # 测试导出性能
        start_time = time.time()
        response = client.get('/api/assets/export', headers=headers)
        export_time = time.time() - start_time
        
        assert response.status_code == 200
        assert export_time < 10.0  # 导出时间应小于10秒
        assert len(response.data) > 0  # 确保有数据导出
    
    def test_pagination_performance(self, client, db_session, auth_headers):
        """测试分页性能"""
        headers = auth_headers()
        
        # 创建测试数据
        assets = []
        for i in range(2000):
            asset = Asset(
                name=f'分页测试资产{i}',
                asset_code=f'PAGE{i:05d}',
                category='服务器',
                brand='测试品牌',
                model='测试型号',
                serial_number=f'SN{i:07d}',
                status='正常',
                location=f'机房{i % 30}',
                price=50000.00
            )
            assets.append(asset)
        
        db_session.add_all(assets)
        db_session.commit()
        
        # 测试不同页码的查询性能
        page_times = []
        for page in [1, 10, 20]:
            start_time = time.time()
            response = client.get(f'/api/assets?page={page}&page_size=50', headers=headers)
            page_time = time.time() - start_time
            page_times.append(page_time)
            
            assert response.status_code == 200
            assert page_time < 1.0  # 每页查询时间应小于1秒
        
        # 各页查询时间应该相近（性能稳定）
        max_time = max(page_times)
        min_time = min(page_times)
        assert (max_time - min_time) < 0.5  # 时间差应小于500ms
    
    def test_search_performance(self, client, db_session, auth_headers):
        """测试搜索性能"""
        headers = auth_headers()
        
        # 创建测试数据
        assets = []
        for i in range(3000):
            asset = Asset(
                name=f'搜索测试资产{i}',
                asset_code=f'SEARCH{i:05d}',
                category='服务器' if i % 2 == 0 else '网络设备',
                brand='Dell' if i % 3 == 0 else 'HP',
                model=f'型号{i % 10}',
                serial_number=f'SN{i:07d}',
                status='正常',
                location=f'机房{i % 40}',
                price=50000.00,
                description=f'这是第{i}个测试资产的描述信息'
            )
            assets.append(asset)
        
        db_session.add_all(assets)
        db_session.commit()
        
        # 测试不同类型的搜索性能
        search_tests = [
            ('search=测试', '模糊搜索'),
            ('category=服务器', '类别筛选'),
            ('brand=Dell', '品牌筛选'),
            ('status=正常', '状态筛选'),
            ('search=资产&category=服务器', '组合搜索')
        ]
        
        for search_param, test_name in search_tests:
            start_time = time.time()
            response = client.get(f'/api/assets?{search_param}', headers=headers)
            search_time = time.time() - start_time
            
            assert response.status_code == 200
            assert search_time < 2.0, f'{test_name}性能测试失败，耗时{search_time}秒'
            
            data = response.get_json()
            assert 'data' in data
            assert 'total' in data
    
    @pytest.mark.slow
    def test_stress_test(self, client, db_session, auth_headers):
        """压力测试"""
        headers = auth_headers()
        
        def stress_worker():
            """压力测试工作函数"""
            success_count = 0
            total_count = 10
            
            for i in range(total_count):
                try:
                    # 随机选择不同的API端点
                    endpoints = [
                        '/api/assets',
                        '/api/users',
                        '/api/maintenance',
                        '/api/faults'
                    ]
                    
                    for endpoint in endpoints:
                        response = client.get(endpoint, headers=headers)
                        if response.status_code in [200, 404]:
                            success_count += 1
                        
                        time.sleep(0.1)  # 模拟用户思考时间
                        
                except Exception:
                    pass
            
            return success_count
        
        # 启动多个并发线程进行压力测试
        thread_count = 20
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(stress_worker) for _ in range(thread_count)]
            results = [future.result() for future in as_completed(futures)]
        
        # 计算总体成功率
        total_success = sum(results)
        total_requests = thread_count * 10 * 4  # 每个线程10次循环，每次4个端点
        success_rate = total_success / total_requests
        
        assert success_rate >= 0.9, f'压力测试失败，成功率{success_rate:.2%}'
    
    def test_database_connection_pool(self, client, db_session, auth_headers):
        """测试数据库连接池性能"""
        headers = auth_headers()
        
        def db_worker():
            """数据库操作工作函数"""
            try:
                response = client.get('/api/assets', headers=headers)
                return response.status_code == 200
            except Exception:
                return False
        
        # 同时创建大量数据库连接
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(db_worker) for _ in range(100)]
            results = [future.result() for future in as_completed(futures)]
        
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.95, f'数据库连接池测试失败，成功率{success_rate:.2%}'