"""
وحدة اختبار واجهة المستخدم - تحتوي على دوال لاختبار واجهات المستخدم وتجربة الاستخدام
"""

import os
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from src.models.user import User, db
from src.utils.test_utils import TestDataGenerator, TestRunner
from src.utils.priority_calculator import PriorityCalculator


class UITester:
    """
    فئة اختبار واجهة المستخدم - تستخدم لاختبار واجهات المستخدم وتجربة الاستخدام
    """

    def __init__(self, app):
        """تهيئة مختبر واجهة المستخدم"""
        self.app = app
        self.test_data_generator = TestDataGenerator()
        self.test_runner = TestRunner()
        self.calculator = PriorityCalculator()
        self.test_results = []

    def setup_test_routes(self):
        """إعداد مسارات الاختبار"""
        
        @self.app.route('/test/generate-data', methods=['GET', 'POST'])
        @login_required
        def generate_test_data():
            """مسار إنشاء البيانات التجريبية"""
            if current_user.role != 'admin':
                flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
                return redirect(url_for('dashboard.index'))
            
            if request.method == 'POST':
                success, message = self.test_data_generator.generate_all_test_data()
                
                if success:
                    flash(message, 'success')
                else:
                    flash(message, 'danger')
                
                return redirect(url_for('test.dashboard'))
            
            return render_template('test/generate_data.html')
        
        @self.app.route('/test/dashboard')
        @login_required
        def test_dashboard():
            """لوحة تحكم الاختبار"""
            if current_user.role != 'admin':
                flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
                return redirect(url_for('dashboard.index'))
            
            # إحصائيات عامة
            stats = {
                'suppliers_count': db.session.query(db.func.count('*')).select_from(Supplier).scalar() or 0,
                'products_count': db.session.query(db.func.count('*')).select_from(Product).scalar() or 0,
                'payables_count': db.session.query(db.func.count('*')).select_from(Payable).scalar() or 0,
                'priority_calcs_count': db.session.query(db.func.count('*')).select_from(PriorityCalculation).scalar() or 0,
                'suggested_payments_count': db.session.query(db.func.count('*')).select_from(SuggestedPayment).scalar() or 0
            }
            
            return render_template('test/dashboard.html', stats=stats, test_results=self.test_results)
        
        @self.app.route('/test/run-tests', methods=['POST'])
        @login_required
        def run_tests():
            """مسار تشغيل الاختبارات"""
            if current_user.role != 'admin':
                flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
                return redirect(url_for('dashboard.index'))
            
            self.test_results = self.test_runner.run_all_tests()
            
            success_count = sum(1 for result in self.test_results if result[0])
            total_count = len(self.test_results)
            
            flash(f'تم تشغيل {total_count} اختبار، نجح {success_count} وفشل {total_count - success_count}', 'info')
            
            return redirect(url_for('test.dashboard'))
        
        @self.app.route('/test/recalculate-priorities', methods=['POST'])
        @login_required
        def recalculate_priorities():
            """مسار إعادة حساب الأولويات"""
            if current_user.role != 'admin':
                flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
                return redirect(url_for('dashboard.index'))
            
            success = self.calculator.calculate_all_priorities(current_user.id)
            
            if success:
                flash('تم إعادة حساب الأولويات بنجاح', 'success')
            else:
                flash('فشل إعادة حساب الأولويات', 'danger')
            
            return redirect(url_for('test.dashboard'))
        
        @self.app.route('/test/performance')
        @login_required
        def test_performance():
            """مسار اختبار الأداء"""
            if current_user.role != 'admin':
                flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
                return redirect(url_for('dashboard.index'))
            
            performance_results = []
            
            # اختبار أداء حساب الأولويات
            start_time = time.time()
            self.calculator.calculate_all_priorities(current_user.id)
            end_time = time.time()
            
            priority_calc_time = end_time - start_time
            performance_results.append(('حساب الأولويات', priority_calc_time))
            
            # اختبار أداء حساب خطة السداد المقترحة
            start_time = time.time()
            self.calculator.calculate_suggested_payments(current_user.id)
            end_time = time.time()
            
            payment_calc_time = end_time - start_time
            performance_results.append(('حساب خطة السداد', payment_calc_time))
            
            return render_template('test/performance.html', performance_results=performance_results)
        
        @self.app.route('/test/usability')
        @login_required
        def test_usability():
            """مسار اختبار سهولة الاستخدام"""
            if current_user.role != 'admin':
                flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
                return redirect(url_for('dashboard.index'))
            
            # قائمة بالصفحات الرئيسية للاختبار
            pages = [
                {'name': 'لوحة التحكم', 'url': url_for('dashboard.index'), 'description': 'الصفحة الرئيسية للتطبيق'},
                {'name': 'الموردين', 'url': url_for('suppliers.index'), 'description': 'إدارة الموردين'},
                {'name': 'المنتجات', 'url': url_for('products.index'), 'description': 'إدارة المنتجات'},
                {'name': 'المستحقات', 'url': url_for('payables.index'), 'description': 'إدارة المستحقات'},
                {'name': 'أولويات السداد', 'url': url_for('priority.index'), 'description': 'حساب أولويات السداد'},
                {'name': 'التقارير', 'url': url_for('reports.index'), 'description': 'عرض وتصدير التقارير'},
                {'name': 'الإعدادات', 'url': url_for('settings.index'), 'description': 'إعدادات النظام'}
            ]
            
            return render_template('test/usability.html', pages=pages)
        
        # تسجيل مسارات الاختبار
        self.app.add_url_rule('/test/generate-data', view_func=generate_test_data)
        self.app.add_url_rule('/test/dashboard', view_func=test_dashboard)
        self.app.add_url_rule('/test/run-tests', view_func=run_tests, methods=['POST'])
        self.app.add_url_rule('/test/recalculate-priorities', view_func=recalculate_priorities, methods=['POST'])
        self.app.add_url_rule('/test/performance', view_func=test_performance)
        self.app.add_url_rule('/test/usability', view_func=test_usability)
        
        # إنشاء مجلد القوالب للاختبار إذا لم يكن موجوداً
        test_templates_dir = os.path.join(self.app.root_path, 'templates', 'test')
        if not os.path.exists(test_templates_dir):
            os.makedirs(test_templates_dir)
        
        # إنشاء قوالب الاختبار
        self._create_test_templates()

    def _create_test_templates(self):
        """إنشاء قوالب الاختبار"""
        templates_dir = os.path.join(self.app.root_path, 'templates', 'test')
        
        # قالب لوحة تحكم الاختبار
        dashboard_template = """
{% extends 'base.html' %}

{% block title %}اختبار النظام | نظام إدارة أولويات السداد للموردين{% endblock %}

{% block page_title %}لوحة تحكم الاختبار{% endblock %}

{% block breadcrumb %}
<li class="breadcrumb-item active">اختبار النظام</li>
{% endblock %}

{% block content %}
<div class="test-dashboard-container">
    <!-- بطاقات الإحصائيات -->
    <div class="row summary-cards mb-4">
        <div class="col-md-4">
            <div class="card summary-card">
                <div class="card-body">
                    <h5 class="card-title">عدد الموردين</h5>
                    <h2 class="card-value">{{ stats.suppliers_count }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card summary-card">
                <div class="card-body">
                    <h5 class="card-title">عدد المنتجات</h5>
                    <h2 class="card-value">{{ stats.products_count }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card summary-card">
                <div class="card-body">
                    <h5 class="card-title">عدد المستحقات</h5>
                    <h2 class="card-value">{{ stats.payables_count }}</h2>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row summary-cards mb-4">
        <div class="col-md-6">
            <div class="card summary-card">
                <div class="card-body">
                    <h5 class="card-title">عدد حسابات الأولوية</h5>
                    <h2 class="card-value">{{ stats.priority_calcs_count }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card summary-card">
                <div class="card-body">
                    <h5 class="card-title">عدد المدفوعات المقترحة</h5>
                    <h2 class="card-value">{{ stats.suggested_payments_count }}</h2>
                </div>
            </div>
        </div>
    </div>
    
    <!-- أزرار الاختبار -->
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h5>أدوات الاختبار</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <a href="{{ url_for('test.generate_data') }}" class="btn btn-primary btn-lg w-100 mb-3">
                                <i class="fas fa-database"></i> إنشاء بيانات تجريبية
                            </a>
                        </div>
                        <div class="col-md-3">
                            <form action="{{ url_for('test.run_tests') }}" method="POST">
                                <button type="submit" class="btn btn-success btn-lg w-100 mb-3">
                                    <i class="fas fa-vial"></i> تشغيل الاختبارات
                                </button>
                            </form>
                        </div>
                        <div class="col-md-3">
                            <form action="{{ url_for('test.recalculate_priorities') }}" method="POST">
                                <button type="submit" class="btn btn-warning btn-lg w-100 mb-3">
                                    <i class="fas fa-calculator"></i> إعادة حساب الأولويات
                                </button>
                            </form>
                        </div>
                        <div class="col-md-3">
                            <a href="{{ url_for('test.performance') }}" class="btn btn-info btn-lg w-100 mb-3">
                                <i class="fas fa-tachometer-alt"></i> اختبار الأداء
                            </a>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-12">
                            <a href="{{ url_for('test.usability') }}" class="btn btn-secondary btn-lg w-100">
                                <i class="fas fa-user-check"></i> اختبار سهولة الاستخدام
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- نتائج الاختبارات -->
    {% if test_results %}
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h5>نتائج الاختبارات</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>النتيجة</th>
                                    <th>الرسالة</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for success, message in test_results %}
                                <tr class="{% if success %}table-success{% else %}table-danger{% endif %}">
                                    <td>
                                        {% if success %}
                                        <i class="fas fa-check-circle text-success"></i> نجاح
                                        {% else %}
                                        <i class="fas fa-times-circle text-danger"></i> فشل
                                        {% endif %}
                                    </td>
                                    <td>{{ message }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
        """
        
        # قالب إنشاء البيانات التجريبية
        generate_data_template = """
{% extends 'base.html' %}

{% block title %}إنشاء بيانات تجريبية | نظام إدارة أولويات السداد للموردين{% endblock %}

{% block page_title %}إنشاء بيانات تجريبية{% endblock %}

{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{{ url_for('test.dashboard') }}">اختبار النظام</a></li>
<li class="breadcrumb-item active">إنشاء بيانات تجريبية</li>
{% endblock %}

{% block content %}
<div class="generate-data-container">
    <div class="card">
        <div class="card-header">
            <h5>إنشاء بيانات تجريبية</h5>
        </div>
        <div class="card-body">
            <div class="alert alert-info">
                <h5><i class="fas fa-info-circle"></i> معلومات</h5>
                <p>سيقوم هذا الإجراء بإنشاء بيانات تجريبية للنظام، بما في ذلك:</p>
                <ul>
                    <li>10 موردين تجريبيين</li>
                    <li>50 منتج تجريبي</li>
                    <li>بيانات مخزون ومبيعات للأشهر الثلاثة الماضية</li>
                    <li>مستحقات تجريبية للموردين</li>
                    <li>حساب أولويات السداد وخطة السداد المقترحة</li>
                </ul>
                <p><strong>ملاحظة:</strong> لن يتم حذف البيانات الموجودة، بل سيتم إضافة البيانات التجريبية إليها.</p>
            </div>
            
            <form action="{{ url_for('test.generate_data') }}" method="POST">
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary btn-lg">
                        <i class="fas fa-database"></i> إنشاء البيانات التجريبية
                    </button>
                    <a href="{{ url_for('test.dashboard') }}" class="btn btn-secondary">
                        <i class="fas fa-arrow-left"></i> العودة إلى لوحة تحكم الاختبار
                    </a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
        """
        
        # قالب اختبار الأداء
        performance_template = """
{% extends 'base.html' %}

{% block title %}اختبار الأداء | نظام إدارة أولويات السداد للموردين{% endblock %}

{% block page_title %}اختبار الأداء{% endblock %}

{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{{ url_for('test.dashboard') }}">اختبار النظام</a></li>
<li class="breadcrumb-item active">اختبار الأداء</li>
{% endblock %}

{% block content %}
<div class="performance-container">
    <div class="card">
        <div class="card-header">
            <h5>نتائج اختبار الأداء</h5>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>العملية</th>
                            <th>وقت التنفيذ (ثانية)</th>
                            <th>التقييم</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for operation, time in performance_results %}
                        <tr>
                            <td>{{ operation }}</td>
                            <td>{{ time|round(3) }}</td>
                            <td>
                                {% if time < 1 %}
                                <span class="badge bg-success">ممتاز</span>
                                {% elif time < 3 %}
                                <span class="badge bg-info">جيد</span>
                                {% elif time < 5 %}
                                <span class="badge bg-warning">مقبول</span>
                                {% else %}
                                <span class="badge bg-danger">بطيء</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="mt-4">
                <a href="{{ url_for('test.dashboard') }}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> العودة إلى لوحة تحكم الاختبار
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
        """
        
        # قالب اختبار سهولة الاستخدام
        usability_template = """
{% extends 'base.html' %}

{% block title %}اختبار سهولة الاستخدام | نظام إدارة أولويات السداد للموردين{% endblock %}

{% block page_title %}اختبار سهولة الاستخدام{% endblock %}

{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{{ url_for('test.dashboard') }}">اختبار النظام</a></li>
<li class="breadcrumb-item active">اختبار سهولة الاستخدام</li>
{% endblock %}

{% block content %}
<div class="usability-container">
    <div class="card mb-4">
        <div class="card-header">
            <h5>قائمة الصفحات للاختبار</h5>
        </div>
        <div class="card-body">
            <p class="mb-4">يرجى زيارة الصفحات التالية واختبار وظائفها للتأكد من سهولة الاستخدام وعدم وجود أخطاء:</p>
            
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>الصفحة</th>
                            <th>الوصف</th>
                            <th>الإجراء</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for page in pages %}
                        <tr>
                            <td>{{ page.name }}</td>
                            <td>{{ page.description }}</td>
                            <td>
                                <a href="{{ page.url }}" class="btn btn-primary" target="_blank">
                                    <i class="fas fa-external-link-alt"></i> فتح
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header">
            <h5>قائمة التحقق من سهولة الاستخدام</h5>
        </div>
        <div class="card-body">
            <form id="usabilityForm">
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check1">
                        <label class="form-check-label" for="check1">
                            تعمل جميع الروابط بشكل صحيح
                        </label>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check2">
                        <label class="form-check-label" for="check2">
                            تظهر جميع العناصر بشكل صحيح على الشاشة
                        </label>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check3">
                        <label class="form-check-label" for="check3">
                            تعمل نماذج الإدخال بشكل صحيح
                        </label>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check4">
                        <label class="form-check-label" for="check4">
                            تظهر الرسائل التنبيهية بشكل واضح
                        </label>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check5">
                        <label class="form-check-label" for="check5">
                            تعمل وظائف البحث والتصفية بشكل صحيح
                        </label>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check6">
                        <label class="form-check-label" for="check6">
                            تعمل وظائف الترتيب بشكل صحيح
                        </label>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check7">
                        <label class="form-check-label" for="check7">
                            تعمل وظائف التصدير والاستيراد بشكل صحيح
                        </label>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check8">
                        <label class="form-check-label" for="check8">
                            تعمل وظائف حساب الأولويات بشكل صحيح
                        </label>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check9">
                        <label class="form-check-label" for="check9">
                            تعمل وظائف خطة السداد المقترحة بشكل صحيح
                        </label>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="check10">
                        <label class="form-check-label" for="check10">
                            يعمل التطبيق بشكل جيد على الأجهزة المحمولة
                        </label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label for="notes" class="form-label">ملاحظات إضافية:</label>
                    <textarea class="form-control" id="notes" rows="3"></textarea>
                </div>
                
                <div class="d-grid gap-2">
                    <button type="button" id="saveResults" class="btn btn-success">
                        <i class="fas fa-save"></i> حفظ النتائج
                    </button>
                    <a href="{{ url_for('test.dashboard') }}" class="btn btn-secondary">
                        <i class="fas fa-arrow-left"></i> العودة إلى لوحة تحكم الاختبار
                    </a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById('saveResults').addEventListener('click', function() {
            // في بيئة حقيقية، يمكن إرسال النتائج إلى الخادم
            // هنا نكتفي بعرض رسالة نجاح
            alert('تم حفظ نتائج الاختبار بنجاح!');
        });
    });
</script>
{% endblock %}
        """
        
        # كتابة القوالب إلى الملفات
        with open(os.path.join(templates_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
            f.write(dashboard_template)
        
        with open(os.path.join(templates_dir, 'generate_data.html'), 'w', encoding='utf-8') as f:
            f.write(generate_data_template)
        
        with open(os.path.join(templates_dir, 'performance.html'), 'w', encoding='utf-8') as f:
            f.write(performance_template)
        
        with open(os.path.join(templates_dir, 'usability.html'), 'w', encoding='utf-8') as f:
            f.write(usability_template)
