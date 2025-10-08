"""
故障分析API
"""
from flask import Blueprint, request
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

from app.models.fault import FaultRecord, FaultImpactAnalysis, FaultProgress
from app.models.asset import Asset
from app.models.network import NetworkDevice
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required, log_operation
from app.utils.exceptions import ValidationError as CustomValidationError, ResourceNotFoundError
from app.utils.helpers import generate_fault_code
from app import db

fault_bp = Blueprint('fault', __name__)


class FaultRecordSchema(Schema):
    """故障记录参数验证"""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    fault_type = fields.Str(required=True, validate=validate.OneOf(['硬件故障', '软件故障', '网络故障', '电源故障', '其他']))
    severity = fields.Str(validate=validate.OneOf(['低', '中', '高', '紧急']), missing='中')
    source_type = fields.Str(required=True, validate=validate.OneOf(['asset', 'device']))
    source_id = fields.Int(required=True)
    fault_time = fields.DateTime(missing=datetime.utcnow)
    building_id = fields.Int(allow_none=True)
    floor_id = fields.Int(allow_none=True)
    room_id = fields.Int(allow_none=True)
    problem_description = fields.Str(allow_none=True)


class FaultProgressSchema(Schema):
    """故障进度参数验证"""
    progress_type = fields.Str(required=True, validate=validate.OneOf(['接受', '分析', '处理', '测试', '完成']))
    description = fields.Str(required=True)


@fault_bp.route('', methods=['GET'])
@login_required
@permission_required('fault:view')
def get_faults():
    """获取故障列表"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    # 查询参数
    filters = {}
    for field in ['fault_type', 'severity', 'status', 'source_type']:
        value = request.args.get(field, '').strip()
        if value:
            filters[field] = value
    
    # 位置过滤
    building_id = request.args.get('building_id', type=int)
    floor_id = request.args.get('floor_id', type=int)
    room_id = request.args.get('room_id', type=int)
    
    if building_id:
        filters['building_id'] = building_id
    if floor_id:
        filters['floor_id'] = floor_id
    if room_id:
        filters['room_id'] = room_id
    
    # 时间范围过滤
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = FaultRecord.query.filter_by(is_deleted=False)
    
    # 应用过滤条件
    for key, value in filters.items():
        if hasattr(FaultRecord, key):
            query = query.filter(getattr(FaultRecord, key) == value)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(FaultRecord.fault_time >= start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(FaultRecord.fault_time <= end_dt)
        except:
            pass
    
    # 分页
    pagination = query.order_by(FaultRecord.fault_time.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    faults = [fault.to_dict() for fault in pagination.items]
    
    return ApiResponse.page_success(
        faults,
        pagination.total,
        page,
        page_size,
        "获取故障列表成功"
    )


@fault_bp.route('/<int:fault_id>', methods=['GET'])
@login_required
@permission_required('fault:view')
def get_fault(fault_id):
    """获取故障详情"""
    fault = FaultRecord.find_by_id(fault_id)
    if not fault:
        raise ResourceNotFoundError("故障记录不存在")
    
    fault_dict = fault.to_dict()
    
    # 获取进度记录
    progress_logs = fault.progress_logs.order_by(FaultProgress.progress_time.desc()).all()
    fault_dict['progress_logs'] = [log.to_dict() for log in progress_logs]
    
    return ApiResponse.success(fault_dict, "获取故障详情成功")


@fault_bp.route('', methods=['POST'])
@login_required
@permission_required('fault:handle')
@log_operation("创建故障记录")
def create_fault():
    """创建故障记录"""
    try:
        schema = FaultRecordSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 验证故障源是否存在
    if data['source_type'] == 'asset':
        source = Asset.find_by_id(data['source_id'])
        if not source:
            raise ResourceNotFoundError("资产不存在")
    elif data['source_type'] == 'device':
        source = NetworkDevice.find_by_id(data['source_id'])
        if not source:
            raise ResourceNotFoundError("设备不存在")
    
    # 生成故障编号
    data['fault_code'] = generate_fault_code()
    
    # 设置报告人
    from flask_jwt_extended import get_jwt_identity
    data['reporter_id'] = get_jwt_identity()
    
    # 如果没有指定位置，从故障源获取位置信息
    if not data.get('building_id') and hasattr(source, 'building_id'):
        data['building_id'] = source.building_id
        data['floor_id'] = source.floor_id
        data['room_id'] = source.room_id
    
    fault = FaultRecord(**data)
    
    try:
        fault.save()
        
        # 创建影响分析
        impact_analysis = FaultImpactAnalysis(fault_id=fault.id)
        impact_analysis.save()
        
        # 执行影响分析
        impact_analysis.analyze_impact()
        
        # 添加初始进度记录
        progress = FaultProgress(
            fault_id=fault.id,
            progress_type='接受',
            description='故障记录已创建，等待处理',
            operator_id=get_jwt_identity()
        )
        progress.save()
        
        return ApiResponse.success(fault.to_dict(), "故障记录创建成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("故障记录创建失败")


@fault_bp.route('/<int:fault_id>', methods=['PUT'])
@login_required
@permission_required('fault:handle')
@log_operation("更新故障记录")
def update_fault(fault_id):
    """更新故障记录"""
    fault = FaultRecord.find_by_id(fault_id)
    if not fault:
        raise ResourceNotFoundError("故障记录不存在")
    
    data = request.json or {}
    
    # 允许更新的字段
    allowed_fields = [
        'title', 'description', 'fault_type', 'severity', 'status',
        'assignee_id', 'problem_description', 'solution_description',
        'cause_analysis', 'prevention_measures', 'response_time',
        'resolve_time', 'impact_scope', 'affected_users', 'business_impact'
    ]
    
    old_status = fault.status
    
    for field in allowed_fields:
        if field in data:
            setattr(fault, field, data[field])
    
    fault.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # 如果状态发生变化，记录进度
        new_status = fault.status
        if old_status != new_status:
            from flask_jwt_extended import get_jwt_identity
            progress = FaultProgress(
                fault_id=fault_id,
                progress_type='处理',
                description=f'状态从"{old_status}"变更为"{new_status}"',
                operator_id=get_jwt_identity()
            )
            progress.save()
        
        return ApiResponse.success(fault.to_dict(), "故障记录更新成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("故障记录更新失败")


@fault_bp.route('/<int:fault_id>/assign', methods=['POST'])
@login_required
@permission_required('fault:handle')
@log_operation("分配故障处理人")
def assign_fault(fault_id):
    """分配故障处理人"""
    fault = FaultRecord.find_by_id(fault_id)
    if not fault:
        raise ResourceNotFoundError("故障记录不存在")
    
    data = request.json or {}
    assignee_id = data.get('assignee_id')
    
    if not assignee_id:
        raise CustomValidationError("处理人ID不能为空")
    
    # 验证处理人是否存在
    from app.models.user import User
    assignee = User.find_by_id(assignee_id)
    if not assignee:
        raise ResourceNotFoundError("处理人不存在")
    
    old_assignee_id = fault.assignee_id
    fault.assignee_id = assignee_id
    fault.status = '处理中'
    fault.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # 记录分配进度
        from flask_jwt_extended import get_jwt_identity
        progress = FaultProgress(
            fault_id=fault_id,
            progress_type='分析',
            description=f'故障已分配给 {assignee.real_name or assignee.username}',
            operator_id=get_jwt_identity()
        )
        progress.save()
        
        return ApiResponse.success(fault.to_dict(), "故障分配成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("故障分配失败")


@fault_bp.route('/<int:fault_id>/progress', methods=['POST'])
@login_required
@permission_required('fault:handle')
@log_operation("添加故障处理进度")
def add_fault_progress(fault_id):
    """添加故障处理进度"""
    fault = FaultRecord.find_by_id(fault_id)
    if not fault:
        raise ResourceNotFoundError("故障记录不存在")
    
    try:
        schema = FaultProgressSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    from flask_jwt_extended import get_jwt_identity
    
    progress = FaultProgress(
        fault_id=fault_id,
        progress_type=data['progress_type'],
        description=data['description'],
        operator_id=get_jwt_identity()
    )
    
    # 根据进度类型更新故障状态
    if data['progress_type'] == '完成':
        fault.status = '已解决'
        fault.resolve_time = datetime.utcnow()
    elif data['progress_type'] in ['分析', '处理']:
        fault.status = '处理中'
        if not fault.response_time:
            fault.response_time = datetime.utcnow()
    
    try:
        progress.save()
        db.session.commit()
        
        return ApiResponse.success({
            'fault': fault.to_dict(),
            'progress': progress.to_dict()
        }, "进度添加成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("进度添加失败")


@fault_bp.route('/<int:fault_id>/close', methods=['POST'])
@login_required
@permission_required('fault:handle')
@log_operation("关闭故障记录")
def close_fault(fault_id):
    """关闭故障记录"""
    fault = FaultRecord.find_by_id(fault_id)
    if not fault:
        raise ResourceNotFoundError("故障记录不存在")
    
    if fault.status == '已关闭':
        raise CustomValidationError("故障已经关闭")
    
    data = request.json or {}
    close_reason = data.get('close_reason', '故障处理完成')
    
    fault.status = '已关闭'
    fault.updated_at = datetime.utcnow()
    
    if not fault.resolve_time:
        fault.resolve_time = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # 记录关闭进度
        from flask_jwt_extended import get_jwt_identity
        progress = FaultProgress(
            fault_id=fault_id,
            progress_type='完成',
            description=close_reason,
            operator_id=get_jwt_identity()
        )
        progress.save()
        
        return ApiResponse.success(fault.to_dict(), "故障记录关闭成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("故障记录关闭失败")


@fault_bp.route('/<int:fault_id>/impact-analysis', methods=['GET'])
@login_required
@permission_required('fault:view')
def get_fault_impact_analysis(fault_id):
    """获取故障影响分析"""
    fault = FaultRecord.find_by_id(fault_id)
    if not fault:
        raise ResourceNotFoundError("故障记录不存在")
    
    if not fault.impact_analysis:
        return ApiResponse.success(None, "暂无影响分析")
    
    return ApiResponse.success(fault.impact_analysis.to_dict(), "获取影响分析成功")


@fault_bp.route('/<int:fault_id>/impact-analysis', methods=['POST'])
@login_required
@permission_required('fault:handle')
@log_operation("重新分析故障影响")
def reanalyze_fault_impact(fault_id):
    """重新分析故障影响"""
    fault = FaultRecord.find_by_id(fault_id)
    if not fault:
        raise ResourceNotFoundError("故障记录不存在")
    
    try:
        if fault.impact_analysis:
            # 重新分析
            fault.impact_analysis.analyze_impact()
        else:
            # 创建新的影响分析
            impact_analysis = FaultImpactAnalysis(fault_id=fault_id)
            impact_analysis.save()
            impact_analysis.analyze_impact()
        
        return ApiResponse.success(fault.impact_analysis.to_dict(), "影响分析完成")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("影响分析失败")


@fault_bp.route('/statistics', methods=['GET'])
@login_required
@permission_required('fault:view')
def get_fault_statistics():
    """获取故障统计"""
    # 总数统计
    total_count = FaultRecord.query.filter_by(is_deleted=False).count()
    
    # 状态统计
    status_stats = {}
    for status in ['待处理', '处理中', '已解决', '已关闭']:
        count = FaultRecord.query.filter_by(status=status, is_deleted=False).count()
        status_stats[status] = count
    
    # 严重程度统计
    severity_stats = {}
    for severity in ['低', '中', '高', '紧急']:
        count = FaultRecord.query.filter_by(severity=severity, is_deleted=False).count()
        severity_stats[severity] = count
    
    # 故障类型统计
    type_stats = {}
    for fault_type in ['硬件故障', '软件故障', '网络故障', '电源故障', '其他']:
        count = FaultRecord.query.filter_by(fault_type=fault_type, is_deleted=False).count()
        type_stats[fault_type] = count
    
    # 故障源统计
    source_stats = {}
    for source_type in ['asset', 'device']:
        count = FaultRecord.query.filter_by(source_type=source_type, is_deleted=False).count()
        source_stats[source_type] = count
    
    # 本月新增故障
    from datetime import datetime, timedelta
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_count = FaultRecord.query.filter(
        FaultRecord.fault_time >= current_month_start,
        FaultRecord.is_deleted == False
    ).count()
    
    # 平均处理时长（已解决的故障）
    resolved_faults = FaultRecord.query.filter_by(status='已解决', is_deleted=False).all()
    avg_resolve_time = 0
    if resolved_faults:
        total_resolve_time = sum([fault.get_resolve_duration() or 0 for fault in resolved_faults])
        avg_resolve_time = total_resolve_time / len(resolved_faults)
    
    return ApiResponse.success({
        'total_count': total_count,
        'status_stats': status_stats,
        'severity_stats': severity_stats,
        'type_stats': type_stats,
        'source_stats': source_stats,
        'monthly_count': monthly_count,
        'avg_resolve_time': round(avg_resolve_time, 2)
    }, "获取故障统计成功")