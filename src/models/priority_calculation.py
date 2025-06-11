from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from . import db

class PriorityCalculation(db.Model):
    """
    نموذج حساب الأولويات - يخزن نتائج حساب الأولويات
    """
    __tablename__ = 'priority_calculations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    avg_turnover_factor = Column(DECIMAL(5, 2), nullable=False)
    avg_profit_margin_factor = Column(DECIMAL(5, 2), nullable=False)
    strategic_importance_factor = Column(Integer, nullable=False)
    due_date_factor = Column(DECIMAL(5, 2), nullable=False)
    priority_score = Column(DECIMAL(5, 2), nullable=False)
    priority_category = Column(Enum('critical', 'high', 'medium', 'low', name='priority_categories'), nullable=False)
    calculation_date = Column(Date, nullable=False)
    total_payable = Column(DECIMAL(10, 2), nullable=True, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    supplier = relationship('Supplier', back_populates='priority_calculations')

    def __init__(self, supplier_id, avg_turnover_factor, avg_profit_margin_factor, 
                 strategic_importance_factor, due_date_factor, priority_score, priority_category,
                 total_payable=0, created_by=None):
        self.supplier_id = supplier_id
        self.avg_turnover_factor = avg_turnover_factor
        self.avg_profit_margin_factor = avg_profit_margin_factor
        self.strategic_importance_factor = strategic_importance_factor
        self.due_date_factor = due_date_factor
        self.priority_score = priority_score
        self.priority_category = priority_category
        self.total_payable = total_payable
        self.calculation_date = datetime.utcnow().date()

    def to_dict(self):
        """تحويل بيانات حساب الأولويات إلى قاموس"""
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'avg_turnover_factor': float(self.avg_turnover_factor),
            'avg_profit_margin_factor': float(self.avg_profit_margin_factor),
            'strategic_importance_factor': self.strategic_importance_factor,
            'due_date_factor': float(self.due_date_factor),
            'priority_score': float(self.priority_score),
            'priority_category': self.priority_category,
            'calculation_date': self.calculation_date.isoformat() if self.calculation_date else None,
            'total_payable': float(self.total_payable) if self.total_payable else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<PriorityCalculation for Supplier {self.supplier_id}>'
