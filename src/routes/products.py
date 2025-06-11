from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.product import Product
from src.models.supplier import Supplier
from src.models.inventory import Inventory

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
@login_required
def index():
    """صفحة قائمة المنتجات"""
    products = Product.query.all()
    return render_template('products/index.html', products=products)

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """إضافة منتج جديد"""
    suppliers = Supplier.query.all()
    
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        supplier_id = request.form.get('supplier_id')
        category = request.form.get('category')
        purchase_price = request.form.get('purchase_price')
        selling_price = request.form.get('selling_price')
        is_seasonal = True if request.form.get('is_seasonal') else False
        season = request.form.get('season')
        notes = request.form.get('notes')
        
        # التحقق من عدم تكرار الكود
        existing_product = Product.query.filter_by(code=code).first()
        if existing_product:
            flash('كود المنتج موجود بالفعل', 'danger')
            return redirect(url_for('products.add'))
        
        # إنشاء منتج جديد
        product = Product(
            code=code,
            name=name,
            supplier_id=supplier_id,
            category=category,
            purchase_price=purchase_price,
            selling_price=selling_price,
            is_seasonal=is_seasonal,
            season=season,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        # إنشاء مخزون للمنتج
        inventory = Inventory(
            product_id=product.id,
            current_stock=0,
            min_stock=0,
            max_stock=0,
            updated_by=current_user.id
        )
        
        db.session.add(inventory)
        db.session.commit()
        
        flash('تم إضافة المنتج بنجاح', 'success')
        return redirect(url_for('products.index'))
    
    return render_template('products/add.html', suppliers=suppliers)

@products_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل منتج"""
    product = Product.query.get_or_404(id)
    suppliers = Supplier.query.all()
    
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        supplier_id = request.form.get('supplier_id')
        category = request.form.get('category')
        purchase_price = request.form.get('purchase_price')
        selling_price = request.form.get('selling_price')
        is_seasonal = True if request.form.get('is_seasonal') else False
        season = request.form.get('season')
        notes = request.form.get('notes')
        
        # التحقق من عدم تكرار الكود
        existing_product = Product.query.filter_by(code=code).first()
        if existing_product and existing_product.id != id:
            flash('كود المنتج موجود بالفعل', 'danger')
            return redirect(url_for('products.edit', id=id))
        
        # تحديث المنتج
        product.code = code
        product.name = name
        product.supplier_id = supplier_id
        product.category = category
        product.purchase_price = purchase_price
        product.selling_price = selling_price
        product.is_seasonal = is_seasonal
        product.season = season
        product.notes = notes
        product.updated_by = current_user.id
        
        db.session.commit()
        
        flash('تم تحديث المنتج بنجاح', 'success')
        return redirect(url_for('products.index'))
    
    return render_template('products/edit.html', product=product, suppliers=suppliers)

@products_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """حذف منتج"""
    product = Product.query.get_or_404(id)
    
    # التحقق من عدم وجود مبيعات مرتبطة بالمنتج
    if product.sales:
        flash('لا يمكن حذف المنتج لوجود مبيعات مرتبطة به', 'danger')
        return redirect(url_for('products.index'))
    
    # حذف المخزون المرتبط بالمنتج
    if product.inventory:
        db.session.delete(product.inventory)
    
    # حذف متوسط المخزون الشهري المرتبط بالمنتج
    for avg_inventory in product.monthly_avg_inventory:
        db.session.delete(avg_inventory)
    
    db.session.delete(product)
    db.session.commit()
    
    flash('تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/view/<int:id>')
@login_required
def view(id):
    """عرض تفاصيل المنتج"""
    product = Product.query.get_or_404(id)
    return render_template('products/view.html', product=product)
