from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.priority_calculation import PriorityCalculation
from src.models.supplier import Supplier
from src.utils.priority_calculator import PriorityCalculator

priority_bp = Blueprint('priority', __name__, url_prefix='/priority')

@priority_bp.route('/')
@login_required
def index():
    """صفحة قائمة الأولويات"""
    priorities = PriorityCalculation.query.all()
    return render_template('priority/index.html', priorities=priorities)

@priority_bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    """إعادة حساب الأولويات"""
    calculator = PriorityCalculator()
    calculator.calculate_all_priorities(current_user.id)
    
    flash('تم إعادة حساب الأولويات بنجاح', 'success')
    return redirect(url_for('priority.index'))

@priority_bp.route('/view/<int:id>')
@login_required
def view(id):
    """عرض تفاصيل الأولوية"""
    priority = PriorityCalculation.query.get_or_404(id)
    return render_template('priority/view.html', priority=priority)

@priority_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """إعدادات حساب الأولويات"""
    calculator = PriorityCalculator()
    settings = calculator.settings
    
    if request.method == 'POST':
        # تحديث الإعدادات
        settings['turnover_weight'] = float(request.form.get('turnover_weight', 0.4))
        settings['profit_margin_weight'] = float(request.form.get('profit_margin_weight', 0.3))
        settings['strategic_importance_weight'] = float(request.form.get('strategic_importance_weight', 0.3))
        settings['available_budget'] = float(request.form.get('available_budget', 0))
        
        # حفظ الإعدادات
        calculator.save_settings(settings, current_user.id)
        
        flash('تم تحديث إعدادات حساب الأولويات بنجاح', 'success')
        return redirect(url_for('priority.settings'))
    
    return render_template('priority/settings.html', settings=settings)
