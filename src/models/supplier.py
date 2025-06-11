from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from . import db

class Supplier(db.Model):
    """
    نموذج المورد - يخزن بيانات الموردين
    """
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    payment_terms = Column(Integer, nullable=False)  # شروط السداد بالأيام
    strategic_importance = Column(Integer, nullable=False)  # الأهمية الاستراتيجية (1-10)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))

    # العلاقات
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])
    products = relationship('Product', back_populates='supplier')
    payables = relationship('Payable', back_populates='supplier')
    priority_calculations = relationship('PriorityCalculation', back_populates='supplier')
    suggested_payments = relationship('SuggestedPayment', back_populates='supplier')

    def __init__(self, code, name, start_date, payment_terms, strategic_importance, 
                 phone=None, email=None, address=None, notes=None, created_by=None):
        self.code = code
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.start_date = start_date
        self.payment_terms = payment_terms
        self.strategic_importance = strategic_importance
        self.notes = notes
        self.created_by = created_by
        self.updated_by = created_by

    def to_dict(self):
        """تحويل بيانات المورد إلى قاموس"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'payment_terms': self.payment_terms,
            'strategic_importance': self.strategic_importance,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Supplier {self.name}>'
