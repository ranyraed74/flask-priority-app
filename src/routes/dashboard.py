from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models.user import db
from src.utils.priority_calculator import PriorityCalculator

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """صفحة لوحة التحكم الرئيسية"""
    # الحصول على إحصائيات الأولويات
    calculator = PriorityCalculator()
    priority_stats = calculator.get_priority_statistics()
    
    # إحصائيات إضافية
    from src.models.supplier import Supplier
    from src.models.product import Product
    from src.models.payable import Payable
    from src.models.suggested_payment import SuggestedPayment
    
    suppliers_count = Supplier.query.count()
    products_count = Product.query.count()
    pending_payables_count = Payable.query.filter(Payable.status.in_(['pending', 'partial'])).count()
    suggested_payments_count = SuggestedPayment.query.count()
    
    # الحصول على الميزانية المتاحة
    available_budget = calculator.settings['available_budget']
    
    return render_template('dashboard/index.html',
                          priority_stats=priority_stats,
                          suppliers_count=suppliers_count,
                          products_count=products_count,
                          pending_payables_count=pending_payables_count,
                          suggested_payments_count=suggested_payments_count,
                          available_budget=available_budget)

@dashboard_bp.route('/recalculate', methods=['POST'])
@login_required
def recalculate():
    """إعادة حساب الأولويات والمدفوعات المقترحة"""
    calculator = PriorityCalculator()
    
    # حساب الأولويات
    calculator.calculate_all_priorities(current_user.id)
    
    # حساب المدفوعات المقترحة
    calculator.calculate_suggested_payments(current_user.id)
    
    flash('تم إعادة حساب الأولويات والمدفوعات المقترحة بنجاح', 'success')
    return redirect(url_for('dashboard.index'))
