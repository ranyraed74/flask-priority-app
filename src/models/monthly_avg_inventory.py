from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from . import db

class MonthlyAvgInventory(db.Model):
    """
    نموذج متوسط المخزون الشهري - يخزن متوسط المخزون الشهري لكل منتج
    """
    __tablename__ = 'monthly_avg_inventory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    avg_stock = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    product = relationship('Product', back_populates='monthly_avg_inventory')

    def __init__(self, product_id, month, year, avg_stock):
        self.product_id = product_id
        self.month = month
        self.year = year
        self.avg_stock = avg_stock

    def to_dict(self):
        """تحويل بيانات متوسط المخزون الشهري إلى قاموس"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'month': self.month,
            'year': self.year,
            'avg_stock': float(self.avg_stock),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<MonthlyAvgInventory for Product {self.product_id} ({self.month}/{self.year})>'
