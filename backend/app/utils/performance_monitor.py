"""
系统性能监控模块
监控系统资源使用情况、响应时间、错误率等关键指标
"""
import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
import statistics
import json
import sqlite3
import os

from flask import current_app


class MetricType:
    """指标类型"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    REQUEST_COUNT = "request_count"
    ACTIVE_CONNECTIONS = "active_connections"


class PerformanceMetric:
    """性能指标"""
    
    def __init__(self, metric_type: str, value: float, timestamp: datetime = None):
        self.metric_type = metric_type
        self.value = value
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'metric_type': self.metric_type,
            'value': self.value,
            'timestamp': self.timestamp.isoformat()
        }


class ResourceMonitor:
    """系统资源监控器"""
    
    def __init__(self):
        self.cpu_percent = 0
        self.memory_percent = 0
        self.disk_percent = 0
        self.network_io = {'sent': 0, 'recv': 0}
        self.last_network_io = None
    
    def get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        self.cpu_percent = psutil.cpu_percent(interval=1)
        return self.cpu_percent
    
    def get_memory_usage(self) -> Tuple[float, Dict]:
        """获取内存使用情况"""
        memory = psutil.virtual_memory()
        self.memory_percent = memory.percent
        
        return self.memory_percent, {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free
        }
    
    def get_disk_usage(self, path: str = '/') -> Tuple[float, Dict]:
        """获取磁盘使用情况"""
        try:
            disk = psutil.disk_usage(path)
            self.disk_percent = (disk.used / disk.total) * 100
            
            return self.disk_percent, {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free
            }
        except Exception:
            # Windows系统使用C:盘
            try:
                disk = psutil.disk_usage('C:')
                self.disk_percent = (disk.used / disk.total) * 100
                return self.disk_percent, {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free
                }
            except Exception:
                return 0, {'total': 0, 'used': 0, 'free': 0}
    
    def get_network_io(self) -> Dict:
        """获取网络IO统计"""
        try:
            net_io = psutil.net_io_counters()
            current_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
            
            if self.last_network_io:
                # 计算差值
                self.network_io = {
                    'sent': current_io['bytes_sent'] - self.last_network_io['bytes_sent'],
                    'recv': current_io['bytes_recv'] - self.last_network_io['bytes_recv']
                }
            
            self.last_network_io = current_io
            return self.network_io
        except Exception:
            return {'sent': 0, 'recv': 0}
    
    def get_process_info(self) -> Dict:
        """获取当前进程信息"""
        try:
            process = psutil.Process()
            return {
                'pid': process.pid,
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_info': process.memory_info()._asdict(),
                'num_threads': process.num_threads(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat()
            }
        except Exception:
            return {}


class RequestMetrics:
    """请求指标统计"""
    
    def __init__(self, max_samples: int = 10000):
        self.max_samples = max_samples
        self.response_times = deque(maxlen=max_samples)
        self.request_counts = deque(maxlen=max_samples)
        self.error_counts = deque(maxlen=max_samples)
        self.status_codes = deque(maxlen=max_samples)
        self.endpoints = deque(maxlen=max_samples)
        self.lock = threading.Lock()
    
    def record_request(self, response_time: float, status_code: int, endpoint: str):
        """记录请求指标"""
        with self.lock:
            timestamp = datetime.now()
            
            self.response_times.append((timestamp, response_time))
            self.request_counts.append((timestamp, 1))
            self.error_counts.append((timestamp, 1 if status_code >= 400 else 0))
            self.status_codes.append((timestamp, status_code))
            self.endpoints.append((timestamp, endpoint))
    
    def get_avg_response_time(self, minutes: int = 5) -> float:
        """获取平均响应时间"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            recent_times = [rt for ts, rt in self.response_times if ts >= cutoff]
            return statistics.mean(recent_times) if recent_times else 0
    
    def get_request_rate(self, minutes: int = 5) -> float:
        """获取请求速率（每分钟）"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            recent_requests = [1 for ts, _ in self.request_counts if ts >= cutoff]
            return (len(recent_requests) / minutes) if recent_requests else 0
    
    def get_error_rate(self, minutes: int = 5) -> float:
        """获取错误率"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            recent_errors = [err for ts, err in self.error_counts if ts >= cutoff]
            total_requests = len(recent_errors)
            error_requests = sum(recent_errors)
            return (error_requests / total_requests * 100) if total_requests > 0 else 0
    
    def get_status_distribution(self, minutes: int = 5) -> Dict[int, int]:
        """获取状态码分布"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            recent_codes = [code for ts, code in self.status_codes if ts >= cutoff]
            distribution = {}
            for code in recent_codes:
                distribution[code] = distribution.get(code, 0) + 1
            return distribution
    
    def get_endpoint_stats(self, minutes: int = 5) -> Dict[str, int]:
        """获取端点访问统计"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            recent_endpoints = [ep for ts, ep in self.endpoints if ts >= cutoff]
            stats = {}
            for endpoint in recent_endpoints:
                stats[endpoint] = stats.get(endpoint, 0) + 1
            return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))


class AlertRule:
    """告警规则"""
    
    def __init__(self, metric_type: str, threshold: float, comparison: str = 'gt'):
        self.metric_type = metric_type
        self.threshold = threshold
        self.comparison = comparison  # gt, lt, eq
        self.triggered = False
        self.last_trigger_time = None
    
    def check(self, value: float) -> bool:
        """检查是否触发告警"""
        triggered = False
        
        if self.comparison == 'gt' and value > self.threshold:
            triggered = True
        elif self.comparison == 'lt' and value < self.threshold:
            triggered = True
        elif self.comparison == 'eq' and value == self.threshold:
            triggered = True
        
        if triggered:
            self.triggered = True
            self.last_trigger_time = datetime.now()
        
        return triggered


class PerformanceMonitor:
    """性能监控主类"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(os.getcwd(), 'performance_metrics.db')
        self.resource_monitor = ResourceMonitor()
        self.request_metrics = RequestMetrics()
        self.alert_rules: List[AlertRule] = []
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history: List[PerformanceMetric] = []
        self._init_database()
        self._setup_default_alerts()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_type TEXT NOT NULL,
                        threshold_value REAL NOT NULL,
                        actual_value REAL NOT NULL,
                        triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        resolved_at DATETIME
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"初始化数据库失败: {e}")
    
    def _setup_default_alerts(self):
        """设置默认告警规则"""
        self.alert_rules = [
            AlertRule(MetricType.CPU_USAGE, 80.0, 'gt'),
            AlertRule(MetricType.MEMORY_USAGE, 85.0, 'gt'),
            AlertRule(MetricType.DISK_USAGE, 90.0, 'gt'),
            AlertRule(MetricType.RESPONSE_TIME, 2000.0, 'gt'),  # 2秒
            AlertRule(MetricType.ERROR_RATE, 10.0, 'gt'),  # 10%
        ]
    
    def start_monitoring(self, interval: int = 60):
        """启动性能监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self.monitoring:
            try:
                # 收集系统指标
                cpu_usage = self.resource_monitor.get_cpu_usage()
                memory_usage, _ = self.resource_monitor.get_memory_usage()
                disk_usage, _ = self.resource_monitor.get_disk_usage()
                
                # 收集应用指标
                avg_response_time = self.request_metrics.get_avg_response_time()
                error_rate = self.request_metrics.get_error_rate()
                request_rate = self.request_metrics.get_request_rate()
                
                # 创建指标对象
                metrics = [
                    PerformanceMetric(MetricType.CPU_USAGE, cpu_usage),
                    PerformanceMetric(MetricType.MEMORY_USAGE, memory_usage),
                    PerformanceMetric(MetricType.DISK_USAGE, disk_usage),
                    PerformanceMetric(MetricType.RESPONSE_TIME, avg_response_time),
                    PerformanceMetric(MetricType.ERROR_RATE, error_rate),
                    PerformanceMetric(MetricType.REQUEST_COUNT, request_rate),
                ]
                
                # 存储指标
                self._store_metrics(metrics)
                
                # 检查告警
                self._check_alerts(metrics)
                
                # 添加到历史记录
                self.metrics_history.extend(metrics)
                
                # 保持历史记录大小
                if len(self.metrics_history) > 10000:
                    self.metrics_history = self.metrics_history[-5000:]
                
            except Exception as e:
                print(f"监控循环错误: {e}")
            
            time.sleep(interval)
    
    def _store_metrics(self, metrics: List[PerformanceMetric]):
        """存储指标到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for metric in metrics:
                    conn.execute(
                        'INSERT INTO performance_metrics (metric_type, value, timestamp) VALUES (?, ?, ?)',
                        (metric.metric_type, metric.value, metric.timestamp)
                    )
                conn.commit()
        except Exception as e:
            print(f"存储指标失败: {e}")
    
    def _check_alerts(self, metrics: List[PerformanceMetric]):
        """检查告警规则"""
        for metric in metrics:
            for rule in self.alert_rules:
                if rule.metric_type == metric.metric_type:
                    if rule.check(metric.value):
                        self._trigger_alert(rule, metric.value)
    
    def _trigger_alert(self, rule: AlertRule, actual_value: float):
        """触发告警"""
        try:
            # 记录到数据库
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO alerts (metric_type, threshold_value, actual_value) VALUES (?, ?, ?)',
                    (rule.metric_type, rule.threshold, actual_value)
                )
                conn.commit()
            
            # 记录到日志
            if current_app:
                current_app.logger.warning(
                    f"性能告警: {rule.metric_type} = {actual_value}, 阈值 = {rule.threshold}"
                )
            else:
                print(f"性能告警: {rule.metric_type} = {actual_value}, 阈值 = {rule.threshold}")
                
        except Exception as e:
            print(f"触发告警失败: {e}")
    
    def get_current_metrics(self) -> Dict:
        """获取当前指标"""
        cpu_usage = self.resource_monitor.get_cpu_usage()
        memory_usage, memory_info = self.resource_monitor.get_memory_usage()
        disk_usage, disk_info = self.resource_monitor.get_disk_usage()
        network_io = self.resource_monitor.get_network_io()
        process_info = self.resource_monitor.get_process_info()
        
        return {
            'system': {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'memory_info': memory_info,
                'disk_usage': disk_usage,
                'disk_info': disk_info,
                'network_io': network_io
            },
            'process': process_info,
            'application': {
                'avg_response_time': self.request_metrics.get_avg_response_time(),
                'request_rate': self.request_metrics.get_request_rate(),
                'error_rate': self.request_metrics.get_error_rate(),
                'status_distribution': self.request_metrics.get_status_distribution(),
                'endpoint_stats': self.request_metrics.get_endpoint_stats()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_historical_metrics(self, metric_type: str, hours: int = 24) -> List[Dict]:
        """获取历史指标"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT value, timestamp FROM performance_metrics WHERE metric_type = ? AND timestamp >= ? ORDER BY timestamp',
                    (metric_type, cutoff)
                )
                return [{'value': row[0], 'timestamp': row[1]} for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取历史指标失败: {e}")
            return []
    
    def get_alerts(self, hours: int = 24) -> List[Dict]:
        """获取告警记录"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT metric_type, threshold_value, actual_value, triggered_at FROM alerts WHERE triggered_at >= ? ORDER BY triggered_at DESC',
                    (cutoff,)
                )
                return [
                    {
                        'metric_type': row[0],
                        'threshold_value': row[1],
                        'actual_value': row[2],
                        'triggered_at': row[3]
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print(f"获取告警记录失败: {e}")
            return []
    
    def record_request(self, response_time: float, status_code: int, endpoint: str):
        """记录请求指标"""
        self.request_metrics.record_request(response_time, status_code, endpoint)


# 创建全局性能监控器实例
performance_monitor = PerformanceMonitor()