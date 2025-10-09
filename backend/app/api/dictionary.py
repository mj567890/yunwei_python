"""
数据字典管理API
"""
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
import sqlite3
import os

from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required, log_operation
from app.utils.exceptions import ValidationError as CustomValidationError, ResourceNotFoundError

dictionary_bp = Blueprint('dictionary', __name__)

def get_db_connection():
    """获取数据库连接"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'it_ops_system.db')
    return sqlite3.connect(db_path)

class DictItemSchema(Schema):
    """字典项参数验证"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    code = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))
    sort_order = fields.Int(missing=0)
    is_active = fields.Bool(missing=True)
    parent_id = fields.Int(allow_none=True)

class DepartmentSchema(Schema):
    """部门参数验证"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    code = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))
    parent_id = fields.Int(allow_none=True)
    sort_order = fields.Int(missing=0)
    is_active = fields.Bool(missing=True)

# =================== 运维记录类型管理 ===================

@dictionary_bp.route('/maintenance-types', methods=['GET'])
@login_required
def get_maintenance_types():
    """获取运维记录类型列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询运维记录类型
        cursor.execute('''
            SELECT id, name, code, description, parent_id, sort_order, is_active, created_at, updated_at
            FROM dict_maintenance_type 
            WHERE (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, created_at
        ''')
        
        types = []
        for row in cursor.fetchall():
            types.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'description': row[3],
                'parent_id': row[4],
                'sort_order': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        conn.close()
        return ApiResponse.success(types, "获取运维记录类型列表成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取运维记录类型列表失败: {str(e)}'
        }), 500

@dictionary_bp.route('/maintenance-types', methods=['POST'])
@login_required
@permission_required('dict:create')
@log_operation("创建运维记录类型")
def create_maintenance_type():
    """创建运维记录类型"""
    try:
        schema = DictItemSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查编码是否已存在
        cursor.execute('SELECT id FROM dict_maintenance_type WHERE code = ? AND (is_deleted = 0 OR is_deleted IS NULL)', (data['code'],))
        if cursor.fetchone():
            conn.close()
            raise CustomValidationError("编码已存在")
        
        # 创建记录
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO dict_maintenance_type (name, code, description, parent_id, sort_order, is_active, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
            data['name'], data['code'], data.get('description', ''),
            data.get('parent_id'), data['sort_order'], data['is_active'],
            now, now
        ))
        
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return ApiResponse.success({'id': new_id}, "创建运维记录类型成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'创建运维记录类型失败: {str(e)}'
        }), 500

@dictionary_bp.route('/maintenance-types/<int:type_id>', methods=['PUT'])
@login_required
@permission_required('dict:edit')
@log_operation("更新运维记录类型")
def update_maintenance_type(type_id):
    """更新运维记录类型"""
    try:
        schema = DictItemSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查记录是否存在
        cursor.execute('SELECT id FROM dict_maintenance_type WHERE id = ?', (type_id,))
        if not cursor.fetchone():
            conn.close()
            raise ResourceNotFoundError("运维记录类型不存在")
        
        # 检查编码是否被其他记录使用
        cursor.execute('SELECT id FROM dict_maintenance_type WHERE code = ? AND id != ? AND (is_deleted = 0 OR is_deleted IS NULL)', (data['code'], type_id))
        if cursor.fetchone():
            conn.close()
            raise CustomValidationError("编码已被其他记录使用")
        
        # 更新记录
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE dict_maintenance_type SET 
            name = ?, code = ?, description = ?, parent_id = ?, sort_order = ?, is_active = ?, updated_at = ?
            WHERE id = ?
        ''', (
            data['name'], data['code'], data.get('description', ''),
            data.get('parent_id'), data['sort_order'], data['is_active'],
            now, type_id
        ))
        
        conn.commit()
        conn.close()
        
        return ApiResponse.success(message="更新运维记录类型成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'更新运维记录类型失败: {str(e)}'
        }), 500

@dictionary_bp.route('/maintenance-types/<int:type_id>', methods=['DELETE'])
@login_required
@permission_required('dict:delete')
@log_operation("删除运维记录类型") 
def delete_maintenance_type(type_id):
    """删除运维记录类型（软删除）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查记录是否存在
        cursor.execute('SELECT id FROM dict_maintenance_type WHERE id = ?', (type_id,))
        if not cursor.fetchone():
            conn.close()
            raise ResourceNotFoundError("运维记录类型不存在")
        
        # 软删除
        now = datetime.now().isoformat()
        cursor.execute('UPDATE dict_maintenance_type SET is_deleted = 1, updated_at = ? WHERE id = ?', (now, type_id))
        
        conn.commit()
        conn.close()
        
        return ApiResponse.success(message="删除运维记录类型成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'删除运维记录类型失败: {str(e)}'
        }), 500

# =================== 运维维护类别管理 ===================

@dictionary_bp.route('/maintenance-categories', methods=['GET'])
@login_required
def get_maintenance_categories():
    """获取运维维护类别列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询运维维护类别
        cursor.execute('''
            SELECT id, name, code, description, parent_id, sort_order, is_active, created_at, updated_at
            FROM dict_maintenance_category 
            WHERE (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, created_at
        ''')
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row[0],
                'name': row[1],
                'code': row[2], 
                'description': row[3],
                'parent_id': row[4],
                'sort_order': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        conn.close()
        return ApiResponse.success(categories, "获取运维维护类别列表成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取运维维护类别列表失败: {str(e)}'
        }), 500

@dictionary_bp.route('/maintenance-categories', methods=['POST'])
@login_required
@permission_required('dict:create')
@log_operation("创建运维维护类别")
def create_maintenance_category():
    """创建运维维护类别"""
    try:
        schema = DictItemSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查编码是否已存在
        cursor.execute('SELECT id FROM dict_maintenance_category WHERE code = ? AND (is_deleted = 0 OR is_deleted IS NULL)', (data['code'],))
        if cursor.fetchone():
            conn.close()
            raise CustomValidationError("编码已存在")
        
        # 创建记录
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO dict_maintenance_category (name, code, description, parent_id, sort_order, is_active, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
            data['name'], data['code'], data.get('description', ''),
            data.get('parent_id'), data['sort_order'], data['is_active'],
            now, now
        ))
        
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return ApiResponse.success({'id': new_id}, "创建运维维护类别成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'创建运维维护类别失败: {str(e)}'
        }), 500

@dictionary_bp.route('/maintenance-categories/<int:category_id>', methods=['PUT'])
@login_required
@permission_required('dict:edit')
@log_operation("更新运维维护类别")
def update_maintenance_category(category_id):
    """更新运维维护类别"""
    try:
        schema = DictItemSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查记录是否存在
        cursor.execute('SELECT id FROM dict_maintenance_category WHERE id = ?', (category_id,))
        if not cursor.fetchone():
            conn.close()
            raise ResourceNotFoundError("运维维护类别不存在")
        
        # 检查编码是否被其他记录使用
        cursor.execute('SELECT id FROM dict_maintenance_category WHERE code = ? AND id != ? AND (is_deleted = 0 OR is_deleted IS NULL)', (data['code'], category_id))
        if cursor.fetchone():
            conn.close()
            raise CustomValidationError("编码已被其他记录使用")
        
        # 更新记录
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE dict_maintenance_category SET 
            name = ?, code = ?, description = ?, parent_id = ?, sort_order = ?, is_active = ?, updated_at = ?
            WHERE id = ?
        ''', (
            data['name'], data['code'], data.get('description', ''),
            data.get('parent_id'), data['sort_order'], data['is_active'],
            now, category_id
        ))
        
        conn.commit()
        conn.close()
        
        return ApiResponse.success(message="更新运维维护类别成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'更新运维维护类别失败: {str(e)}'
        }), 500

@dictionary_bp.route('/maintenance-categories/<int:category_id>', methods=['DELETE'])
@login_required
@permission_required('dict:delete')
@log_operation("删除运维维护类别") 
def delete_maintenance_category(category_id):
    """删除运维维护类别（软删除）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查记录是否存在
        cursor.execute('SELECT id FROM dict_maintenance_category WHERE id = ?', (category_id,))
        if not cursor.fetchone():
            conn.close()
            raise ResourceNotFoundError("运维维护类别不存在")
        
        # 软删除
        now = datetime.now().isoformat()
        cursor.execute('UPDATE dict_maintenance_category SET is_deleted = 1, updated_at = ? WHERE id = ?', (now, category_id))
        
        conn.commit()
        conn.close()
        
        return ApiResponse.success(message="删除运维维护类别成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取运维维护类别列表失败: {str(e)}'
        }), 500

# =================== 组织机构管理 ===================

@dictionary_bp.route('/departments', methods=['GET'])
@login_required
def get_departments():
    """获取组织机构列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询组织机构
        cursor.execute('''
            SELECT id, name, code, description, parent_id, sort_order, is_active, created_at, updated_at
            FROM dict_department 
            WHERE (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, created_at
        ''')
        
        departments = []
        for row in cursor.fetchall():
            departments.append({
                'id': row[0],
                'name': row[1],
                'code': row[2],
                'description': row[3],
                'parent_id': row[4],
                'sort_order': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        conn.close()
        return ApiResponse.success(departments, "获取组织机构列表成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取组织机构列表失败: {str(e)}'
        }), 500

@dictionary_bp.route('/departments', methods=['POST'])
@login_required
@permission_required('dict:create')
@log_operation("创建组织机构")
def create_department():
    """创建组织机构"""
    try:
        schema = DepartmentSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查编码是否已存在
        cursor.execute('SELECT id FROM dict_department WHERE code = ? AND (is_deleted = 0 OR is_deleted IS NULL)', (data['code'],))
        if cursor.fetchone():
            conn.close()
            raise CustomValidationError("编码已存在")
        
        # 创建记录
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO dict_department (name, code, description, parent_id, sort_order, is_active, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
            data['name'], data['code'], data.get('description', ''),
            data.get('parent_id'), data['sort_order'], data['is_active'],
            now, now
        ))
        
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return ApiResponse.success({'id': new_id}, "创建组织机构成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'创建组织机构失败: {str(e)}'
        }), 500

@dictionary_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@login_required
@permission_required('dict:edit')
@log_operation("更新组织机构")
def update_department(dept_id):
    """更新组织机构"""
    try:
        schema = DepartmentSchema()
        data = schema.load(request.json or {})
    except ValidationError as e:
        raise CustomValidationError("参数验证失败", e.messages)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查记录是否存在
        cursor.execute('SELECT id FROM dict_department WHERE id = ?', (dept_id,))
        if not cursor.fetchone():
            conn.close()
            raise ResourceNotFoundError("组织机构不存在")
        
        # 检查编码是否被其他记录使用
        cursor.execute('SELECT id FROM dict_department WHERE code = ? AND id != ? AND (is_deleted = 0 OR is_deleted IS NULL)', (data['code'], dept_id))
        if cursor.fetchone():
            conn.close()
            raise CustomValidationError("编码已被其他记录使用")
        
        # 更新记录
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE dict_department SET 
            name = ?, code = ?, description = ?, parent_id = ?, sort_order = ?, is_active = ?, updated_at = ?
            WHERE id = ?
        ''', (
            data['name'], data['code'], data.get('description', ''),
            data.get('parent_id'), data['sort_order'], data['is_active'],
            now, dept_id
        ))
        
        conn.commit()
        conn.close()
        
        return ApiResponse.success(message="更新组织机构成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'更新组织机构失败: {str(e)}'
        }), 500

@dictionary_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@login_required
@permission_required('dict:delete')
@log_operation("删除组织机构") 
def delete_department(dept_id):
    """删除组织机构（软删除）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查记录是否存在
        cursor.execute('SELECT id FROM dict_department WHERE id = ?', (dept_id,))
        if not cursor.fetchone():
            conn.close()
            raise ResourceNotFoundError("组织机构不存在")
        
        # 软删除
        now = datetime.now().isoformat()
        cursor.execute('UPDATE dict_department SET is_deleted = 1, updated_at = ? WHERE id = ?', (now, dept_id))
        
        conn.commit()
        conn.close()
        
        return ApiResponse.success(message="删除组织机构成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'创建组织机构失败: {str(e)}'
        }), 500

# =================== 通用接口 ===================

@dictionary_bp.route('/maintenance/types', methods=['GET'])
def get_types_for_maintenance():
    """为运维记录表单提供类型选项"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name FROM dict_maintenance_type 
            WHERE is_active = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, name
        ''')
        
        types = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 如果数据字典为空，返回默认值
        if not types:
            types = ['例行维护', '紧急处理', '升级改造', '故障修复', '巡检']
        
        return ApiResponse.success(types, "获取运维类型成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取运维类型失败: {str(e)}'
        }), 500

@dictionary_bp.route('/maintenance/categories', methods=['GET'])
def get_categories_for_maintenance():
    """为运维记录表单提供类别选项"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name FROM dict_maintenance_category 
            WHERE is_active = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, name
        ''')
        
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 如果数据字典为空，返回默认值
        if not categories:
            categories = ['硬件维护', '软件维护', '网络设备', '系统巡检', '故障修复']
        
        return ApiResponse.success(categories, "获取维护类别成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取维护类别失败: {str(e)}'
        }), 500

@dictionary_bp.route('/departments/simple', methods=['GET'])
def get_departments_for_form():
    """为表单提供部门选项"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name FROM dict_department 
            WHERE is_active = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY sort_order, name
        ''')
        
        departments = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 如果数据字典为空，返回默认值
        if not departments:
            departments = ['IT部门', '运维部门', '技术部门', '网络部门']
        
        return ApiResponse.success(departments, "获取部门列表成功")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'code': 500,
            'message': f'获取部门列表失败: {str(e)}'
        }), 500