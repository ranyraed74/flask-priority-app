from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    """صفحة التقارير الرئيسية"""
    return render_template('reports/index.html')

@reports_bp.route('/inventory')
@login_required
def inventory():
    """تقرير المخزون"""
    from src.models.inventory import Inventory
    from src.models.product import Product
    
    inventory_items = Inventory.query.all()
    return render_template('reports/inventory.html', inventory_items=inventory_items)

@reports_bp.route('/sales')
@login_required
def sales():
    """تقرير المبيعات"""
    from src.models.sale import Sale
    
    # الحصول على المبيعات حسب الفترة
    period = request.args.get('period', 'month')
    
    if period == 'month':
        month = int(request.args.get('month', datetime.now().month))
        year = int(request.args.get('year', datetime.now().year))
        sales = Sale.query.filter_by(month=month, year=year).all()
        title = f"تقرير المبيعات لشهر {month}/{year}"
    elif period == 'year':
        year = int(request.args.get('year', datetime.now().year))
        sales = Sale.query.filter_by(year=year).all()
        title = f"تقرير المبيعات لعام {year}"
    else:
        sales = Sale.query.all()
        title = "تقرير المبيعات الكامل"
    
    return render_template('reports/sales.html', sales=sales, title=title, period=period)

@reports_bp.route('/payables')
@login_required
def payables():
    """تقرير المستحقات"""
    from src.models.payable import Payable
    
    # الحصول على المستحقات حسب الحالة
    status = request.args.get('status', 'all')
    
    if status == 'pending':
        payables = Payable.query.filter_by(status='pending').all()
        title = "تقرير المستحقات المعلقة"
    elif status == 'partial':
        payables = Payable.query.filter_by(status='partial').all()
        title = "تقرير المستحقات المدفوعة جزئياً"
    elif status == 'paid':
        payables = Payable.query.filter_by(status='paid').all()
        title = "تقرير المستحقات المدفوعة بالكامل"
    else:
        payables = Payable.query.all()
        title = "تقرير المستحقات الكامل"
    
    return render_template('reports/payables.html', payables=payables, title=title, status=status)

@reports_bp.route('/priorities')
@login_required
def priorities():
    """تقرير الأولويات"""
    from src.models.priority_calculation import PriorityCalculation
    
    priorities = PriorityCalculation.query.all()
    return render_template('reports/priorities.html', priorities=priorities)

@reports_bp.route('/suggested_payments')
@login_required
def suggested_payments():
    """تقرير المدفوعات المقترحة"""
    from src.models.suggested_payment import SuggestedPayment
    
    payments = SuggestedPayment.query.all()
    return render_template('reports/suggested_payments.html', payments=payments)
