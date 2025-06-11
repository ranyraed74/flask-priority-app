from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DECIMAL, Boolean, DateTime
from sqlalchemy.orm import relationship
from . import db

class Product(db.Model):
    """
    نموذج المنتج - يخزن بيانات المنتجات
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    category = Column(String(50), nullable=False)
    purchase_price = Column(DECIMAL(10, 2), nullable=False)
    selling_price = Column(DECIMAL(10, 2), nullable=False)
    is_seasonal = Column(Boolean, default=False)
    season = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))

    # العلاقات
    supplier = relationship('Supplier', back_populates='products')
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])
    inventory = relationship('Inventory', back_populates='product', uselist=False)
    sales = relationship('Sale', back_populates='product')
    monthly_avg_inventory = relationship('MonthlyAvgInventory', back_populates='product')

    def __init__(self, code, name, supplier_id, category, purchase_price, selling_price,
                 is_seasonal=False, season=None, notes=None, created_by=None):
        self.code = code
        self.name = name
        self.supplier_id = supplier_id
        self.category = category
        self.purchase_price = purchase_price
        self.selling_price = selling_price
        self.is_seasonal = is_seasonal
        self.season = season
        self.notes = notes
        self.created_by = created_by
        self.updated_by = created_by

    def calculate_profit_margin(self):
        """حساب هامش الربح"""
        if float(self.selling_price) == 0:
            return 0
        return ((float(self.selling_price) - float(self.purchase_price)) / float(self.selling_price)) * 100

    def calculate_profit_margin_factor(self):
        """حساب معامل هامش الربح (1-10)"""
        profit_margin = self.calculate_profit_margin()
        if profit_margin >= 30:
            return 10
        elif profit_margin >= 25:
            return 9
        elif profit_margin >= 20:
            return 8
        elif profit_margin >= 15:
            return 7
        elif profit_margin >= 10:
            return 6
        elif profit_margin >= 8:
            return 5
        elif profit_margin >= 6:
            return 4
        elif profit_margin >= 4:
            return 3
        elif profit_margin >= 2:
            return 2
        elif profit_margin > 0:
            return 1
        return 0

    def to_dict(self):
        """تحويل بيانات المنتج إلى قاموس"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'category': self.category,
            'purchase_price': float(self.purchase_price),
            'selling_price': float(self.selling_price),
            'profit_margin': self.calculate_profit_margin(),
            'profit_margin_factor': self.calculate_profit_margin_factor(),
            'is_seasonal': self.is_seasonal,
            'season': self.season,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Product {self.name}>'
