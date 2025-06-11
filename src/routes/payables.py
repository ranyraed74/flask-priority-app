from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.payable import Payable
from src.models.supplier import Supplier
from src.models.suggested_payment import SuggestedPayment

payables_bp = Blueprint('payables', __name__, url_prefix='/payables')

@payables_bp.route('/')
@login_required
def index():
    """صفحة قائمة المستحقات"""
    payables = Payable.query.all()
    return render_template('payables/index.html', payables=payables)

@payables_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """إضافة مستحق جديد"""
    suppliers = Supplier.query.all()
    
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        invoice_number = request.form.get('invoice_number')
        invoice_date = request.form.get('invoice_date')
        due_date = request.form.get('due_date')
        amount = request.form.get('amount')
        paid_amount = request.form.get('paid_amount', 0)
        status = 'paid' if float(paid_amount) >= float(amount) else 'partial' if float(paid_amount) > 0 else 'pending'
        notes = request.form.get('notes')
        
        # إنشاء مستحق جديد
        payable = Payable(
            supplier_id=supplier_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            amount=amount,
            paid_amount=paid_amount,
            status=status,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(payable)
        db.session.commit()
        
        flash('تم إضافة المستحق بنجاح', 'success')
        return redirect(url_for('payables.index'))
    
    return render_template('payables/add.html', suppliers=suppliers)

@payables_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل مستحق"""
    payable = Payable.query.get_or_404(id)
    suppliers = Supplier.query.all()
    
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        invoice_number = request.form.get('invoice_number')
        invoice_date = request.form.get('invoice_date')
        due_date = request.form.get('due_date')
        amount = request.form.get('amount')
        paid_amount = request.form.get('paid_amount', 0)
        status = 'paid' if float(paid_amount) >= float(amount) else 'partial' if float(paid_amount) > 0 else 'pending'
        notes = request.form.get('notes')
        
        # تحديث المستحق
        payable.supplier_id = supplier_id
        payable.invoice_number = invoice_number
        payable.invoice_date = invoice_date
        payable.due_date = due_date
        payable.amount = amount
        payable.paid_amount = paid_amount
        payable.status = status
        payable.notes = notes
        payable.updated_by = current_user.id
        
        db.session.commit()
        
        flash('تم تحديث المستحق بنجاح', 'success')
        return redirect(url_for('payables.index'))
    
    return render_template('payables/edit.html', payable=payable, suppliers=suppliers)

@payables_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """حذف مستحق"""
    payable = Payable.query.get_or_404(id)
    
    db.session.delete(payable)
    db.session.commit()
    
    flash('تم حذف المستحق بنجاح', 'success')
    return redirect(url_for('payables.index'))

@payables_bp.route('/view/<int:id>')
@login_required
def view(id):
    """عرض تفاصيل المستحق"""
    payable = Payable.query.get_or_404(id)
    return render_template('payables/view.html', payable=payable)

@payables_bp.route('/pay/<int:id>', methods=['GET', 'POST'])
@login_required
def pay(id):
    """تسديد مستحق"""
    payable = Payable.query.get_or_404(id)
    
    if request.method == 'POST':
        payment_amount = float(request.form.get('payment_amount', 0))
        
        # التحقق من صحة المبلغ
        if payment_amount <= 0:
            flash('يجب أن يكون مبلغ السداد أكبر من صفر', 'danger')
            return redirect(url_for('payables.pay', id=id))
        
        if payment_amount > (float(payable.amount) - float(payable.paid_amount)):
            flash('مبلغ السداد أكبر من المبلغ المتبقي', 'danger')
            return redirect(url_for('payables.pay', id=id))
        
        # تحديث المستحق
        payable.paid_amount = float(payable.paid_amount) + payment_amount
        payable.status = 'paid' if float(payable.paid_amount) >= float(payable.amount) else 'partial'
        payable.updated_by = current_user.id
        
        db.session.commit()
        
        flash('تم تسديد المستحق بنجاح', 'success')
        return redirect(url_for('payables.index'))
    
    return render_template('payables/pay.html', payable=payable)
