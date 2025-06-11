from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.supplier import Supplier

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

@suppliers_bp.route('/')
@login_required
def index():
    """صفحة قائمة الموردين"""
    suppliers = Supplier.query.all()
    return render_template('suppliers/index.html', suppliers=suppliers)

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """إضافة مورد جديد"""
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        start_date = request.form.get('start_date')
        payment_terms = request.form.get('payment_terms')
        strategic_importance = request.form.get('strategic_importance')
        notes = request.form.get('notes')
        
        # التحقق من عدم تكرار الكود
        existing_supplier = Supplier.query.filter_by(code=code).first()
        if existing_supplier:
            flash('كود المورد موجود بالفعل', 'danger')
            return redirect(url_for('suppliers.add'))
        
        # إنشاء مورد جديد
        supplier = Supplier(
            code=code,
            name=name,
            phone=phone,
            email=email,
            address=address,
            start_date=start_date,
            payment_terms=payment_terms,
            strategic_importance=strategic_importance,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        flash('تم إضافة المورد بنجاح', 'success')
        return redirect(url_for('suppliers.index'))
    
    return render_template('suppliers/add.html')

@suppliers_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل مورد"""
    supplier = Supplier.query.get_or_404(id)
    
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        start_date = request.form.get('start_date')
        payment_terms = request.form.get('payment_terms')
        strategic_importance = request.form.get('strategic_importance')
        notes = request.form.get('notes')
        
        # التحقق من عدم تكرار الكود
        existing_supplier = Supplier.query.filter_by(code=code).first()
        if existing_supplier and existing_supplier.id != id:
            flash('كود المورد موجود بالفعل', 'danger')
            return redirect(url_for('suppliers.edit', id=id))
        
        # تحديث المورد
        supplier.code = code
        supplier.name = name
        supplier.phone = phone
        supplier.email = email
        supplier.address = address
        supplier.start_date = start_date
        supplier.payment_terms = payment_terms
        supplier.strategic_importance = strategic_importance
        supplier.notes = notes
        supplier.updated_by = current_user.id
        
        db.session.commit()
        
        flash('تم تحديث المورد بنجاح', 'success')
        return redirect(url_for('suppliers.index'))
    
    return render_template('suppliers/edit.html', supplier=supplier)

@suppliers_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """حذف مورد"""
    supplier = Supplier.query.get_or_404(id)
    
    # التحقق من عدم وجود منتجات أو مستحقات مرتبطة بالمورد
    if supplier.products or supplier.payables:
        flash('لا يمكن حذف المورد لوجود منتجات أو مستحقات مرتبطة به', 'danger')
        return redirect(url_for('suppliers.index'))
    
    db.session.delete(supplier)
    db.session.commit()
    
    flash('تم حذف المورد بنجاح', 'success')
    return redirect(url_for('suppliers.index'))

@suppliers_bp.route('/view/<int:id>')
@login_required
def view(id):
    """عرض تفاصيل المورد"""
    supplier = Supplier.query.get_or_404(id)
    return render_template('suppliers/view.html', supplier=supplier)
