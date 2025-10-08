"""
监控API端点
提供系统监控、性能指标、安全审计等信息的API接口
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.utils.response import ApiResponse
from app.utils.auth import role_required, log_operation
from app.utils.performance_monitor import performance_monitor
from app.utils.compliance_checker import compliance_manager
from app.utils.anomaly_detection import anomaly_detector
from app.utils.enhanced_audit import audit_logger
from app.utils.api_signature import require_api_signature

monitor_bp = Blueprint('monitor', __name__)


@monitor_bp.route('/system/metrics', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_system_metrics():
    """获取系统性能指标"""
    try:
        metrics = performance_monitor.get_current_metrics()
        return ApiResponse.success(metrics, "获取系统指标成功")
    except Exception as e:
        return ApiResponse.error(f"获取系统指标失败: {str(e)}")


@monitor_bp.route('/system/metrics/history', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_metrics_history():
    """获取历史性能指标"""
    metric_type = request.args.get('metric_type', 'cpu_usage')
    hours = request.args.get('hours', 24, type=int)
    
    try:
        history = performance_monitor.get_historical_metrics(metric_type, hours)
        return ApiResponse.success({
            'metric_type': metric_type,
            'hours': hours,
            'data': history
        }, "获取历史指标成功")
    except Exception as e:
        return ApiResponse.error(f"获取历史指标失败: {str(e)}")


@monitor_bp.route('/system/alerts', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_system_alerts():
    """获取系统告警"""
    hours = request.args.get('hours', 24, type=int)
    
    try:
        alerts = performance_monitor.get_alerts(hours)
        return ApiResponse.success({
            'hours': hours,
            'alerts': alerts,
            'total': len(alerts)
        }, "获取系统告警成功")
    except Exception as e:
        return ApiResponse.error(f"获取系统告警失败: {str(e)}")


@monitor_bp.route('/security/anomalies', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_security_anomalies():
    """获取安全异常事件"""
    hours = request.args.get('hours', 24, type=int)
    risk_threshold = request.args.get('risk_threshold', 50, type=int)
    
    try:
        anomalies = anomaly_detector.get_anomaly_events(hours=hours, min_risk_score=risk_threshold)
        return ApiResponse.success({
            'hours': hours,
            'risk_threshold': risk_threshold,
            'anomalies': [anomaly.to_dict() for anomaly in anomalies],
            'total': len(anomalies)
        }, "获取安全异常成功")
    except Exception as e:
        return ApiResponse.error(f"获取安全异常失败: {str(e)}")


@monitor_bp.route('/security/blocked-ips', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_blocked_ips():
    """获取被阻止的IP列表"""
    try:
        blocked_ips = anomaly_detector.get_blocked_ips()
        return ApiResponse.success({
            'blocked_ips': blocked_ips,
            'total': len(blocked_ips)
        }, "获取阻止IP列表成功")
    except Exception as e:
        return ApiResponse.error(f"获取阻止IP列表失败: {str(e)}")


@monitor_bp.route('/security/unblock-ip', methods=['POST'])
@jwt_required()
@role_required('admin')
@require_api_signature
@log_operation("解除IP阻止")
def unblock_ip():
    """解除IP阻止"""
    data = request.json or {}
    ip_address = data.get('ip_address')
    
    if not ip_address:
        return ApiResponse.error("IP地址不能为空")
    
    try:
        success = anomaly_detector.unblock_ip(ip_address)
        if success:
            return ApiResponse.success(message=f"IP {ip_address} 已解除阻止")
        else:
            return ApiResponse.error(f"IP {ip_address} 未在阻止列表中")
    except Exception as e:
        return ApiResponse.error(f"解除IP阻止失败: {str(e)}")


@monitor_bp.route('/compliance/check', methods=['POST'])
@jwt_required()
@role_required('admin')
@require_api_signature
@log_operation("执行合规性检查")
def run_compliance_check():
    """执行合规性检查"""
    data = request.json or {}
    
    try:
        # 检查密码策略
        if 'password' in data:
            compliance_manager.check_password_compliance(data['password'])
        
        # 检查加密配置
        if 'encryption' in data:
            enc_config = data['encryption']
            compliance_manager.check_encryption_compliance(
                enc_config.get('algorithm', 'AES'),
                enc_config.get('key_length', 256)
            )
        
        # 检查网络安全
        if 'network' in data:
            net_config = data['network']
            compliance_manager.check_network_compliance(
                net_config.get('hostname', 'localhost'),
                net_config.get('headers', {})
            )
        
        # 生成报告
        report = compliance_manager.generate_compliance_report()
        
        return ApiResponse.success(report, "合规性检查完成")
        
    except Exception as e:
        return ApiResponse.error(f"合规性检查失败: {str(e)}")


@monitor_bp.route('/audit/logs', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_audit_logs():
    """获取审计日志"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 50, type=int), 200)
    event_type = request.args.get('event_type')
    severity = request.args.get('severity')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    try:
        logs = audit_logger.query_logs(
            page=page,
            page_size=page_size,
            event_type=event_type,
            severity=severity,
            start_time=start_time,
            end_time=end_time
        )
        
        return ApiResponse.page_success(
            logs['items'],
            logs['total'],
            page,
            page_size,
            "获取审计日志成功"
        )
        
    except Exception as e:
        return ApiResponse.error(f"获取审计日志失败: {str(e)}")


@monitor_bp.route('/audit/statistics', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_audit_statistics():
    """获取审计统计信息"""
    hours = request.args.get('hours', 24, type=int)
    
    try:
        stats = audit_logger.get_statistics(hours=hours)
        return ApiResponse.success(stats, "获取审计统计成功")
    except Exception as e:
        return ApiResponse.error(f"获取审计统计失败: {str(e)}")


@monitor_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        # 基本系统检查
        metrics = performance_monitor.get_current_metrics()
        
        # 判断系统健康状态
        cpu_usage = metrics['system']['cpu_usage']
        memory_usage = metrics['system']['memory_usage']
        disk_usage = metrics['system']['disk_usage']
        
        status = "healthy"
        issues = []
        
        if cpu_usage > 90:
            status = "warning"
            issues.append(f"CPU使用率过高: {cpu_usage}%")
        
        if memory_usage > 90:
            status = "warning"
            issues.append(f"内存使用率过高: {memory_usage}%")
        
        if disk_usage > 95:
            status = "critical"
            issues.append(f"磁盘使用率过高: {disk_usage}%")
        
        response_data = {
            'status': status,
            'timestamp': metrics['timestamp'],
            'system': {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'disk_usage': disk_usage
            },
            'issues': issues
        }
        
        # 根据状态返回不同的HTTP状态码
        if status == "critical":
            return jsonify(response_data), 503  # Service Unavailable
        elif status == "warning":
            return jsonify(response_data), 200  # OK but with warnings
        else:
            return jsonify(response_data), 200  # OK
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': performance_monitor.get_current_metrics().get('timestamp')
        }), 500


@monitor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_dashboard_data():
    """获取监控仪表板数据"""
    try:
        # 系统指标
        current_metrics = performance_monitor.get_current_metrics()
        
        # 近期告警
        recent_alerts = performance_monitor.get_alerts(hours=24)
        
        # 安全异常
        security_anomalies = anomaly_detector.get_anomaly_events(hours=24, min_risk_score=70)
        
        # 审计统计
        audit_stats = audit_logger.get_statistics(hours=24)
        
        # 合规性概览
        compliance_report = compliance_manager.generate_compliance_report()
        
        dashboard_data = {
            'overview': {
                'system_status': 'healthy' if all([
                    current_metrics['system']['cpu_usage'] < 80,
                    current_metrics['system']['memory_usage'] < 85,
                    current_metrics['system']['disk_usage'] < 90
                ]) else 'warning',
                'total_alerts': len(recent_alerts),
                'security_incidents': len(security_anomalies),
                'compliance_rate': compliance_report['compliance_rate']
            },
            'system_metrics': current_metrics,
            'recent_alerts': recent_alerts[:10],  # 最近10条告警
            'security_summary': {
                'high_risk_anomalies': len([a for a in security_anomalies if a.risk_score >= 80]),
                'blocked_ips': len(anomaly_detector.get_blocked_ips()),
                'failed_logins': sum(1 for a in security_anomalies if a.event_type == 'brute_force_attack')
            },
            'audit_summary': audit_stats,
            'compliance_summary': {
                'level': compliance_report['compliance_level'],
                'rate': compliance_report['compliance_rate'],
                'high_risk_items': len(compliance_report['high_risk_items'])
            }
        }
        
        return ApiResponse.success(dashboard_data, "获取仪表板数据成功")
        
    except Exception as e:
        return ApiResponse.error(f"获取仪表板数据失败: {str(e)}")


@monitor_bp.route('/start-monitoring', methods=['POST'])
@jwt_required()
@role_required('admin')
@require_api_signature
@log_operation("启动系统监控")
def start_monitoring():
    """启动系统监控"""
    data = request.json or {}
    interval = data.get('interval', 60)  # 默认60秒间隔
    
    try:
        performance_monitor.start_monitoring(interval)
        return ApiResponse.success(message="系统监控已启动")
    except Exception as e:
        return ApiResponse.error(f"启动系统监控失败: {str(e)}")


@monitor_bp.route('/stop-monitoring', methods=['POST'])
@jwt_required()
@role_required('admin')
@require_api_signature
@log_operation("停止系统监控")
def stop_monitoring():
    """停止系统监控"""
    try:
        performance_monitor.stop_monitoring()
        return ApiResponse.success(message="系统监控已停止")
    except Exception as e:
        return ApiResponse.error(f"停止系统监控失败: {str(e)}")