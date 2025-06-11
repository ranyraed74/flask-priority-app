from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    """
    نموذج المستخدم - يخزن بيانات المستخدمين وصلاحياتهم
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum('admin', 'accountant', 'data_entry', name='user_roles'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __init__(self, username, email, full_name, role, password=None):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role
        if password:
            self.set_password(password)

    def set_password(self, password):
        """تعيين كلمة المرور المشفرة"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """تحديث تاريخ آخر تسجيل دخول"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def is_admin(self):
        """التحقق مما إذا كان المستخدم مديراً"""
        return self.role == 'admin'

    def is_accountant(self):
        """التحقق مما إذا كان المستخدم محاسباً"""
        return self.role == 'accountant'

    def is_data_entry(self):
        """التحقق مما إذا كان المستخدم مدخل بيانات"""
        return self.role == 'data_entry'

    def get_id(self):
        """إرجاع معرف المستخدم كنص - مطلوب لـ Flask-Login"""
        return str(self.id)

    def to_dict(self):
        """تحويل بيانات المستخدم إلى قاموس"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.username}>'
