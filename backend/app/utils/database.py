"""
数据库安全连接和优化工具
"""
import time
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DisconnectionError, OperationalError
from sqlalchemy.pool import QueuePool
from flask import current_app
from app import db


class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self):
        self._connection_pool_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'last_check_time': time.time()
        }
    
    @staticmethod
    def create_secure_engine(database_uri: str, **kwargs) -> Engine:
        """
        创建安全的数据库引擎
        
        Args:
            database_uri: 数据库连接URI
            **kwargs: 额外的引擎参数
            
        Returns:
            配置好的数据库引擎
        """
        # 默认安全配置
        default_config = {
            'poolclass': QueuePool,
            'pool_size': 10,                    # 连接池大小
            'max_overflow': 20,                 # 超出连接池大小的连接数
            'pool_timeout': 30,                 # 获取连接超时时间
            'pool_recycle': 3600,              # 连接回收时间（1小时）
            'pool_pre_ping': True,             # 连接前ping检查
            'pool_reset_on_return': 'commit',   # 连接返回时重置
            'echo': False,                      # 生产环境关闭SQL日志
            'isolation_level': 'READ_COMMITTED', # 事务隔离级别
            'connect_args': {
                'charset': 'utf8mb4',
                'connect_timeout': 10,          # 连接超时
                'read_timeout': 30,             # 读取超时
                'write_timeout': 30,            # 写入超时
                'autocommit': False,            # 禁用自动提交
                'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO',
            }
        }
        
        # 合并用户配置
        config = {**default_config, **kwargs}
        
        # 创建引擎
        engine = create_engine(database_uri, **config)
        
        # 注册事件监听器
        DatabaseManager._register_event_listeners(engine)
        
        return engine
    
    @staticmethod
    def _register_event_listeners(engine: Engine):
        """注册数据库事件监听器"""
        
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """SQLite特殊配置（如果使用SQLite）"""
            if 'sqlite' in str(engine.url):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.close()
        
        @event.listens_for(engine, "connect")
        def set_mysql_settings(dbapi_connection, connection_record):
            """MySQL特殊配置"""
            if 'mysql' in str(engine.url):
                cursor = dbapi_connection.cursor()
                # 设置会话级别的SQL模式
                cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
                # 设置字符集
                cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci")
                # 设置时区
                cursor.execute("SET time_zone='+00:00'")
                cursor.close()
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """连接检出时的处理"""
            connection_record.info['checkout_time'] = time.time()
        
        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """连接检入时的处理"""
            if 'checkout_time' in connection_record.info:
                checkout_time = connection_record.info['checkout_time']
                duration = time.time() - checkout_time
                if duration > 60:  # 连接使用超过1分钟记录警告
                    current_app.logger.warning(f"数据库连接使用时间过长: {duration:.2f}秒")
    
    @staticmethod
    def health_check() -> Dict[str, Any]:
        """
        数据库健康检查
        
        Returns:
            健康检查结果
        """
        try:
            start_time = time.time()
            
            # 执行简单查询测试连接
            result = db.session.execute(text('SELECT 1 as health_check'))
            row = result.fetchone()
            
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            if row and row[0] == 1:
                # 获取连接池状态
                pool = db.engine.pool
                pool_status = {
                    'pool_size': pool.size(),
                    'checked_in': pool.checkedin(),
                    'checked_out': pool.checkedout(),
                    'overflow': pool.overflow(),
                    'invalid': pool.invalid()
                }
                
                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time, 2),
                    'pool_status': pool_status,
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': '查询测试失败',
                    'timestamp': time.time()
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }
    
    @staticmethod
    @contextmanager
    def safe_transaction():
        """
        安全事务上下文管理器
        
        使用方法:
        with DatabaseManager.safe_transaction():
            # 数据库操作
            pass
        """
        try:
            yield db.session
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"事务回滚: {str(e)}")
            raise e
    
    @staticmethod
    def execute_with_retry(query, params=None, max_retries=3, retry_delay=0.5):
        """
        带重试机制的数据库查询执行
        
        Args:
            query: SQL查询语句
            params: 查询参数
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            查询结果
        """
        for attempt in range(max_retries + 1):
            try:
                if params:
                    result = db.session.execute(text(query), params)
                else:
                    result = db.session.execute(text(query))
                return result
                
            except (DisconnectionError, OperationalError) as e:
                if attempt < max_retries:
                    current_app.logger.warning(f"数据库查询失败，重试 {attempt + 1}/{max_retries}: {str(e)}")
                    time.sleep(retry_delay * (attempt + 1))  # 递增延迟
                    continue
                else:
                    current_app.logger.error(f"数据库查询最终失败: {str(e)}")
                    raise e
            except Exception as e:
                current_app.logger.error(f"数据库查询异常: {str(e)}")
                raise e
    
    @staticmethod
    def get_connection_stats() -> Dict[str, Any]:
        """
        获取数据库连接统计信息
        
        Returns:
            连接统计信息
        """
        try:
            pool = db.engine.pool
            return {
                'pool_size': pool.size(),
                'checked_in_connections': pool.checkedin(),
                'checked_out_connections': pool.checkedout(),
                'overflow_connections': pool.overflow(),
                'invalid_connections': pool.invalid(),
                'total_connections': pool.size() + pool.overflow(),
                'timestamp': time.time()
            }
        except Exception as e:
            current_app.logger.error(f"获取连接统计失败: {str(e)}")
            return {'error': str(e), 'timestamp': time.time()}


def init_database_security(app):
    """
    初始化数据库安全配置
    
    Args:
        app: Flask应用实例
    """
    # 配置数据库连接安全参数
    if not app.config.get('SQLALCHEMY_ENGINE_OPTIONS'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    
    # 更新安全配置
    security_options = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_timeout': 30,
        'pool_size': 10,
        'max_overflow': 20,
    }
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'].update(security_options)
    
    @app.before_first_request
    def setup_database():
        """应用启动时的数据库设置"""
        try:
            # 检查数据库连接
            health_result = DatabaseManager.health_check()
            if health_result['status'] == 'healthy':
                app.logger.info("数据库连接健康检查通过")
            else:
                app.logger.error(f"数据库连接健康检查失败: {health_result}")
        except Exception as e:
            app.logger.error(f"数据库初始化失败: {str(e)}")