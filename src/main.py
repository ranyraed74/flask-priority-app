from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user
import os
from datetime import datetime

# تعديل مؤقت: استخدام القالب المبسط لتقليل استهلاك الموارد
USE_MINIMAL_TEMPLATE = True

# استيراد كائن db المركزي
from src.models import db

# إنشاء تطبيق Flask
app = Flask(__name__)

def create_app():
    # استخدام التطبيق المعرف مسبقاً
    global app
    app.config['SECRET_KEY'] = 'warehouse_payment_system_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # تهيئة قاعدة البيانات مع التطبيق
    db.init_app(app)
    
    # تهيئة مدير تسجيل الدخول
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # استيراد النماذج
    from .models.user import User
    from .models.supplier import Supplier
    from .models.product import Product
    from .models.inventory import Inventory
    from .models.sale import Sale
    from .models.payable import Payable
    from .models.monthly_avg_inventory import MonthlyAvgInventory
    from .models.priority_calculation import PriorityCalculation
    from .models.suggested_payment import SuggestedPayment
    from .models.setting import Setting
    from .models.log import Log
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # تسجيل المسارات
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.suppliers import suppliers_bp
    from .routes.products import products_bp
    from .routes.inventory import inventory_bp
    from .routes.payables import payables_bp
    from .routes.priority import priority_bp
    from .routes.payments import payments_bp
    from .routes.sales import sales_bp
    from .routes.reports import reports_bp
    from .routes.settings import settings_bp
    from .routes.import_export import import_export_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(payables_bp)
    app.register_blueprint(priority_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(import_export_bp)
    
    # تعديل مؤقت: استخدام القالب المبسط في جميع الصفحات
    if USE_MINIMAL_TEMPLATE:
        @app.context_processor
        def override_base_template():
            return {'base_template': 'minimal_base.html'}
    
    # الصفحة الرئيسية
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))
    
    # تهيئة قاعدة البيانات
    with app.app_context():
        db.create_all()
        
        # إنشاء مستخدم افتراضي إذا لم يكن موجوداً
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='مدير النظام',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    # مرشحات القوالب
    @app.template_filter('date')
    def date_filter(value, format='%Y-%m-%d'):
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
        return value.strftime(format)
    
    @app.template_filter('currency')
    def currency_filter(value):
        if value is None:
            return "0.00 ج.م"
        return f"{value:.2f} ج.م"
    
    @app.template_filter('percentage')
    def percentage_filter(value):
        if value is None:
            return "0%"
        return f"{value * 100:.2f}%"
    
    return app

# تنفيذ دالة create_app لتهيئة التطبيق
app = create_app()
