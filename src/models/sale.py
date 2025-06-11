from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date, DateTime
from sqlalchemy.orm import relationship
from . import db

class Sale(db.Model):
    """
    نموذج المبيعات - يخزن بيانات المبيعات
    """
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    sale_value = Column(DECIMAL(10, 2), nullable=False)
    sale_date = Column(Date, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))

    # العلاقات
    product = relationship('Product', back_populates='sales')
    creator = relationship('User', foreign_keys=[created_by])

    def __init__(self, product_id, quantity, sale_value, sale_date, created_by=None):
        self.product_id = product_id
        self.quantity = quantity
        self.sale_value = sale_value
        self.sale_date = sale_date
        self.month = sale_date.month
        self.year = sale_date.year
        self.created_by = created_by

    def to_dict(self):
        """تحويل بيانات المبيعات إلى قاموس"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'sale_value': float(self.sale_value),
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'month': self.month,
            'year': self.year,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Sale {self.id} for Product {self.product_id}>'
