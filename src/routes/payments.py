from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.suggested_payment import SuggestedPayment
from src.models.supplier import Supplier
from src.utils.priority_calculator import PriorityCalculator

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route('/')
@login_required
def index():
    """صفحة قائمة المدفوعات المقترحة"""
    payments = SuggestedPayment.query.all()
    return render_template('payments/index.html', payments=payments)

@payments_bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    """إعادة حساب المدفوعات المقترحة"""
    calculator = PriorityCalculator()
    calculator.calculate_suggested_payments(current_user.id)
    
    flash('تم إعادة حساب المدفوعات المقترحة بنجاح', 'success')
    return redirect(url_for('payments.index'))

@payments_bp.route('/view/<int:id>')
@login_required
def view(id):
    """عرض تفاصيل المدفوعات المقترحة"""
    payment = SuggestedPayment.query.get_or_404(id)
    return render_template('payments/view.html', payment=payment)

@payments_bp.route('/approve/<int:id>', methods=['POST'])
@login_required
def approve(id):
    """اعتماد مدفوعات مقترحة"""
    payment = SuggestedPayment.query.get_or_404(id)
    
    # تحديث حالة المدفوعات المقترحة
    payment.status = 'approved'
    payment.approved_by = current_user.id
    payment.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('تم اعتماد المدفوعات المقترحة بنجاح', 'success')
    return redirect(url_for('payments.index'))

@payments_bp.route('/reject/<int:id>', methods=['POST'])
@login_required
def reject(id):
    """رفض مدفوعات مقترحة"""
    payment = SuggestedPayment.query.get_or_404(id)
    
    # تحديث حالة المدفوعات المقترحة
    payment.status = 'rejected'
    payment.approved_by = current_user.id
    payment.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('تم رفض المدفوعات المقترحة بنجاح', 'success')
    return redirect(url_for('payments.index'))
