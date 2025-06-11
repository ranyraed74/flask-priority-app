from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from src.models.user import db
import os
import csv
import json
from datetime import datetime
from werkzeug.utils import secure_filename

import_export_bp = Blueprint('import_export', __name__, url_prefix='/import_export')

@import_export_bp.route('/')
@login_required
def index():
    """صفحة الاستيراد والتصدير الرئيسية"""
    return render_template('import_export/index.html')

@import_export_bp.route('/export_suppliers')
@login_required
def export_suppliers():
    """تصدير بيانات الموردين"""
    from src.models.supplier import Supplier
    
    suppliers = Supplier.query.all()
    
    # إنشاء ملف CSV
    filename = f'suppliers_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['id', 'code', 'name', 'phone', 'email', 'address', 'start_date', 'payment_terms', 'strategic_importance', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for supplier in suppliers:
            writer.writerow({
                'id': supplier.id,
                'code': supplier.code,
                'name': supplier.name,
                'phone': supplier.phone,
                'email': supplier.email,
                'address': supplier.address,
                'start_date': supplier.start_date.isoformat() if supplier.start_date else '',
                'payment_terms': supplier.payment_terms,
                'strategic_importance': supplier.strategic_importance,
                'notes': supplier.notes
            })
    
    return send_file(filepath, as_attachment=True)

@import_export_bp.route('/export_products')
@login_required
def export_products():
    """تصدير بيانات المنتجات"""
    from src.models.product import Product
    
    products = Product.query.all()
    
    # إنشاء ملف CSV
    filename = f'products_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['id', 'code', 'name', 'supplier_id', 'category', 'purchase_price', 'selling_price', 'is_seasonal', 'season', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for product in products:
            writer.writerow({
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'supplier_id': product.supplier_id,
                'category': product.category,
                'purchase_price': float(product.purchase_price),
                'selling_price': float(product.selling_price),
                'is_seasonal': product.is_seasonal,
                'season': product.season,
                'notes': product.notes
            })
    
    return send_file(filepath, as_attachment=True)

@import_export_bp.route('/import_suppliers', methods=['POST'])
@login_required
def import_suppliers():
    """استيراد بيانات الموردين"""
    from src.models.supplier import Supplier
    
    if 'file' not in request.files:
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('import_export.index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('import_export.index'))
    
    if not file.filename.endswith('.csv'):
        flash('يجب اختيار ملف CSV', 'danger')
        return redirect(url_for('import_export.index'))
    
    # حفظ الملف
    filename = secure_filename(file.filename)
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', filename)
    file.save(filepath)
    
    # قراءة الملف
    with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # التحقق من وجود المورد
            supplier = Supplier.query.filter_by(code=row['code']).first()
            
            if supplier:
                # تحديث المورد
                supplier.name = row['name']
                supplier.phone = row['phone']
                supplier.email = row['email']
                supplier.address = row['address']
                supplier.start_date = datetime.strptime(row['start_date'], '%Y-%m-%d').date() if row['start_date'] else None
                supplier.payment_terms = int(row['payment_terms'])
                supplier.strategic_importance = int(row['strategic_importance'])
                supplier.notes = row['notes']
                supplier.updated_by = current_user.id
            else:
                # إنشاء مورد جديد
                supplier = Supplier(
                    code=row['code'],
                    name=row['name'],
                    phone=row['phone'],
                    email=row['email'],
                    address=row['address'],
                    start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date() if row['start_date'] else None,
                    payment_terms=int(row['payment_terms']),
                    strategic_importance=int(row['strategic_importance']),
                    notes=row['notes'],
                    created_by=current_user.id
                )
                db.session.add(supplier)
        
        db.session.commit()
    
    flash('تم استيراد بيانات الموردين بنجاح', 'success')
    return redirect(url_for('import_export.index'))

@import_export_bp.route('/import_products', methods=['POST'])
@login_required
def import_products():
    """استيراد بيانات المنتجات"""
    from src.models.product import Product
    
    if 'file' not in request.files:
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('import_export.index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('import_export.index'))
    
    if not file.filename.endswith('.csv'):
        flash('يجب اختيار ملف CSV', 'danger')
        return redirect(url_for('import_export.index'))
    
    # حفظ الملف
    filename = secure_filename(file.filename)
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', filename)
    file.save(filepath)
    
    # قراءة الملف
    with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # التحقق من وجود المنتج
            product = Product.query.filter_by(code=row['code']).first()
            
            if product:
                # تحديث المنتج
                product.name = row['name']
                product.supplier_id = int(row['supplier_id'])
                product.category = row['category']
                product.purchase_price = float(row['purchase_price'])
                product.selling_price = float(row['selling_price'])
                product.is_seasonal = row['is_seasonal'].lower() in ['true', '1', 'yes']
                product.season = row['season']
                product.notes = row['notes']
                product.updated_by = current_user.id
            else:
                # إنشاء منتج جديد
                product = Product(
                    code=row['code'],
                    name=row['name'],
                    supplier_id=int(row['supplier_id']),
                    category=row['category'],
                    purchase_price=float(row['purchase_price']),
                    selling_price=float(row['selling_price']),
                    is_seasonal=row['is_seasonal'].lower() in ['true', '1', 'yes'],
                    season=row['season'],
                    notes=row['notes'],
                    created_by=current_user.id
                )
                db.session.add(product)
        
        db.session.commit()
    
    flash('تم استيراد بيانات المنتجات بنجاح', 'success')
    return redirect(url_for('import_export.index'))
