"""
وحدة اختبار التكامل - تحتوي على دوال لاختبار تكامل جميع أجزاء التطبيق معاً
"""

import os
import sys
import time
import json
import random
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from src.models.user import User, db
from src.models.supplier import Supplier
from src.models.product import Product
from src.models.inventory import Inventory
from src.models.sale import Sale
from src.models.payable import Payable
from src.models.monthly_avg_inventory import MonthlyAvgInventory
from src.models.priority_calculation import PriorityCalculation
from src.models.suggested_payment import SuggestedPayment
from src.models.setting import Setting
from src.utils.priority_calculator import PriorityCalculator


# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integration_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('integration_test')


class IntegrationTester:
    """
    فئة اختبار التكامل - تستخدم لاختبار تكامل جميع أجزاء التطبيق معاً
    """

    def __init__(self):
        """تهيئة مختبر التكامل"""
        self.calculator = PriorityCalculator()
        self.admin_user = None
        self.test_results = []
        self.test_suppliers = []
        self.test_products = []
        self.test_payables = []

    def setup(self):
        """إعداد بيئة الاختبار"""
        logger.info("بدء إعداد بيئة الاختبار")
        
        # التحقق من وجود مستخدم إداري
        admin = User.query.filter_by(username='admin').first()
        if admin:
            self.admin_user = admin
        else:
            # إنشاء مستخدم إداري
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='مدير النظام',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            self.admin_user = admin
        
        logger.info(f"تم إعداد المستخدم الإداري: {self.admin_user.username}")
        
        return True

    def run_all_tests(self):
        """تشغيل جميع اختبارات التكامل"""
        logger.info("بدء تشغيل اختبارات التكامل")
        
        # إعداد بيئة الاختبار
        if not self.setup():
            logger.error("فشل إعداد بيئة الاختبار")
            return False
        
        # اختبار إدارة الموردين
        self.test_supplier_management()
        
        # اختبار إدارة المنتجات
        self.test_product_management()
        
        # اختبار إدارة المستحقات
        self.test_payable_management()
        
        # اختبار حساب الأولويات
        self.test_priority_calculation()
        
        # اختبار خطة السداد المقترحة
        self.test_suggested_payments()
        
        # اختبار التقارير
        self.test_reports()
        
        # اختبار الإعدادات
        self.test_settings()
        
        # اختبار استيراد وتصدير البيانات
        self.test_import_export()
        
        # اختبار الأداء
        self.test_performance()
        
        # تنظيف بيئة الاختبار
        self.cleanup()
        
        # عرض ملخص النتائج
        self.print_summary()
        
        return True

    def test_supplier_management(self):
        """اختبار إدارة الموردين"""
        logger.info("بدء اختبار إدارة الموردين")
        
        try:
            # إنشاء مورد جديد
            supplier = Supplier(
                name="مورد اختبار التكامل",
                code="TEST001",
                phone="01012345678",
                email="test@example.com",
                address="عنوان اختبار التكامل",
                start_date=datetime.now().date(),
                payment_terms="30 يوم",
                strategic_importance=8,
                notes="ملاحظات اختبار التكامل",
                created_by=self.admin_user.id,
                updated_by=self.admin_user.id
            )
            db.session.add(supplier)
            db.session.commit()
            
            logger.info(f"تم إنشاء المورد: {supplier.name}")
            
            # التحقق من وجود المورد
            saved_supplier = Supplier.query.filter_by(name="مورد اختبار التكامل").first()
            if not saved_supplier:
                logger.error("فشل التحقق من وجود المورد")
                self.test_results.append((False, "فشل اختبار إنشاء المورد"))
                return False
            
            # تحديث المورد
            saved_supplier.phone = "01087654321"
            saved_supplier.strategic_importance = 9
            db.session.commit()
            
            logger.info(f"تم تحديث المورد: {saved_supplier.name}")
            
            # التحقق من تحديث المورد
            updated_supplier = Supplier.query.get(saved_supplier.id)
            if updated_supplier.phone != "01087654321" or updated_supplier.strategic_importance != 9:
                logger.error("فشل التحقق من تحديث المورد")
                self.test_results.append((False, "فشل اختبار تحديث المورد"))
                return False
            
            # حفظ المورد للاختبارات اللاحقة
            self.test_suppliers.append(updated_supplier)
            
            self.test_results.append((True, "نجاح اختبار إدارة الموردين"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار إدارة الموردين: {str(e)}")
            self.test_results.append((False, f"فشل اختبار إدارة الموردين: {str(e)}"))
            return False

    def test_product_management(self):
        """اختبار إدارة المنتجات"""
        logger.info("بدء اختبار إدارة المنتجات")
        
        try:
            if not self.test_suppliers:
                logger.error("لا يوجد موردين للاختبار")
                self.test_results.append((False, "فشل اختبار إدارة المنتجات: لا يوجد موردين للاختبار"))
                return False
            
            supplier = self.test_suppliers[0]
            
            # إنشاء منتج جديد
            product = Product(
                name="منتج اختبار التكامل",
                code="PROD001",
                supplier_id=supplier.id,
                category="سكر",
                purchase_price=50.0,
                selling_price=75.0,
                is_seasonal=False,
                notes="ملاحظات اختبار التكامل",
                created_by=self.admin_user.id,
                updated_by=self.admin_user.id
            )
            db.session.add(product)
            db.session.commit()
            
            logger.info(f"تم إنشاء المنتج: {product.name}")
            
            # التحقق من وجود المنتج
            saved_product = Product.query.filter_by(name="منتج اختبار التكامل").first()
            if not saved_product:
                logger.error("فشل التحقق من وجود المنتج")
                self.test_results.append((False, "فشل اختبار إنشاء المنتج"))
                return False
            
            # إنشاء مخزون للمنتج
            inventory = Inventory(
                product_id=saved_product.id,
                current_stock=100,
                min_stock=20,
                max_stock=200,
                last_stock_update=datetime.now(),
                created_by=self.admin_user.id,
                updated_by=self.admin_user.id
            )
            db.session.add(inventory)
            db.session.commit()
            
            logger.info(f"تم إنشاء مخزون للمنتج: {saved_product.name}")
            
            # إنشاء مبيعات للمنتج
            for i in range(3):
                sale_date = datetime.now().date() - timedelta(days=i * 10)
                sale = Sale(
                    product_id=saved_product.id,
                    quantity=10,
                    unit_price=75.0,
                    total_price=750.0,
                    sale_date=sale_date,
                    created_by=self.admin_user.id
                )
                db.session.add(sale)
            
            db.session.commit()
            
            logger.info(f"تم إنشاء مبيعات للمنتج: {saved_product.name}")
            
            # إنشاء متوسط المخزون الشهري
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            for i in range(3):
                month = current_month - i
                year = current_year
                if month <= 0:
                    month += 12
                    year -= 1
                
                avg_inventory = MonthlyAvgInventory(
                    product_id=saved_product.id,
                    month=month,
                    year=year,
                    avg_stock=80
                )
                db.session.add(avg_inventory)
            
            db.session.commit()
            
            logger.info(f"تم إنشاء متوسط المخزون الشهري للمنتج: {saved_product.name}")
            
            # حفظ المنتج للاختبارات اللاحقة
            self.test_products.append(saved_product)
            
            self.test_results.append((True, "نجاح اختبار إدارة المنتجات"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار إدارة المنتجات: {str(e)}")
            self.test_results.append((False, f"فشل اختبار إدارة المنتجات: {str(e)}"))
            return False

    def test_payable_management(self):
        """اختبار إدارة المستحقات"""
        logger.info("بدء اختبار إدارة المستحقات")
        
        try:
            if not self.test_suppliers:
                logger.error("لا يوجد موردين للاختبار")
                self.test_results.append((False, "فشل اختبار إدارة المستحقات: لا يوجد موردين للاختبار"))
                return False
            
            supplier = self.test_suppliers[0]
            
            # إنشاء مستحق جديد
            payable = Payable(
                supplier_id=supplier.id,
                amount=10000.0,
                due_date=datetime.now().date() + timedelta(days=30),
                description="مستحق اختبار التكامل",
                created_by=self.admin_user.id
            )
            db.session.add(payable)
            db.session.commit()
            
            logger.info(f"تم إنشاء المستحق للمورد: {supplier.name}")
            
            # التحقق من وجود المستحق
            saved_payable = Payable.query.filter_by(description="مستحق اختبار التكامل").first()
            if not saved_payable:
                logger.error("فشل التحقق من وجود المستحق")
                self.test_results.append((False, "فشل اختبار إنشاء المستحق"))
                return False
            
            # تسجيل سداد جزئي
            saved_payable.update_payment(5000.0, datetime.now().date())
            db.session.commit()
            
            logger.info(f"تم تسجيل سداد جزئي للمستحق: {saved_payable.id}")
            
            # التحقق من تحديث المستحق
            updated_payable = Payable.query.get(saved_payable.id)
            if updated_payable.status != 'partial' or float(updated_payable.paid_amount) != 5000.0:
                logger.error("فشل التحقق من تحديث المستحق")
                self.test_results.append((False, "فشل اختبار تحديث المستحق"))
                return False
            
            # حفظ المستحق للاختبارات اللاحقة
            self.test_payables.append(updated_payable)
            
            # إنشاء مستحق آخر
            payable2 = Payable(
                supplier_id=supplier.id,
                amount=5000.0,
                due_date=datetime.now().date() - timedelta(days=10),  # متأخر
                description="مستحق متأخر اختبار التكامل",
                created_by=self.admin_user.id
            )
            db.session.add(payable2)
            db.session.commit()
            
            logger.info(f"تم إنشاء مستحق متأخر للمورد: {supplier.name}")
            
            # حفظ المستحق للاختبارات اللاحقة
            self.test_payables.append(payable2)
            
            self.test_results.append((True, "نجاح اختبار إدارة المستحقات"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار إدارة المستحقات: {str(e)}")
            self.test_results.append((False, f"فشل اختبار إدارة المستحقات: {str(e)}"))
            return False

    def test_priority_calculation(self):
        """اختبار حساب الأولويات"""
        logger.info("بدء اختبار حساب الأولويات")
        
        try:
            if not self.test_suppliers:
                logger.error("لا يوجد موردين للاختبار")
                self.test_results.append((False, "فشل اختبار حساب الأولويات: لا يوجد موردين للاختبار"))
                return False
            
            supplier = self.test_suppliers[0]
            
            # حساب معدل دوران المخزون
            if self.test_products:
                product = self.test_products[0]
                turnover_rate = self.calculator.calculate_turnover_rate(product.id)
                logger.info(f"معدل دوران المخزون للمنتج {product.name}: {turnover_rate}")
            
            # حساب معامل هامش الربح
            profit_margin_factor = self.calculator.calculate_avg_profit_margin_factor(supplier.id)
            logger.info(f"معامل هامش الربح للمورد {supplier.name}: {profit_margin_factor}")
            
            # حساب معامل تاريخ الاستحقاق
            due_date_factor = self.calculator.calculate_due_date_factor(supplier.id)
            logger.info(f"معامل تاريخ الاستحقاق للمورد {supplier.name}: {due_date_factor}")
            
            # حساب درجة الأولوية
            priority_score, priority_category = self.calculator.calculate_priority_score(supplier.id)
            logger.info(f"درجة الأولوية للمورد {supplier.name}: {priority_score} ({priority_category})")
            
            # حساب أولويات جميع الموردين
            result = self.calculator.calculate_all_priorities(self.admin_user.id)
            if not result:
                logger.error("فشل حساب أولويات جميع الموردين")
                self.test_results.append((False, "فشل اختبار حساب أولويات جميع الموردين"))
                return False
            
            logger.info("تم حساب أولويات جميع الموردين بنجاح")
            
            # التحقق من وجود حسابات الأولوية
            priority_calcs = PriorityCalculation.query.all()
            if not priority_calcs:
                logger.error("لم يتم العثور على حسابات الأولوية")
                self.test_results.append((False, "فشل اختبار التحقق من وجود حسابات الأولوية"))
                return False
            
            logger.info(f"تم العثور على {len(priority_calcs)} حساب أولوية")
            
            self.test_results.append((True, "نجاح اختبار حساب الأولويات"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار حساب الأولويات: {str(e)}")
            self.test_results.append((False, f"فشل اختبار حساب الأولويات: {str(e)}"))
            return False

    def test_suggested_payments(self):
        """اختبار خطة السداد المقترحة"""
        logger.info("بدء اختبار خطة السداد المقترحة")
        
        try:
            # تحديث الميزانية المتاحة
            setting = Setting.query.filter_by(key='available_budget').first()
            if setting:
                setting.value = '50000'
            else:
                setting = Setting(
                    key='available_budget',
                    value='50000',
                    description='الميزانية المتاحة للسداد',
                    updated_by=self.admin_user.id
                )
                db.session.add(setting)
            
            db.session.commit()
            
            logger.info("تم تحديث الميزانية المتاحة: 50000")
            
            # حساب خطة السداد المقترحة
            result = self.calculator.calculate_suggested_payments(self.admin_user.id)
            if not result:
                logger.error("فشل حساب خطة السداد المقترحة")
                self.test_results.append((False, "فشل اختبار حساب خطة السداد المقترحة"))
                return False
            
            logger.info("تم حساب خطة السداد المقترحة بنجاح")
            
            # التحقق من وجود خطة السداد المقترحة
            suggested_payments = SuggestedPayment.query.all()
            if not suggested_payments:
                logger.error("لم يتم العثور على خطة السداد المقترحة")
                self.test_results.append((False, "فشل اختبار التحقق من وجود خطة السداد المقترحة"))
                return False
            
            logger.info(f"تم العثور على {len(suggested_payments)} دفعة مقترحة")
            
            # التحقق من أن مجموع المدفوعات المقترحة لا يتجاوز الميزانية
            total_suggested = sum(float(payment.suggested_amount) for payment in suggested_payments)
            if total_suggested > 50000:
                logger.error(f"مجموع المدفوعات المقترحة ({total_suggested}) يتجاوز الميزانية (50000)")
                self.test_results.append((False, "فشل اختبار التحقق من مجموع المدفوعات المقترحة"))
                return False
            
            logger.info(f"مجموع المدفوعات المقترحة: {total_suggested}")
            
            self.test_results.append((True, "نجاح اختبار خطة السداد المقترحة"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار خطة السداد المقترحة: {str(e)}")
            self.test_results.append((False, f"فشل اختبار خطة السداد المقترحة: {str(e)}"))
            return False

    def test_reports(self):
        """اختبار التقارير"""
        logger.info("بدء اختبار التقارير")
        
        try:
            # اختبار تقرير الموردين
            suppliers = Supplier.query.all()
            logger.info(f"تم استرجاع {len(suppliers)} مورد لتقرير الموردين")
            
            # اختبار تقرير المنتجات
            products = Product.query.all()
            logger.info(f"تم استرجاع {len(products)} منتج لتقرير المنتجات")
            
            # اختبار تقرير المستحقات
            payables = Payable.query.all()
            logger.info(f"تم استرجاع {len(payables)} مستحق لتقرير المستحقات")
            
            # اختبار تقرير الأولويات
            priority_calcs = PriorityCalculation.query.all()
            logger.info(f"تم استرجاع {len(priority_calcs)} حساب أولوية لتقرير الأولويات")
            
            # اختبار تقرير خطة السداد
            suggested_payments = SuggestedPayment.query.all()
            logger.info(f"تم استرجاع {len(suggested_payments)} دفعة مقترحة لتقرير خطة السداد")
            
            self.test_results.append((True, "نجاح اختبار التقارير"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار التقارير: {str(e)}")
            self.test_results.append((False, f"فشل اختبار التقارير: {str(e)}"))
            return False

    def test_settings(self):
        """اختبار الإعدادات"""
        logger.info("بدء اختبار الإعدادات")
        
        try:
            # تحديث إعدادات حساب الأولويات
            new_settings = {
                'turnover_weight': 35,
                'profit_margin_weight': 25,
                'strategic_importance_weight': 20,
                'due_date_weight': 20,
                'critical_threshold': 8.5,
                'high_threshold': 6.5,
                'medium_threshold': 4.5,
                'available_budget': 60000,
                'payment_date': datetime.now().date().isoformat()
            }
            
            success, message = self.calculator.update_settings(new_settings, self.admin_user.id)
            if not success:
                logger.error(f"فشل تحديث الإعدادات: {message}")
                self.test_results.append((False, f"فشل اختبار تحديث الإعدادات: {message}"))
                return False
            
            logger.info("تم تحديث الإعدادات بنجاح")
            
            # التحقق من تحديث الإعدادات
            settings = self.calculator._load_settings()
            if settings['turnover_weight'] != 35 or settings['critical_threshold'] != 8.5:
                logger.error("فشل التحقق من تحديث الإعدادات")
                self.test_results.append((False, "فشل اختبار التحقق من تحديث الإعدادات"))
                return False
            
            logger.info("تم التحقق من تحديث الإعدادات بنجاح")
            
            self.test_results.append((True, "نجاح اختبار الإعدادات"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار الإعدادات: {str(e)}")
            self.test_results.append((False, f"فشل اختبار الإعدادات: {str(e)}"))
            return False

    def test_import_export(self):
        """اختبار استيراد وتصدير البيانات"""
        logger.info("بدء اختبار استيراد وتصدير البيانات")
        
        try:
            # محاكاة تصدير البيانات
            export_data = {
                'suppliers': [
                    {
                        'name': supplier.name,
                        'code': supplier.code,
                        'phone': supplier.phone,
                        'email': supplier.email,
                        'strategic_importance': supplier.strategic_importance
                    }
                    for supplier in Supplier.query.all()[:5]
                ],
                'products': [
                    {
                        'name': product.name,
                        'code': product.code,
                        'category': product.category,
                        'purchase_price': float(product.purchase_price),
                        'selling_price': float(product.selling_price)
                    }
                    for product in Product.query.all()[:5]
                ],
                'payables': [
                    {
                        'supplier_name': payable.supplier.name,
                        'amount': float(payable.amount),
                        'due_date': payable.due_date.isoformat(),
                        'status': payable.status
                    }
                    for payable in Payable.query.all()[:5]
                ]
            }
            
            # كتابة البيانات إلى ملف JSON
            export_file = 'export_test.json'
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"تم تصدير البيانات إلى الملف: {export_file}")
            
            # محاكاة استيراد البيانات
            with open(export_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            logger.info(f"تم استيراد البيانات من الملف: {export_file}")
            
            # التحقق من البيانات المستوردة
            if len(import_data['suppliers']) != len(export_data['suppliers']):
                logger.error("فشل التحقق من البيانات المستوردة: عدد الموردين غير متطابق")
                self.test_results.append((False, "فشل اختبار التحقق من البيانات المستوردة"))
                return False
            
            logger.info("تم التحقق من البيانات المستوردة بنجاح")
            
            # حذف ملف التصدير
            os.remove(export_file)
            
            self.test_results.append((True, "نجاح اختبار استيراد وتصدير البيانات"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار استيراد وتصدير البيانات: {str(e)}")
            self.test_results.append((False, f"فشل اختبار استيراد وتصدير البيانات: {str(e)}"))
            return False

    def test_performance(self):
        """اختبار الأداء"""
        logger.info("بدء اختبار الأداء")
        
        try:
            # اختبار أداء حساب الأولويات
            start_time = time.time()
            self.calculator.calculate_all_priorities(self.admin_user.id)
            end_time = time.time()
            
            priority_calc_time = end_time - start_time
            logger.info(f"وقت حساب الأولويات: {priority_calc_time} ثانية")
            
            # اختبار أداء حساب خطة السداد المقترحة
            start_time = time.time()
            self.calculator.calculate_suggested_payments(self.admin_user.id)
            end_time = time.time()
            
            payment_calc_time = end_time - start_time
            logger.info(f"وقت حساب خطة السداد: {payment_calc_time} ثانية")
            
            # اختبار أداء استرجاع البيانات
            start_time = time.time()
            suppliers = Supplier.query.all()
            products = Product.query.all()
            payables = Payable.query.all()
            end_time = time.time()
            
            data_retrieval_time = end_time - start_time
            logger.info(f"وقت استرجاع البيانات: {data_retrieval_time} ثانية")
            
            self.test_results.append((True, "نجاح اختبار الأداء"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار الأداء: {str(e)}")
            self.test_results.append((False, f"فشل اختبار الأداء: {str(e)}"))
            return False

    def cleanup(self):
        """تنظيف بيئة الاختبار"""
        logger.info("بدء تنظيف بيئة الاختبار")
        
        try:
            # حذف المستحقات التجريبية
            for payable in self.test_payables:
                db.session.delete(payable)
            
            # حذف المنتجات التجريبية
            for product in self.test_products:
                # حذف المبيعات المرتبطة بالمنتج
                Sale.query.filter_by(product_id=product.id).delete()
                
                # حذف المخزون المرتبط بالمنتج
                Inventory.query.filter_by(product_id=product.id).delete()
                
                # حذف متوسط المخزون الشهري المرتبط بالمنتج
                MonthlyAvgInventory.query.filter_by(product_id=product.id).delete()
                
                # حذف المنتج
                db.session.delete(product)
            
            # حذف الموردين التجريبيين
            for supplier in self.test_suppliers:
                # حذف حسابات الأولوية المرتبطة بالمورد
                PriorityCalculation.query.filter_by(supplier_id=supplier.id).delete()
                
                # حذف المدفوعات المقترحة المرتبطة بالمورد
                SuggestedPayment.query.filter_by(supplier_id=supplier.id).delete()
                
                # حذف المورد
                db.session.delete(supplier)
            
            db.session.commit()
            
            logger.info("تم تنظيف بيئة الاختبار بنجاح")
            
            return True
        
        except Exception as e:
            logger.error(f"خطأ في تنظيف بيئة الاختبار: {str(e)}")
            db.session.rollback()
            return False

    def print_summary(self):
        """عرض ملخص نتائج الاختبارات"""
        logger.info("ملخص نتائج الاختبارات:")
        
        success_count = sum(1 for result in self.test_results if result[0])
        total_count = len(self.test_results)
        
        logger.info(f"إجمالي الاختبارات: {total_count}")
        logger.info(f"الاختبارات الناجحة: {success_count}")
        logger.info(f"الاختبارات الفاشلة: {total_count - success_count}")
        
        for i, (success, message) in enumerate(self.test_results, 1):
            status = "نجاح" if success else "فشل"
            logger.info(f"{i}. {status}: {message}")
        
        return success_count, total_count
