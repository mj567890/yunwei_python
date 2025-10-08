#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资产类别管理API
"""
from flask import Blueprint, request, jsonify
from app.models.asset import Asset
from app.utils.response import ApiResponse
from app.utils.auth import login_required, permission_required
from app import db
from datetime import datetime
import sqlite3

category_bp = Blueprint('category', __name__)

class AssetCategory:
    """资产类别模型"""
    def __init__(self, id=None, name=None, code=None, parent_id=None, description=None, 
                 sort_order=0, is_network_device=False, can_topology=False, 
                 is_terminal=False, default_port_count=0, device_icon=None, 
                 device_color=None, created_at=None, updated_at=None, is_deleted=False):
        self.id = id
        self.name = name
        self.code = code
        self.parent_id = parent_id
        self.description = description
        self.sort_order = sort_order
        self.is_network_device = is_network_device
        self.can_topology = can_topology
        self.is_terminal = is_terminal
        self.default_port_count = default_port_count
        self.device_icon = device_icon
        self.device_color = device_color
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_deleted = is_deleted
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_network_device': bool(self.is_network_device),
            'can_topology': bool(self.can_topology),
            'is_terminal': bool(self.is_terminal),
            'default_port_count': self.default_port_count,
            'device_icon': self.device_icon,
            'device_color': self.device_color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

def get_db_connection():
    """获取数据库连接"""
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'it_ops_system.db')
    return sqlite3.connect(db_path)

@category_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有资产类别"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取查询参数
        network_only = request.args.get('network_only', 'false').lower() == 'true'
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if not include_deleted:
            where_conditions.append('(is_deleted = 0 OR is_deleted IS NULL)')
        
        if network_only:
            where_conditions.append('is_network_device = 1')
        
        where_clause = ' WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        query = f'''
        SELECT id, name, code, parent_id, description, sort_order, 
               is_network_device, can_topology, is_terminal, default_port_count,
               device_icon, device_color, created_at, updated_at, is_deleted
        FROM asset_category 
        {where_clause}
        ORDER BY sort_order, name
        '''
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        categories = []
        for row in rows:
            category = AssetCategory(
                id=row[0], name=row[1], code=row[2], parent_id=row[3],
                description=row[4], sort_order=row[5], is_network_device=row[6],
                can_topology=row[7], is_terminal=row[8], default_port_count=row[9],
                device_icon=row[10], device_color=row[11], created_at=row[12],
                updated_at=row[13], is_deleted=row[14]
            )
            categories.append(category.to_dict())
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取类别列表成功',
            'data': categories
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'获取类别列表失败: {str(e)}'
        }), 500

@category_bp.route('/categories', methods=['POST'])
def create_category():
    """创建新的资产类别"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name') or not data.get('code'):
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '类别名称和编码不能为空'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查编码是否已存在
        cursor.execute('SELECT id FROM asset_category WHERE code = ? AND (is_deleted = 0 OR is_deleted IS NULL)', (data['code'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '类别编码已存在'
            }), 400
        
        # 插入新类别
        now = datetime.now().isoformat()
        insert_sql = '''
        INSERT INTO asset_category (name, code, parent_id, description, sort_order,
                                   is_network_device, can_topology, is_terminal, 
                                   default_port_count, device_icon, device_color,
                                   created_at, updated_at, is_deleted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        cursor.execute(insert_sql, (
            data['name'], data['code'], data.get('parent_id'),
            data.get('description', ''), data.get('sort_order', 0),
            data.get('is_network_device', False), data.get('can_topology', False),
            data.get('is_terminal', False), data.get('default_port_count', 0),
            data.get('device_icon', '📦'), data.get('device_color', '#606266'),
            now, now, False
        ))
        
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '创建类别成功',
            'data': {'id': new_id}
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'创建类别失败: {str(e)}'
        }), 500

@category_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """更新资产类别"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查类别是否存在
        cursor.execute('SELECT id FROM asset_category WHERE id = ?', (category_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '类别不存在'
            }), 404
        
        # 更新类别
        now = datetime.now().isoformat()
        update_sql = '''
        UPDATE asset_category SET 
            name = ?, description = ?, sort_order = ?,
            is_network_device = ?, can_topology = ?, is_terminal = ?,
            default_port_count = ?, device_icon = ?, device_color = ?,
            updated_at = ?
        WHERE id = ?
        '''
        
        cursor.execute(update_sql, (
            data.get('name'), data.get('description', ''), data.get('sort_order', 0),
            data.get('is_network_device', False), data.get('can_topology', False),
            data.get('is_terminal', False), data.get('default_port_count', 0),
            data.get('device_icon', '📦'), data.get('device_color', '#606266'),
            now, category_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '更新类别成功'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'更新类别失败: {str(e)}'
        }), 500

@category_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除资产类别（软删除）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否有资产使用此类别
        cursor.execute('SELECT COUNT(*) FROM it_asset WHERE category = (SELECT name FROM asset_category WHERE id = ?)', (category_id,))
        asset_count = cursor.fetchone()[0]
        
        if asset_count > 0:
            conn.close()
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': f'该类别下还有{asset_count}个资产，无法删除'
            }), 400
        
        # 软删除类别
        now = datetime.now().isoformat()
        cursor.execute('UPDATE asset_category SET is_deleted = 1, updated_at = ? WHERE id = ?', (now, category_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '类别不存在'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '删除类别成功'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'删除类别失败: {str(e)}'
        }), 500

@category_bp.route('/categories/network', methods=['GET'])
def get_network_categories():
    """获取网络设备类别列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT name, code, can_topology, is_terminal, device_icon, device_color
        FROM asset_category 
        WHERE is_network_device = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
        ORDER BY sort_order, name
        ''')
        
        rows = cursor.fetchall()
        categories = []
        for row in rows:
            categories.append({
                'name': row[0],
                'code': row[1],
                'can_topology': bool(row[2]),
                'is_terminal': bool(row[3]),
                'device_icon': row[4],
                'device_color': row[5]
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '获取网络设备类别成功',
            'data': categories
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'获取网络设备类别失败: {str(e)}'
        }), 500