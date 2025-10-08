"""
运维记录管理API
"""
import os
from flask import Blueprint, request, send_file, current_app
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
from werkzeug.utils import secure_filename

from app.models.maintenance import MaintenanceRecord, MaintenanceAttachment, MaintenanceProgress, MaintenanceTemplate
from app.models.file import FileInfo
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required, log_operation
from app.utils.exceptions import ValidationError as CustomValidationError, ResourceNotFoundError
from app.utils.helpers import allowed_file, generate_unique_filename, get_file_hash
from app import db

maintenance_bp = Blueprint('maintenance', __name__)


class MaintenanceRecordSchema(Schema):
    """运维记录参数验证"""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    record_type = fields.Str(required=True, validate=validate.OneOf(['例行维护', '紧急处理', '升级改造', '故障修复', '巡检']))
    priority = fields.Str(validate=validate.OneOf(['低', '中', '高', '紧急']), missing='中')
    status = fields.Str(validate=validate.OneOf(['计划中', '进行中', '已完成', '已取消']), missing='计划中')
    planned_start_time = fields.DateTime(allow_none=True)
    planned_end_time = fields.DateTime(allow_none=True)
    actual_start_time = fields.DateTime(allow_none=True)
    actual_end_time = fields.DateTime(allow_none=True)
    assignee_id = fields.Int(allow_none=True)
    participants = fields.Str(allow_none=True, validate=validate.Length(max=255))
    description = fields.Str(allow_none=True)
    work_content = fields.Str(allow_none=True)
    result_description = fields.Str(allow_none=True)
    problem_description = fields.Str(allow_none=True)
    solution_description = fields.Str(allow_none=True)
    related_asset_ids = fields.Str(allow_none=True)
    related_device_ids = fields.Str(allow_none=True)
    building_id = fields.Int(allow_none=True)
    floor_id = fields.Int(allow_none=True)
    room_id = fields.Int(allow_none=True)
    location_detail = fields.Str(allow_none=True, validate=validate.Length(max=255))
    estimated_cost = fields.Decimal(allow_none=True, places=2)
    actual_cost = fields.Decimal(allow_none=True, places=2)
    cost_items = fields.Str(allow_none=True)
    difficulty_level = fields.Str(allow_none=True, validate=validate.OneOf(['简单', '中等', '困难', '复杂']))
    risk_level = fields.Str(allow_none=True, validate=validate.OneOf(['低', '中', '高']))
    impact_scope = fields.Str(allow_none=True, validate=validate.Length(max=100))


@maintenance_bp.route('', methods=['GET'])
@login_required
@permission_required('maintenance:view')
def get_maintenance_records():
    """获取运维记录列表"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    # 查询参数
    filters = {}
    for field in ['record_type', 'priority', 'status', 'difficulty_level', 'risk_level']:
        value = request.args.get(field, '').strip()
        if value:
            filters[field] = value
    
    # 负责人过滤
    assignee_id = request.args.get('assignee_id', type=int)
    if assignee_id:
        filters['assignee_id'] = assignee_id
    
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
    
    query = MaintenanceRecord.query.filter_by(is_deleted=False)
    
    # 应用过滤条件
    for key, value in filters.items():
        if hasattr(MaintenanceRecord, key):
            query = query.filter(getattr(MaintenanceRecord, key) == value)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(MaintenanceRecord.planned_start_time >= start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(MaintenanceRecord.planned_start_time <= end_dt)
        except:
            pass
    
    # 分页
    pagination = query.order_by(MaintenanceRecord.planned_start_time.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    records = [record.to_dict() for record in pagination.items]
    
    return ApiResponse.page_success(
        records,
        pagination.total,
        page,
        page_size,
        "获取运维记录列表成功"
    )


@maintenance_bp.route('/<int:record_id>', methods=['GET'])
@login_required
@permission_required('maintenance:view')
def get_maintenance_record(record_id):
    """获取运维记录详情"""
    record = MaintenanceRecord.find_by_id(record_id)
    if not record:
        raise ResourceNotFoundError("运维记录不存在")
    
    record_dict = record.to_dict()
    
    # 获取附件列表
    attachments = record.attachments.filter_by(is_deleted=False).all()
    record_dict['attachments'] = [attachment.to_dict() for attachment in attachments]
    
    # 获取进度记录
    progress_logs = record.progress_logs.order_by(MaintenanceProgress.progress_time.desc()).all()
    record_dict['progress_logs'] = [log.to_dict() for log in progress_logs]
    
    # 获取关联资产和设备
    record_dict['related_assets'] = [asset.to_dict() for asset in record.get_related_assets()]
    record_dict['related_devices'] = [device.to_dict() for device in record.get_related_devices()]
    
    return ApiResponse.success(record_dict, "获取运维记录详情成功")


@maintenance_bp.route('', methods=['POST'])
@login_required
@permission_required('maintenance:create')
@log_operation("创建运维记录")
def create_maintenance_record():
    """创建运维记录"""
    try:
        schema = MaintenanceRecordSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 设置报告人
    from flask_jwt_extended import get_jwt_identity
    data['reporter_id'] = get_jwt_identity()
    
    # 验证负责人是否存在
    if data.get('assignee_id'):
        from app.models.user import User
        assignee = User.find_by_id(data['assignee_id'])
        if not assignee:
            raise ResourceNotFoundError("负责人不存在")
    
    # 验证位置信息
    if data.get('room_id'):
        from app.models.location import Room
        room = Room.find_by_id(data['room_id'])
        if not room:
            raise ResourceNotFoundError("房间不存在")
        data['floor_id'] = room.floor_id
        data['building_id'] = room.floor.building_id
    elif data.get('floor_id'):
        from app.models.location import Floor
        floor = Floor.find_by_id(data['floor_id'])
        if not floor:
            raise ResourceNotFoundError("楼层不存在")
        data['building_id'] = floor.building_id
    elif data.get('building_id'):
        from app.models.location import Building
        building = Building.find_by_id(data['building_id'])
        if not building:
            raise ResourceNotFoundError("楼宇不存在")
    
    record = MaintenanceRecord(**data)
    
    try:
        record.save()
        
        # 添加初始进度记录
        progress = MaintenanceProgress(
            record_id=record.id,
            progress_time=datetime.utcnow(),
            progress_content='运维记录已创建',
            progress_type='开始',
            operator_id=get_jwt_identity()
        )
        progress.save()
        
        return ApiResponse.success(record.to_dict(), "运维记录创建成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("运维记录创建失败")


@maintenance_bp.route('/<int:record_id>', methods=['PUT'])
@login_required
@permission_required('maintenance:edit')
@log_operation("更新运维记录")
def update_maintenance_record(record_id):
    """更新运维记录"""
    record = MaintenanceRecord.find_by_id(record_id)
    if not record:
        raise ResourceNotFoundError("运维记录不存在")
    
    try:
        schema = MaintenanceRecordSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    # 验证负责人是否存在
    if data.get('assignee_id'):
        from app.models.user import User
        assignee = User.find_by_id(data['assignee_id'])
        if not assignee:
            raise ResourceNotFoundError("负责人不存在")
    
    # 验证位置信息
    if data.get('room_id'):
        from app.models.location import Room
        room = Room.find_by_id(data['room_id'])
        if not room:
            raise ResourceNotFoundError("房间不存在")
        data['floor_id'] = room.floor_id
        data['building_id'] = room.floor.building_id
    elif data.get('floor_id'):
        from app.models.location import Floor
        floor = Floor.find_by_id(data['floor_id'])
        if not floor:
            raise ResourceNotFoundError("楼层不存在")
        data['building_id'] = floor.building_id
    elif data.get('building_id'):
        from app.models.location import Building
        building = Building.find_by_id(data['building_id'])
        if not building:
            raise ResourceNotFoundError("楼宇不存在")
    
    old_status = record.status
    
    # 更新记录信息
    for key, value in data.items():
        setattr(record, key, value)
    
    record.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # 如果状态发生变化，记录进度
        new_status = record.status
        if old_status != new_status:
            from flask_jwt_extended import get_jwt_identity
            progress = MaintenanceProgress(
                record_id=record_id,
                progress_time=datetime.utcnow(),
                progress_content=f'状态从"{old_status}"变更为"{new_status}"',
                progress_type='进行中',
                operator_id=get_jwt_identity()
            )
            progress.save()
        
        return ApiResponse.success(record.to_dict(), "运维记录更新成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("运维记录更新失败")


@maintenance_bp.route('/<int:record_id>', methods=['DELETE'])
@login_required
@permission_required('maintenance:delete')
@log_operation("删除运维记录")
def delete_maintenance_record(record_id):
    """删除运维记录"""
    record = MaintenanceRecord.find_by_id(record_id)
    if not record:
        raise ResourceNotFoundError("运维记录不存在")
    
    record.delete()
    return ApiResponse.success(message="运维记录删除成功")


@maintenance_bp.route('/<int:record_id>/progress', methods=['POST'])
@login_required
@permission_required('maintenance:edit')
@log_operation("添加运维进度")
def add_maintenance_progress(record_id):
    """添加运维进度"""
    record = MaintenanceRecord.find_by_id(record_id)
    if not record:
        raise ResourceNotFoundError("运维记录不存在")
    
    data = request.json or {}
    progress_content = data.get('progress_content')
    progress_type = data.get('progress_type', '进行中')
    
    if not progress_content:
        raise CustomValidationError("进度内容不能为空")
    
    from flask_jwt_extended import get_jwt_identity
    
    progress = MaintenanceProgress(
        record_id=record_id,
        progress_time=datetime.utcnow(),
        progress_content=progress_content,
        progress_type=progress_type,
        operator_id=get_jwt_identity()
    )
    
    # 根据进度类型更新记录状态
    if progress_type == '完成':
        record.status = '已完成'
        if not record.actual_end_time:
            record.actual_end_time = datetime.utcnow()
    elif progress_type == '开始':
        record.status = '进行中'
        if not record.actual_start_time:
            record.actual_start_time = datetime.utcnow()
    
    try:
        progress.save()
        db.session.commit()
        
        return ApiResponse.success({
            'record': record.to_dict(),
            'progress': progress.to_dict()
        }, "进度添加成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("进度添加失败")


@maintenance_bp.route('/<int:record_id>/attachments/upload', methods=['POST'])
@login_required
@permission_required('maintenance:edit')
@log_operation("上传运维附件")
def upload_maintenance_attachment(record_id):
    """上传运维附件"""
    record = MaintenanceRecord.find_by_id(record_id)
    if not record:
        raise ResourceNotFoundError("运维记录不存在")
    
    if 'file' not in request.files:
        raise CustomValidationError("请选择要上传的文件")
    
    file = request.files['file']
    if file.filename == '':
        raise CustomValidationError("请选择要上传的文件")
    
    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        raise CustomValidationError("不支持的文件格式")
    
    try:
        # 生成唯一文件名
        filename = generate_unique_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        file_hash = get_file_hash(file_path)
        
        # 创建附件记录
        attachment = MaintenanceAttachment(
            record_id=record_id,
            filename=filename,
            original_filename=secure_filename(file.filename),
            file_path=file_path,
            file_size=file_size,
            file_type=file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else '',
            upload_time=datetime.utcnow(),
            description=request.form.get('description', '')
        )
        
        # 创建文件信息记录
        file_info = FileInfo(
            filename=filename,
            original_filename=secure_filename(file.filename),
            file_path=file_path,
            file_size=file_size,
            file_type=attachment.file_type,
            file_hash=file_hash,
            related_type='maintenance',
            related_id=record_id,
            upload_time=datetime.utcnow(),
            uploader_id=request.form.get('uploader_id')
        )
        
        attachment.save()
        file_info.save()
        
        return ApiResponse.success(attachment.to_dict(), "附件上传成功")
        
    except Exception as e:
        current_app.logger.error(f"上传附件失败: {str(e)}")
        raise CustomValidationError("附件上传失败")


@maintenance_bp.route('/attachments/<int:attachment_id>/download', methods=['GET'])
@login_required
@permission_required('maintenance:view')
def download_maintenance_attachment(attachment_id):
    """下载运维附件"""
    attachment = MaintenanceAttachment.find_by_id(attachment_id)
    if not attachment:
        raise ResourceNotFoundError("附件不存在")
    
    if not os.path.exists(attachment.file_path):
        raise ResourceNotFoundError("文件不存在")
    
    try:
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.original_filename
        )
    except Exception as e:
        current_app.logger.error(f"下载附件失败: {str(e)}")
        raise CustomValidationError("文件下载失败")


@maintenance_bp.route('/templates', methods=['GET'])
@login_required
@permission_required('maintenance:view')
def get_maintenance_templates():
    """获取运维模板列表"""
    templates = MaintenanceTemplate.query.filter_by(is_deleted=False, is_active=True).all()
    template_list = [template.to_dict() for template in templates]
    
    return ApiResponse.success(template_list, "获取运维模板列表成功")


@maintenance_bp.route('/statistics', methods=['GET'])
@login_required
@permission_required('maintenance:view')
def get_maintenance_statistics():
    """获取运维统计"""
    # 总数统计
    total_count = MaintenanceRecord.query.filter_by(is_deleted=False).count()
    
    # 状态统计
    status_stats = {}
    for status in ['计划中', '进行中', '已完成', '已取消']:
        count = MaintenanceRecord.query.filter_by(status=status, is_deleted=False).count()
        status_stats[status] = count
    
    # 优先级统计
    priority_stats = {}
    for priority in ['低', '中', '高', '紧急']:
        count = MaintenanceRecord.query.filter_by(priority=priority, is_deleted=False).count()
        priority_stats[priority] = count
    
    # 类型统计
    type_stats = {}
    for record_type in ['例行维护', '紧急处理', '升级改造', '故障修复', '巡检']:
        count = MaintenanceRecord.query.filter_by(record_type=record_type, is_deleted=False).count()
        type_stats[record_type] = count
    
    # 本月完成统计
    from datetime import datetime, timedelta
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_completed = MaintenanceRecord.query.filter(
        MaintenanceRecord.status == '已完成',
        MaintenanceRecord.actual_end_time >= current_month_start,
        MaintenanceRecord.is_deleted == False
    ).count()
    
    # 平均工期计算（已完成的记录）
    completed_records = MaintenanceRecord.query.filter_by(status='已完成', is_deleted=False).all()
    avg_duration = 0
    if completed_records:
        total_duration = sum([record.get_actual_duration() or 0 for record in completed_records])
        avg_duration = total_duration / len(completed_records)
    
    # 总成本统计
    total_cost = db.session.query(db.func.sum(MaintenanceRecord.actual_cost)).filter_by(is_deleted=False).scalar() or 0
    
    return ApiResponse.success({
        'total_count': total_count,
        'status_stats': status_stats,
        'priority_stats': priority_stats,
        'type_stats': type_stats,
        'monthly_completed': monthly_completed,
        'avg_duration': round(avg_duration, 2),
        'total_cost': float(total_cost)
    }, "获取运维统计成功")