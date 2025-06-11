from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.sale import Sale
from src.models.product import Product
from datetime import datetime

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/')
@login_required
def index():
    """صفحة قائمة المبيعات"""
    sales = Sale.query.all()
    return render_template('sales/index.html', sales=sales)

@sales_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """إضافة مبيعات جديدة"""
    products = Product.query.all()
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        sale_value = request.form.get('sale_value')
        sale_date = request.form.get('sale_date')
        
        # إنشاء مبيعات جديدة
        sale = Sale(
            product_id=product_id,
            quantity=quantity,
            sale_value=sale_value,
            sale_date=datetime.strptime(sale_date, '%Y-%m-%d').date(),
            created_by=current_user.id
        )
        
        db.session.add(sale)
        db.session.commit()
        
        flash('تم إضافة المبيعات بنجاح', 'success')
        return redirect(url_for('sales.index'))
    
    return render_template('sales/add.html', products=products)

@sales_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل مبيعات"""
    sale = Sale.query.get_or_404(id)
    products = Product.query.all()
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        sale_value = request.form.get('sale_value')
        sale_date = request.form.get('sale_date')
        
        # تحديث المبيعات
        sale.product_id = product_id
        sale.quantity = quantity
        sale.sale_value = sale_value
        sale.sale_date = datetime.strptime(sale_date, '%Y-%m-%d').date()
        sale.month = sale.sale_date.month
        sale.year = sale.sale_date.year
        
        db.session.commit()
        
        flash('تم تحديث المبيعات بنجاح', 'success')
        return redirect(url_for('sales.index'))
    
    return render_template('sales/edit.html', sale=sale, products=products)

@sales_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """حذف مبيعات"""
    sale = Sale.query.get_or_404(id)
    
    db.session.delete(sale)
    db.session.commit()
    
    flash('تم حذف المبيعات بنجاح', 'success')
    return redirect(url_for('sales.index'))

@sales_bp.route('/view/<int:id>')
@login_required
def view(id):
    """عرض تفاصيل المبيعات"""
    sale = Sale.query.get_or_404(id)
    return render_template('sales/view.html', sale=sale)
