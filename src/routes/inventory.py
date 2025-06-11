from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.inventory import Inventory
from src.models.product import Product

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
def index():
    """صفحة قائمة المخزون"""
    inventory_items = Inventory.query.all()
    return render_template('inventory/index.html', inventory_items=inventory_items)

@inventory_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    """تحديث المخزون"""
    inventory = Inventory.query.get_or_404(id)
    product = Product.query.get(inventory.product_id)
    
    if request.method == 'POST':
        current_stock = request.form.get('current_stock')
        min_stock = request.form.get('min_stock')
        max_stock = request.form.get('max_stock')
        
        # تحديث المخزون
        inventory.current_stock = current_stock
        inventory.min_stock = min_stock
        inventory.max_stock = max_stock
        inventory.updated_by = current_user.id
        
        db.session.commit()
        
        flash('تم تحديث المخزون بنجاح', 'success')
        return redirect(url_for('inventory.index'))
    
    return render_template('inventory/update.html', inventory=inventory, product=product)

@inventory_bp.route('/low_stock')
@login_required
def low_stock():
    """صفحة المخزون المنخفض"""
    low_stock_items = []
    inventory_items = Inventory.query.all()
    
    for item in inventory_items:
        if item.is_low_stock():
            low_stock_items.append(item)
    
    return render_template('inventory/low_stock.html', low_stock_items=low_stock_items)

@inventory_bp.route('/over_stock')
@login_required
def over_stock():
    """صفحة المخزون الزائد"""
    over_stock_items = []
    inventory_items = Inventory.query.all()
    
    for item in inventory_items:
        if item.is_over_stock():
            over_stock_items.append(item)
    
    return render_template('inventory/over_stock.html', over_stock_items=over_stock_items)
