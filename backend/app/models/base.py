"""
数据库基础模型类
"""
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime


class BaseModel(db.Model):
    """基础模型类，包含通用字段"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    created_by = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='创建人ID')
    updated_by = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='更新人ID')
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, comment='是否删除')
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        if exclude_fields is None:
            exclude_fields = []
        
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                result[column.name] = value
        return result
    
    def save(self):
        """保存对象"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """软删除"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def hard_delete(self):
        """硬删除"""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_by_id(cls, id):
        """根据ID查找"""
        return cls.query.filter_by(id=id, is_deleted=False).first()
    
    @classmethod
    def find_all(cls):
        """查找所有未删除记录"""
        return cls.query.filter_by(is_deleted=False).all()
    
    @classmethod
    def paginate(cls, page=1, per_page=20, **filters):
        """分页查询"""
        query = cls.query.filter_by(is_deleted=False)
        
        # 添加过滤条件
        for key, value in filters.items():
            if hasattr(cls, key) and value is not None:
                if isinstance(value, str) and value:
                    # 字符串模糊查询
                    query = query.filter(getattr(cls, key).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(cls, key) == value)
        
        return query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )