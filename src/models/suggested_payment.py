from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from . import db

class SuggestedPayment(db.Model):
    """
    نموذج خطة السداد المقترحة - يخزن خطة السداد المقترحة
    """
    __tablename__ = 'suggested_payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    total_due = Column(DECIMAL(10, 2), nullable=False)
    priority_score = Column(DECIMAL(5, 2), nullable=False)
    priority_category = Column(Enum('critical', 'high', 'medium', 'low', name='priority_categories'), nullable=False)
    suggested_amount = Column(DECIMAL(10, 2), nullable=False)
    percentage_of_total = Column(DECIMAL(5, 2), nullable=False)
    suggested_payment_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(Enum('pending', 'approved', 'rejected', 'paid', name='payment_plan_status'), nullable=False, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))

    # العلاقات
    supplier = relationship('Supplier', back_populates='suggested_payments')
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])

    def __init__(self, supplier_id, total_due, priority_score, priority_category, 
                 suggested_amount, percentage_of_total, suggested_payment_date, 
                 notes=None, created_by=None):
        self.supplier_id = supplier_id
        self.total_due = total_due
        self.priority_score = priority_score
        self.priority_category = priority_category
        self.suggested_amount = suggested_amount
        self.percentage_of_total = percentage_of_total
        self.suggested_payment_date = suggested_payment_date
        self.notes = notes
        self.status = 'pending'
        self.created_by = created_by
        self.updated_by = created_by

    def to_dict(self):
        """تحويل بيانات خطة السداد المقترحة إلى قاموس"""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'total_due': float(self.total_due),
            'priority_score': float(self.priority_score),
            'priority_category': self.priority_category,
            'suggested_amount': float(self.suggested_amount),
            'percentage_of_total': float(self.percentage_of_total),
            'suggested_payment_date': self.suggested_payment_date.isoformat() if self.suggested_payment_date else None,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<SuggestedPayment for Supplier {self.supplier_id}>'
