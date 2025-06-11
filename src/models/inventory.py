from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date, DateTime
from sqlalchemy.orm import relationship
from . import db

class Inventory(db.Model):
    """
    نموذج المخزون - يخزن بيانات المخزون الحالي
    """
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, unique=True)
    current_stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=0)
    max_stock = Column(Integer, nullable=False, default=0)
    last_stock_update = Column(Date, nullable=False, default=datetime.utcnow().date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'))

    # العلاقات
    product = relationship('Product', back_populates='inventory')
    updater = relationship('User', foreign_keys=[updated_by])

    def __init__(self, product_id, current_stock, min_stock, max_stock, updated_by=None):
        self.product_id = product_id
        self.current_stock = current_stock
        self.min_stock = min_stock
        self.max_stock = max_stock
        self.last_stock_update = datetime.utcnow().date()
        self.updated_by = updated_by

    def is_low_stock(self):
        """التحقق مما إذا كان المخزون منخفضاً"""
        return self.current_stock <= self.min_stock

    def is_over_stock(self):
        """التحقق مما إذا كان المخزون زائداً"""
        return self.current_stock >= self.max_stock

    def to_dict(self):
        """تحويل بيانات المخزون إلى قاموس"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'current_stock': self.current_stock,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'last_stock_update': self.last_stock_update.isoformat() if self.last_stock_update else None,
            'is_low_stock': self.is_low_stock(),
            'is_over_stock': self.is_over_stock(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Inventory for Product {self.product_id}>'
