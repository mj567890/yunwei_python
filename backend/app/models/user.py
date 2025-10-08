"""
用户和权限模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.base import BaseModel
from app.utils.encryption import PartialEncryptedType, mask_sensitive_data


# 用户角色关联表
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('sys_user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('sys_role.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# 角色权限关联表
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('sys_role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('sys_permission.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class User(BaseModel):
    """用户模型"""
    __tablename__ = 'sys_user'
    
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(128), nullable=False, comment='密码哈希')
    email = db.Column(PartialEncryptedType, unique=True, nullable=True, comment='邮箱')
    phone = db.Column(PartialEncryptedType, nullable=True, comment='手机号')
    real_name = db.Column(db.String(50), nullable=True, comment='真实姓名')
    avatar = db.Column(db.String(255), nullable=True, comment='头像路径')
    status = db.Column(db.Integer, default=1, nullable=False, comment='状态：0-禁用，1-启用')
    login_count = db.Column(db.Integer, default=0, comment='登录次数')
    last_login_at = db.Column(db.DateTime, nullable=True, comment='最后登录时间')
    last_login_ip = db.Column(db.String(45), nullable=True, comment='最后登录IP')
    failed_login_count = db.Column(db.Integer, default=0, comment='失败登录次数')
    locked_until = db.Column(db.DateTime, nullable=True, comment='锁定到期时间')
    
    # 关联关系
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_active(self):
        """是否激活"""
        return self.status == 1 and not self.is_locked()
    
    def is_locked(self):
        """是否被锁定"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def lock_account(self, minutes=30):
        """锁定账户"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.save()
    
    def unlock_account(self):
        """解锁账户"""
        self.locked_until = None
        self.failed_login_count = 0
        self.save()
    
    def has_permission(self, permission_code):
        """检查是否有某个权限"""
        for role in self.roles:
            if role.has_permission(permission_code):
                return True
        return False
    
    def has_role(self, role_name):
        """检查是否有某个角色"""
        return any(role.name == role_name for role in self.roles)
    
    def to_dict(self, exclude_fields=None, mask_sensitive=True):
        """转换为字典"""
        if exclude_fields is None:
            exclude_fields = ['password_hash']
        else:
            exclude_fields.append('password_hash')
        
        result = super().to_dict(exclude_fields)
        result['roles'] = [role.to_dict() for role in self.roles]
        result['is_locked'] = self.is_locked()
        
        # 敏感数据掩码处理
        if mask_sensitive:
            if 'email' in result and result['email']:
                result['email_masked'] = mask_sensitive_data(result['email'], visible_start=2, visible_end=0)
            if 'phone' in result and result['phone']:
                result['phone_masked'] = mask_sensitive_data(result['phone'], visible_start=3, visible_end=4)
        
        return result


class Role(BaseModel):
    """角色模型"""
    __tablename__ = 'sys_role'
    
    name = db.Column(db.String(50), unique=True, nullable=False, comment='角色名称')
    code = db.Column(db.String(50), unique=True, nullable=False, comment='角色编码')
    description = db.Column(db.String(255), nullable=True, comment='角色描述')
    status = db.Column(db.Integer, default=1, nullable=False, comment='状态：0-禁用，1-启用')
    
    # 关联关系
    users = db.relationship('User', secondary=user_roles, back_populates='roles')
    permissions = db.relationship('Permission', secondary=role_permissions, back_populates='roles')
    
    def has_permission(self, permission_code):
        """检查是否有某个权限"""
        return any(perm.code == permission_code for perm in self.permissions)
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        result['permissions'] = [perm.to_dict() for perm in self.permissions]
        return result


class Permission(BaseModel):
    """权限模型"""
    __tablename__ = 'sys_permission'
    
    name = db.Column(db.String(50), nullable=False, comment='权限名称')
    code = db.Column(db.String(50), unique=True, nullable=False, comment='权限编码')
    description = db.Column(db.String(255), nullable=True, comment='权限描述')
    resource = db.Column(db.String(100), nullable=True, comment='资源标识')
    action = db.Column(db.String(50), nullable=True, comment='操作类型')
    
    # 关联关系
    roles = db.relationship('Role', secondary=role_permissions, back_populates='permissions')


class OperationLog(BaseModel):
    """操作日志模型"""
    __tablename__ = 'operation_log'
    
    user_id = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=False, comment='操作用户ID')
    username = db.Column(db.String(50), nullable=False, comment='用户名')
    operation = db.Column(db.String(100), nullable=False, comment='操作类型')
    method = db.Column(db.String(10), nullable=False, comment='请求方法')
    url = db.Column(db.String(255), nullable=False, comment='请求URL')
    ip = db.Column(db.String(45), nullable=True, comment='IP地址')
    user_agent = db.Column(db.Text, nullable=True, comment='用户代理')
    request_data = db.Column(db.Text, nullable=True, comment='请求数据')
    response_data = db.Column(db.Text, nullable=True, comment='响应数据')
    status_code = db.Column(db.Integer, nullable=True, comment='响应状态码')
    duration = db.Column(db.Integer, nullable=True, comment='执行时长(ms)')
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('operation_logs', lazy='dynamic'))