from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from . import db

class Payable(db.Model):
    """
    نموذج المستحقات - يخزن بيانات المستحقات للموردين
    """
    __tablename__ = 'payables'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum('pending', 'partial', 'paid', name='payment_status'), nullable=False, default='pending')
    paid_amount = Column(DECIMAL(10, 2), nullable=False, default=0)
    payment_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))

    # العلاقات
    supplier = relationship('Supplier', back_populates='payables')
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])

    def __init__(self, supplier_id, amount, due_date, description=None, created_by=None):
        self.supplier_id = supplier_id
        self.amount = amount
        self.due_date = due_date
        self.description = description
        self.status = 'pending'
        self.paid_amount = 0
        self.created_by = created_by
        self.updated_by = created_by

    def calculate_remaining_amount(self):
        """حساب المبلغ المتبقي"""
        return float(self.amount) - float(self.paid_amount)

    def calculate_days_until_due(self):
        """حساب عدد الأيام حتى تاريخ الاستحقاق"""
        if self.due_date:
            today = datetime.utcnow().date()
            return (self.due_date - today).days
        return 0

    def calculate_due_date_factor(self):
        """حساب معامل تاريخ الاستحقاق (1-10)"""
        days = self.calculate_days_until_due()
        if days <= 0:
            return 10
        elif days <= 7:
            return 9
        elif days <= 14:
            return 8
        elif days <= 21:
            return 7
        elif days <= 30:
            return 6
        elif days <= 45:
            return 5
        elif days <= 60:
            return 4
        elif days <= 90:
            return 3
        elif days <= 120:
            return 2
        return 1

    def update_payment(self, paid_amount, payment_date=None):
        """تحديث المبلغ المدفوع وحالة السداد"""
        self.paid_amount = paid_amount
        if payment_date:
            self.payment_date = payment_date
        else:
            self.payment_date = datetime.utcnow().date()

        if float(self.paid_amount) >= float(self.amount):
            self.status = 'paid'
        elif float(self.paid_amount) > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'

    def to_dict(self):
        """تحويل بيانات المستحقات إلى قاموس"""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'amount': float(self.amount),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'description': self.description,
            'status': self.status,
            'paid_amount': float(self.paid_amount),
            'remaining_amount': self.calculate_remaining_amount(),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'days_until_due': self.calculate_days_until_due(),
            'due_date_factor': self.calculate_due_date_factor(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Payable {self.id} for Supplier {self.supplier_id}>'
