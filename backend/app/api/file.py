"""
文件管理API
"""
import os
from flask import Blueprint, request, send_file, current_app
from werkzeug.utils import secure_filename
from datetime import datetime

from app.models.file import FileInfo
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required, log_operation
from app.utils.exceptions import ValidationError as CustomValidationError, ResourceNotFoundError
from app.utils.file_security import FileSecurityValidator
from app.utils.helpers import allowed_file, generate_unique_filename, get_file_hash, format_file_size, validate_file_content, check_file_size, sanitize_filename
from app import db

file_bp = Blueprint('file', __name__)


@file_bp.route('', methods=['GET'])
@login_required
@permission_required('maintenance:view')
def get_files():
    """获取文件列表"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    # 查询参数
    related_type = request.args.get('related_type', '').strip()
    related_id = request.args.get('related_id', type=int)
    file_type = request.args.get('file_type', '').strip()
    uploader_id = request.args.get('uploader_id', type=int)
    
    query = FileInfo.query.filter_by(is_deleted=False)
    
    if related_type:
        query = query.filter_by(related_type=related_type)
    if related_id:
        query = query.filter_by(related_id=related_id)
    if file_type:
        query = query.filter_by(file_type=file_type)
    if uploader_id:
        query = query.filter_by(uploader_id=uploader_id)
    
    # 文件名搜索
    filename = request.args.get('filename', '').strip()
    if filename:
        query = query.filter(FileInfo.original_filename.like(f'%{filename}%'))
    
    pagination = query.order_by(FileInfo.upload_time.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    files = [file_info.to_dict() for file_info in pagination.items]
    
    return ApiResponse.page_success(
        files,
        pagination.total,
        page,
        page_size,
        "获取文件列表成功"
    )


@file_bp.route('/<int:file_id>', methods=['GET'])
@login_required
@permission_required('maintenance:view')
def get_file(file_id):
    """获取文件详情"""
    file_info = FileInfo.find_by_id(file_id)
    if not file_info:
        raise ResourceNotFoundError("文件不存在")
    
    return ApiResponse.success(file_info.to_dict(), "获取文件详情成功")


@file_bp.route('/upload', methods=['POST'])
@login_required
@permission_required('maintenance:edit')
@log_operation("上传文件")
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        raise CustomValidationError("请选择要上传的文件")
    
    file = request.files['file']
    if file.filename == '':
        raise CustomValidationError("请选择要上传的文件")
    
    # 使用增强的安全验证
    is_valid, error_msg = FileSecurityValidator.validate_file(file)
    if not is_valid:
        raise CustomValidationError(error_msg)
    
    try:
        # 生成安全的文件名
        filename = FileSecurityValidator.get_safe_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取文件信息
        file_hash = get_file_hash(file_path)
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        # 获取MIME类型
        mime_type = file.content_type or 'application/octet-stream'
        
        # 创建文件记录
        from flask_jwt_extended import get_jwt_identity
        
        file_info = FileInfo(
            filename=filename,
            original_filename=sanitize_filename(file.filename),
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension,
            mime_type=mime_type,
            file_hash=file_hash,
            related_type=request.form.get('related_type'),
            related_id=int(request.form.get('related_id')) if request.form.get('related_id') else None,
            upload_time=datetime.utcnow(),
            uploader_id=get_jwt_identity(),
            description=request.form.get('description', ''),
            tags=request.form.get('tags', '')
        )
        
        file_info.save()
        
        return ApiResponse.success(file_info.to_dict(), "文件上传成功")
        
    except Exception as e:
        # 如果保存数据库失败，删除已上传的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        current_app.logger.error(f"上传文件失败: {str(e)}")
        raise CustomValidationError("文件上传失败")


@file_bp.route('/<int:file_id>/download', methods=['GET'])
@login_required
@permission_required('maintenance:view')
@log_operation("下载文件")
def download_file(file_id):
    """下载文件"""
    file_info = FileInfo.find_by_id(file_id)
    if not file_info:
        raise ResourceNotFoundError("文件不存在")
    
    if not os.path.exists(file_info.file_path):
        raise ResourceNotFoundError("文件已被删除或移动")
    
    try:
        # 增加下载次数
        file_info.download_count += 1
        db.session.commit()
        
        return send_file(
            file_info.file_path,
            as_attachment=True,
            download_name=file_info.original_filename,
            mimetype=file_info.mime_type
        )
    except Exception as e:
        current_app.logger.error(f"下载文件失败: {str(e)}")
        raise CustomValidationError("文件下载失败")


@file_bp.route('/<int:file_id>/preview', methods=['GET'])
@login_required
@permission_required('maintenance:view')
def preview_file(file_id):
    """预览文件"""
    file_info = FileInfo.find_by_id(file_id)
    if not file_info:
        raise ResourceNotFoundError("文件不存在")
    
    if not os.path.exists(file_info.file_path):
        raise ResourceNotFoundError("文件已被删除或移动")
    
    # 只支持图片和文本文件预览
    previewable_types = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'txt', 'md', 'log']
    if file_info.file_type.lower() not in previewable_types:
        raise CustomValidationError("该文件类型不支持预览")
    
    try:
        return send_file(
            file_info.file_path,
            mimetype=file_info.mime_type
        )
    except Exception as e:
        current_app.logger.error(f"预览文件失败: {str(e)}")
        raise CustomValidationError("文件预览失败")


@file_bp.route('/<int:file_id>', methods=['PUT'])
@login_required
@permission_required('maintenance:edit')
@log_operation("更新文件信息")
def update_file(file_id):
    """更新文件信息"""
    file_info = FileInfo.find_by_id(file_id)
    if not file_info:
        raise ResourceNotFoundError("文件不存在")
    
    data = request.json or {}
    
    # 允许更新的字段
    allowed_fields = ['description', 'tags', 'related_type', 'related_id']
    
    for field in allowed_fields:
        if field in data:
            if field == 'related_id' and data[field]:
                setattr(file_info, field, int(data[field]))
            else:
                setattr(file_info, field, data[field])
    
    file_info.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return ApiResponse.success(file_info.to_dict(), "文件信息更新成功")
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("文件信息更新失败")


@file_bp.route('/<int:file_id>', methods=['DELETE'])
@login_required
@permission_required('maintenance:edit')
@log_operation("删除文件")
def delete_file(file_id):
    """删除文件"""
    file_info = FileInfo.find_by_id(file_id)
    if not file_info:
        raise ResourceNotFoundError("文件不存在")
    
    try:
        # 软删除文件记录
        file_info.delete()
        
        # 可选：删除物理文件（根据需求决定）
        delete_physical = request.args.get('delete_physical', 'false').lower() == 'true'
        if delete_physical and os.path.exists(file_info.file_path):
            try:
                os.remove(file_info.file_path)
            except Exception as e:
                current_app.logger.warning(f"删除物理文件失败: {str(e)}")
        
        return ApiResponse.success(message="文件删除成功")
        
    except Exception as e:
        db.session.rollback()
        raise CustomValidationError("文件删除失败")


@file_bp.route('/batch-upload', methods=['POST'])
@login_required
@permission_required('maintenance:edit')
@log_operation("批量上传文件")
def batch_upload_files():
    """批量上传文件"""
    if 'files' not in request.files:
        raise CustomValidationError("请选择要上传的文件")
    
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        raise CustomValidationError("请选择要上传的文件")
    
    upload_results = []
    success_count = 0
    failed_count = 0
    
    related_type = request.form.get('related_type')
    related_id = int(request.form.get('related_id')) if request.form.get('related_id') else None
    description = request.form.get('description', '')
    tags = request.form.get('tags', '')
    
    for file in files:
        if file.filename == '':
            continue
        
        try:
            if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                upload_results.append({
                    'filename': file.filename,
                    'success': False,
                    'message': '不支持的文件格式'
                })
                failed_count += 1
                continue
            
            # 检查文件大小
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > current_app.config['MAX_CONTENT_LENGTH']:
                upload_results.append({
                    'filename': file.filename,
                    'success': False,
                    'message': '文件大小超出限制'
                })
                failed_count += 1
                continue
            
            # 生成唯一文件名
            filename = generate_unique_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            
            # 保存文件
            file.save(file_path)
            
            # 获取文件信息
            file_hash = get_file_hash(file_path)
            file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            mime_type = file.content_type or 'application/octet-stream'
            
            # 创建文件记录
            from flask_jwt_extended import get_jwt_identity
            
            file_info = FileInfo(
                filename=filename,
                original_filename=secure_filename(file.filename),
                file_path=file_path,
                file_size=file_size,
                file_type=file_extension,
                mime_type=mime_type,
                file_hash=file_hash,
                related_type=related_type,
                related_id=related_id,
                upload_time=datetime.utcnow(),
                uploader_id=get_jwt_identity(),
                description=description,
                tags=tags
            )
            
            file_info.save()
            
            upload_results.append({
                'filename': file.filename,
                'success': True,
                'file_id': file_info.id,
                'message': '上传成功'
            })
            success_count += 1
            
        except Exception as e:
            # 删除已上传的文件
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            upload_results.append({
                'filename': file.filename,
                'success': False,
                'message': f'上传失败: {str(e)}'
            })
            failed_count += 1
    
    return ApiResponse.success({
        'results': upload_results,
        'summary': {
            'total': len(files),
            'success': success_count,
            'failed': failed_count
        }
    }, f"批量上传完成，成功{success_count}个，失败{failed_count}个")


@file_bp.route('/statistics', methods=['GET'])
@login_required
@permission_required('maintenance:view')
def get_file_statistics():
    """获取文件统计"""
    # 总数统计
    total_count = FileInfo.query.filter_by(is_deleted=False).count()
    
    # 按类型统计
    type_stats = db.session.query(
        FileInfo.file_type,
        db.func.count(FileInfo.id).label('count'),
        db.func.sum(FileInfo.file_size).label('total_size')
    ).filter_by(is_deleted=False).group_by(FileInfo.file_type).all()
    
    # 按关联类型统计
    related_type_stats = db.session.query(
        FileInfo.related_type,
        db.func.count(FileInfo.id).label('count')
    ).filter_by(is_deleted=False).group_by(FileInfo.related_type).all()
    
    # 按上传者统计
    uploader_stats = db.session.query(
        FileInfo.uploader_id,
        db.func.count(FileInfo.id).label('count')
    ).filter_by(is_deleted=False).group_by(FileInfo.uploader_id).limit(10).all()
    
    # 总存储大小
    total_size = db.session.query(db.func.sum(FileInfo.file_size)).filter_by(is_deleted=False).scalar() or 0
    
    return ApiResponse.success({
        'total_count': total_count,
        'total_size': total_size,
        'total_size_formatted': format_file_size(total_size),
        'type_stats': [
            {
                'file_type': stat.file_type,
                'count': stat.count,
                'total_size': stat.total_size,
                'total_size_formatted': format_file_size(stat.total_size or 0)
            }
            for stat in type_stats
        ],
        'related_type_stats': [
            {'related_type': stat.related_type, 'count': stat.count}
            for stat in related_type_stats
        ],
        'uploader_stats': [
            {'uploader_id': stat.uploader_id, 'count': stat.count}
            for stat in uploader_stats
        ]
    }, "获取文件统计成功")


@file_bp.route('/cleanup', methods=['POST'])
@login_required
@permission_required('maintenance:edit')
@log_operation("清理文件")
def cleanup_files():
    """清理文件"""
    # 清理已删除的文件记录对应的物理文件
    deleted_files = FileInfo.query.filter_by(is_deleted=True).all()
    
    cleaned_count = 0
    error_count = 0
    
    for file_info in deleted_files:
        try:
            if os.path.exists(file_info.file_path):
                os.remove(file_info.file_path)
                cleaned_count += 1
        except Exception as e:
            current_app.logger.error(f"清理文件失败 {file_info.file_path}: {str(e)}")
            error_count += 1
    
    return ApiResponse.success({
        'cleaned_count': cleaned_count,
        'error_count': error_count
    }, f"文件清理完成，清理{cleaned_count}个文件，{error_count}个失败")