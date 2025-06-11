from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from . import db

class Setting(db.Model):
    """
    نموذج الإعدادات - يخزن إعدادات النظام
    """
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'))

    # العلاقات
    updater = relationship('User', foreign_keys=[updated_by])

    def __init__(self, key, value, description=None, updated_by=None):
        self.key = key
        self.value = value
        self.description = description
        self.updated_by = updated_by

    def to_dict(self):
        """تحويل بيانات الإعدادات إلى قاموس"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }

    def __repr__(self):
        return f'<Setting {self.key}>'
