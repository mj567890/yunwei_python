"""
统计分析API
"""
from flask import Blueprint, request
from datetime import datetime, timedelta
from sqlalchemy import func, text

from app.models.asset import Asset
from app.models.network import NetworkDevice
from app.models.maintenance import MaintenanceRecord
from app.models.fault import FaultRecord
from app.models.user import OperationLog
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required
from app import db

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/dashboard', methods=['GET'])
@login_required
@permission_required('statistics:view')
def get_dashboard_statistics():
    """获取仪表板统计数据"""
    # 资产统计
    asset_stats = {
        'total': Asset.query.filter_by(is_deleted=False).count(),
        'in_use': Asset.query.filter_by(status='在用', is_deleted=False).count(),
        'idle': Asset.query.filter_by(status='闲置', is_deleted=False).count(),
        'maintenance': Asset.query.filter_by(status='维修', is_deleted=False).count(),
        'scrapped': Asset.query.filter_by(status='报废', is_deleted=False).count()
    }
    
    # 网络设备统计
    device_stats = {
        'total': NetworkDevice.query.filter_by(is_deleted=False).count(),
        'normal': NetworkDevice.query.filter_by(status='正常', is_deleted=False).count(),
        'fault': NetworkDevice.query.filter_by(status='故障', is_deleted=False).count(),
        'maintenance': NetworkDevice.query.filter_by(status='维护', is_deleted=False).count(),
        'offline': NetworkDevice.query.filter_by(status='离线', is_deleted=False).count()
    }
    
    # 运维记录统计
    maintenance_stats = {
        'total': MaintenanceRecord.query.filter_by(is_deleted=False).count(),
        'planned': MaintenanceRecord.query.filter_by(status='计划中', is_deleted=False).count(),
        'in_progress': MaintenanceRecord.query.filter_by(status='进行中', is_deleted=False).count(),
        'completed': MaintenanceRecord.query.filter_by(status='已完成', is_deleted=False).count(),
        'cancelled': MaintenanceRecord.query.filter_by(status='已取消', is_deleted=False).count()
    }
    
    # 故障统计
    fault_stats = {
        'total': FaultRecord.query.filter_by(is_deleted=False).count(),
        'pending': FaultRecord.query.filter_by(status='待处理', is_deleted=False).count(),
        'processing': FaultRecord.query.filter_by(status='处理中', is_deleted=False).count(),
        'resolved': FaultRecord.query.filter_by(status='已解决', is_deleted=False).count(),
        'closed': FaultRecord.query.filter_by(status='已关闭', is_deleted=False).count()
    }
    
    # 本月新增统计
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_stats = {
        'assets': Asset.query.filter(Asset.created_at >= current_month_start, Asset.is_deleted == False).count(),
        'devices': NetworkDevice.query.filter(NetworkDevice.created_at >= current_month_start, NetworkDevice.is_deleted == False).count(),
        'maintenance': MaintenanceRecord.query.filter(MaintenanceRecord.created_at >= current_month_start, MaintenanceRecord.is_deleted == False).count(),
        'faults': FaultRecord.query.filter(FaultRecord.fault_time >= current_month_start, FaultRecord.is_deleted == False).count()
    }
    
    # 保修预警
    warranty_alerts = 0
    assets = Asset.query.filter_by(is_deleted=False).all()
    for asset in assets:
        if asset.is_warranty_expiring(30):  # 30天内到期
            warranty_alerts += 1
    
    return ApiResponse.success({
        'asset_stats': asset_stats,
        'device_stats': device_stats,
        'maintenance_stats': maintenance_stats,
        'fault_stats': fault_stats,
        'monthly_stats': monthly_stats,
        'warranty_alerts': warranty_alerts
    }, "获取仪表板统计成功")


@statistics_bp.route('/assets/category', methods=['GET'])
@login_required
@permission_required('statistics:view')
def get_asset_category_statistics():
    """获取资产类别统计"""
    # 按类别统计
    category_stats = db.session.query(
        Asset.category,
        func.count(Asset.id).label('count')
    ).filter_by(is_deleted=False).group_by(Asset.category).all()
    
    # 按状态统计
    status_stats = db.session.query(
        Asset.status,
        func.count(Asset.id).label('count')
    ).filter_by(is_deleted=False).group_by(Asset.status).all()
    
    # 按位置统计（楼宇）
    location_stats = db.session.query(
        text('b.name as building_name'),
        func.count(Asset.id).label('count')
    ).select_from(Asset).join(
        text('building_info b ON asset.building_id = b.id')
    ).filter(Asset.is_deleted == False).group_by(text('b.name')).all()
    
    return ApiResponse.success({
        'category_stats': [{'category': cat, 'count': count} for cat, count in category_stats],
        'status_stats': [{'status': status, 'count': count} for status, count in status_stats],
        'location_stats': [{'building': building, 'count': count} for building, count in location_stats]
    }, "获取资产类别统计成功")


@statistics_bp.route('/assets/trend', methods=['GET'])
@login_required
@permission_required('statistics:view')
def get_asset_trend():
    """获取资产趋势统计"""
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 按日期统计新增资产
    daily_stats = db.session.query(
        func.date(Asset.created_at).label('date'),
        func.count(Asset.id).label('count')
    ).filter(
        Asset.created_at >= start_date,
        Asset.created_at <= end_date,
        Asset.is_deleted == False
    ).group_by(func.date(Asset.created_at)).all()
    
    # 生成完整的日期序列
    trend_data = []
    current_date = start_date.date()
    stats_dict = {stat.date: stat.count for stat in daily_stats}
    
    while current_date <= end_date.date():
        trend_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'count': stats_dict.get(current_date, 0)
        })
        current_date += timedelta(days=1)
    
    return ApiResponse.success(trend_data, "获取资产趋势统计成功")


@statistics_bp.route('/maintenance/workload', methods=['GET'])
@login_required
@permission_required('statistics:view')
def get_maintenance_workload():
    """获取运维工作量统计"""
    # 按人员统计工作量
    user_workload = db.session.query(
        text('u.real_name as assignee_name'),
        func.count(MaintenanceRecord.id).label('total_count'),
        func.sum(
            func.case(
                [(MaintenanceRecord.status == '已完成', 1)],
                else_=0
            )
        ).label('completed_count'),
        func.avg(
            func.case(
                [(MaintenanceRecord.actual_end_time.isnot(None),
                  func.timestampdiff(text('HOUR'), MaintenanceRecord.actual_start_time, MaintenanceRecord.actual_end_time))],
                else_=None
            )
        ).label('avg_duration')
    ).select_from(MaintenanceRecord).join(
        text('sys_user u ON maintenance_record.assignee_id = u.id')
    ).filter(
        MaintenanceRecord.is_deleted == False,
        MaintenanceRecord.assignee_id.isnot(None)
    ).group_by(text('u.real_name')).all()
    
    # 按类型统计
    type_workload = db.session.query(
        MaintenanceRecord.record_type,
        func.count(MaintenanceRecord.id).label('count'),
        func.avg(MaintenanceRecord.actual_cost).label('avg_cost')
    ).filter_by(is_deleted=False).group_by(MaintenanceRecord.record_type).all()
    
    return ApiResponse.success({
        'user_workload': [
            {
                'assignee_name': user.assignee_name,
                'total_count': user.total_count,
                'completed_count': user.completed_count or 0,
                'avg_duration': round(float(user.avg_duration or 0), 2)
            }
            for user in user_workload
        ],
        'type_workload': [
            {
                'record_type': type_stat.record_type,
                'count': type_stat.count,
                'avg_cost': round(float(type_stat.avg_cost or 0), 2)
            }
            for type_stat in type_workload
        ]
    }, "获取运维工作量统计成功")


@statistics_bp.route('/faults/analysis', methods=['GET'])
@login_required
@permission_required('statistics:view')
def get_fault_analysis():
    """获取故障分析统计"""
    # 按类型统计
    type_stats = db.session.query(
        FaultRecord.fault_type,
        func.count(FaultRecord.id).label('count'),
        func.avg(
            func.case(
                [(FaultRecord.resolve_time.isnot(None),
                  func.timestampdiff(text('HOUR'), FaultRecord.report_time, FaultRecord.resolve_time))],
                else_=None
            )
        ).label('avg_resolve_time')
    ).filter_by(is_deleted=False).group_by(FaultRecord.fault_type).all()
    
    # 按严重程度统计
    severity_stats = db.session.query(
        FaultRecord.severity,
        func.count(FaultRecord.id).label('count')
    ).filter_by(is_deleted=False).group_by(FaultRecord.severity).all()
    
    # 按月份统计故障趋势
    monthly_trend = db.session.query(
        func.date_format(FaultRecord.fault_time, '%Y-%m').label('month'),
        func.count(FaultRecord.id).label('count')
    ).filter_by(is_deleted=False).group_by(
        func.date_format(FaultRecord.fault_time, '%Y-%m')
    ).order_by(
        func.date_format(FaultRecord.fault_time, '%Y-%m')
    ).limit(12).all()
    
    return ApiResponse.success({
        'type_stats': [
            {
                'fault_type': stat.fault_type,
                'count': stat.count,
                'avg_resolve_time': round(float(stat.avg_resolve_time or 0), 2)
            }
            for stat in type_stats
        ],
        'severity_stats': [
            {'severity': stat.severity, 'count': stat.count}
            for stat in severity_stats
        ],
        'monthly_trend': [
            {'month': stat.month, 'count': stat.count}
            for stat in monthly_trend
        ]
    }, "获取故障分析统计成功")


@statistics_bp.route('/locations/distribution', methods=['GET'])
@login_required
@permission_required('statistics:view')
def get_location_distribution():
    """获取位置分布统计"""
    # 资产按楼宇分布
    asset_distribution = db.session.query(
        text('b.name as building_name'),
        func.count(Asset.id).label('asset_count')
    ).select_from(Asset).join(
        text('building_info b ON it_asset.building_id = b.id')
    ).filter(Asset.is_deleted == False).group_by(text('b.name')).all()
    
    # 设备按楼宇分布
    device_distribution = db.session.query(
        text('b.name as building_name'),
        func.count(NetworkDevice.id).label('device_count')
    ).select_from(NetworkDevice).join(
        text('building_info b ON network_device.building_id = b.id')
    ).filter(NetworkDevice.is_deleted == False).group_by(text('b.name')).all()
    
    # 故障按楼宇分布
    fault_distribution = db.session.query(
        text('b.name as building_name'),
        func.count(FaultRecord.id).label('fault_count')
    ).select_from(FaultRecord).join(
        text('building_info b ON fault_record.building_id = b.id')
    ).filter(FaultRecord.is_deleted == False).group_by(text('b.name')).all()
    
    return ApiResponse.success({
        'asset_distribution': [
            {'building_name': dist.building_name, 'count': dist.asset_count}
            for dist in asset_distribution
        ],
        'device_distribution': [
            {'building_name': dist.building_name, 'count': dist.device_count}
            for dist in device_distribution
        ],
        'fault_distribution': [
            {'building_name': dist.building_name, 'count': dist.fault_count}
            for dist in fault_distribution
        ]
    }, "获取位置分布统计成功")


@statistics_bp.route('/costs/analysis', methods=['GET'])
@login_required
@permission_required('statistics:view')
def get_cost_analysis():
    """获取成本分析统计"""
    # 资产采购成本按类别统计
    asset_cost_by_category = db.session.query(
        Asset.category,
        func.sum(Asset.purchase_price).label('total_cost'),
        func.avg(Asset.purchase_price).label('avg_cost'),
        func.count(Asset.id).label('count')
    ).filter(
        Asset.is_deleted == False,
        Asset.purchase_price.isnot(None)
    ).group_by(Asset.category).all()
    
    # 运维成本按类型统计
    maintenance_cost_by_type = db.session.query(
        MaintenanceRecord.record_type,
        func.sum(MaintenanceRecord.actual_cost).label('total_cost'),
        func.avg(MaintenanceRecord.actual_cost).label('avg_cost'),
        func.count(MaintenanceRecord.id).label('count')
    ).filter(
        MaintenanceRecord.is_deleted == False,
        MaintenanceRecord.actual_cost.isnot(None)
    ).group_by(MaintenanceRecord.record_type).all()
    
    # 月度成本趋势
    monthly_cost_trend = db.session.query(
        func.date_format(MaintenanceRecord.actual_end_time, '%Y-%m').label('month'),
        func.sum(MaintenanceRecord.actual_cost).label('total_cost')
    ).filter(
        MaintenanceRecord.is_deleted == False,
        MaintenanceRecord.actual_cost.isnot(None),
        MaintenanceRecord.actual_end_time.isnot(None)
    ).group_by(
        func.date_format(MaintenanceRecord.actual_end_time, '%Y-%m')
    ).order_by(
        func.date_format(MaintenanceRecord.actual_end_time, '%Y-%m')
    ).limit(12).all()
    
    return ApiResponse.success({
        'asset_cost_by_category': [
            {
                'category': stat.category,
                'total_cost': float(stat.total_cost or 0),
                'avg_cost': float(stat.avg_cost or 0),
                'count': stat.count
            }
            for stat in asset_cost_by_category
        ],
        'maintenance_cost_by_type': [
            {
                'record_type': stat.record_type,
                'total_cost': float(stat.total_cost or 0),
                'avg_cost': float(stat.avg_cost or 0),
                'count': stat.count
            }
            for stat in maintenance_cost_by_type
        ],
        'monthly_cost_trend': [
            {
                'month': stat.month,
                'total_cost': float(stat.total_cost or 0)
            }
            for stat in monthly_cost_trend
        ]
    }, "获取成本分析统计成功")


@statistics_bp.route('/operations/log', methods=['GET'])
@login_required
@permission_required('statistics:view')
def get_operation_statistics():
    """获取操作统计"""
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 按操作类型统计
    operation_stats = db.session.query(
        OperationLog.operation,
        func.count(OperationLog.id).label('count')
    ).filter(
        OperationLog.created_at >= start_date,
        OperationLog.created_at <= end_date
    ).group_by(OperationLog.operation).all()
    
    # 按用户统计
    user_stats = db.session.query(
        OperationLog.username,
        func.count(OperationLog.id).label('count')
    ).filter(
        OperationLog.created_at >= start_date,
        OperationLog.created_at <= end_date
    ).group_by(OperationLog.username).order_by(
        func.count(OperationLog.id).desc()
    ).limit(10).all()
    
    # 按小时统计活跃度
    hourly_stats = db.session.query(
        func.hour(OperationLog.created_at).label('hour'),
        func.count(OperationLog.id).label('count')
    ).filter(
        OperationLog.created_at >= start_date,
        OperationLog.created_at <= end_date
    ).group_by(func.hour(OperationLog.created_at)).all()
    
    return ApiResponse.success({
        'operation_stats': [
            {'operation': stat.operation, 'count': stat.count}
            for stat in operation_stats
        ],
        'user_stats': [
            {'username': stat.username, 'count': stat.count}
            for stat in user_stats
        ],
        'hourly_stats': [
            {'hour': stat.hour, 'count': stat.count}
            for stat in hourly_stats
        ]
    }, "获取操作统计成功")