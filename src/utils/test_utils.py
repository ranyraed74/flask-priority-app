"""
وحدة اختبار التطبيق - تحتوي على دوال لتوليد بيانات تجريبية واختبار وظائف التطبيق
"""

import logging
import random
import string
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

# إعداد التسجيل
logger = logging.getLogger(__name__)

class TestDataGenerator:
    """
    فئة توليد البيانات التجريبية - تستخدم لتوليد بيانات تجريبية للاختبار
    """

    def __init__(self):
        """تهيئة مولد البيانات التجريبية"""
        self.admin_user = None

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

    def generate_all(self):
        """توليد جميع البيانات التجريبية"""
        logger.info("بدء توليد البيانات التجريبية")
        
        # إعداد بيئة الاختبار
        if not self.setup():
            logger.error("فشل إعداد بيئة الاختبار")
            return False
        
        # توليد الموردين
        self.generate_suppliers(10)
        
        # توليد المنتجات
        self.generate_products(30)
        
        # توليد المخزون
        self.generate_inventory()
        
        # توليد المبيعات
        self.generate_sales(100)
        
        # توليد متوسط المخزون الشهري
        self.generate_monthly_avg_inventory()
        
        # توليد المستحقات
        self.generate_payables(20)
        
        # توليد الإعدادات
        self.generate_settings()
        
        logger.info("تم توليد جميع البيانات التجريبية بنجاح")
        
        return True

    def generate_suppliers(self, count):
        """توليد موردين تجريبيين"""
        logger.info(f"توليد {count} مورد تجريبي")
        
        for i in range(count):
            supplier = Supplier(
                name=f"مورد تجريبي {i+1}",
                code=f"SUP{i+1:03d}",
                phone=f"0101234{i+1:04d}",
                email=f"supplier{i+1}@example.com",
                address=f"عنوان المورد التجريبي {i+1}",
                start_date=datetime.now().date() - timedelta(days=random.randint(30, 365)),
                payment_terms=random.choice(["30 يوم", "45 يوم", "60 يوم"]),
                strategic_importance=random.randint(1, 10),
                notes=f"ملاحظات المورد التجريبي {i+1}",
                created_by=self.admin_user.id,
                updated_by=self.admin_user.id
            )
            db.session.add(supplier)
        
        db.session.commit()
        logger.info(f"تم توليد {count} مورد تجريبي بنجاح")

    def generate_products(self, count):
        """توليد منتجات تجريبية"""
        logger.info(f"توليد {count} منتج تجريبي")
        
        # الحصول على جميع الموردين
        suppliers = Supplier.query.all()
        if not suppliers:
            logger.error("لا يوجد موردين لتوليد المنتجات")
            return False
        
        categories = ["سكر", "زيت", "رز", "معلبات", "بقوليات", "توابل", "مشروبات"]
        
        for i in range(count):
            supplier = random.choice(suppliers)
            category = random.choice(categories)
            purchase_price = round(random.uniform(10, 100), 2)
            selling_price = round(purchase_price * random.uniform(1.1, 1.5), 2)
            
            product = Product(
                name=f"{category} تجريبي {i+1}",
                code=f"PRD{i+1:03d}",
                supplier_id=supplier.id,
                category=category,
                purchase_price=purchase_price,
                selling_price=selling_price,
                is_seasonal=random.choice([True, False]),
                notes=f"ملاحظات المنتج التجريبي {i+1}",
                created_by=self.admin_user.id,
                updated_by=self.admin_user.id
            )
            db.session.add(product)
        
        db.session.commit()
        logger.info(f"تم توليد {count} منتج تجريبي بنجاح")

    def generate_inventory(self):
        """توليد مخزون تجريبي"""
        logger.info("توليد مخزون تجريبي")
        
        # الحصول على جميع المنتجات
        products = Product.query.all()
        if not products:
            logger.error("لا يوجد منتجات لتوليد المخزون")
            return False
        
        for product in products:
            current_stock = random.randint(10, 200)
            min_stock = random.randint(5, 20)
            max_stock = current_stock + random.randint(50, 100)
            
            inventory = Inventory(
                product_id=product.id,
                current_stock=current_stock,
                min_stock=min_stock,
                max_stock=max_stock,
                last_stock_update=datetime.now() - timedelta(days=random.randint(0, 30)),
                created_by=self.admin_user.id,
                updated_by=self.admin_user.id
            )
            db.session.add(inventory)
        
        db.session.commit()
        logger.info("تم توليد المخزون التجريبي بنجاح")

    def generate_sales(self, count):
        """توليد مبيعات تجريبية"""
        logger.info(f"توليد {count} عملية بيع تجريبية")
        
        # الحصول على جميع المنتجات
        products = Product.query.all()
        if not products:
            logger.error("لا يوجد منتجات لتوليد المبيعات")
            return False
        
        for i in range(count):
            product = random.choice(products)
            quantity = random.randint(1, 20)
            unit_price = float(product.selling_price)
            total_price = quantity * unit_price
            sale_date = datetime.now().date() - timedelta(days=random.randint(0, 90))
            
            sale = Sale(
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                sale_date=sale_date,
                created_by=self.admin_user.id
            )
            db.session.add(sale)
        
        db.session.commit()
        logger.info(f"تم توليد {count} عملية بيع تجريبية بنجاح")

    def generate_monthly_avg_inventory(self):
        """توليد متوسط المخزون الشهري التجريبي"""
        logger.info("توليد متوسط المخزون الشهري التجريبي")
        
        # الحصول على جميع المنتجات
        products = Product.query.all()
        if not products:
            logger.error("لا يوجد منتجات لتوليد متوسط المخزون الشهري")
            return False
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        for product in products:
            # توليد متوسط المخزون للثلاثة أشهر الماضية
            for i in range(3):
                month = current_month - i
                year = current_year
                if month <= 0:
                    month += 12
                    year -= 1
                
                # الحصول على المخزون الحالي
                inventory = Inventory.query.filter_by(product_id=product.id).first()
                if inventory:
                    current_stock = float(inventory.current_stock)
                    avg_stock = current_stock * random.uniform(0.8, 1.2)
                    
                    avg_inventory = MonthlyAvgInventory(
                        product_id=product.id,
                        month=month,
                        year=year,
                        avg_stock=avg_stock
                    )
                    db.session.add(avg_inventory)
        
        db.session.commit()
        logger.info("تم توليد متوسط المخزون الشهري التجريبي بنجاح")

    def generate_payables(self, count):
        """توليد مستحقات تجريبية"""
        logger.info(f"توليد {count} مستحق تجريبي")
        
        # الحصول على جميع الموردين
        suppliers = Supplier.query.all()
        if not suppliers:
            logger.error("لا يوجد موردين لتوليد المستحقات")
            return False
        
        statuses = ["pending", "partial", "paid"]
        
        for i in range(count):
            supplier = random.choice(suppliers)
            amount = round(random.uniform(1000, 10000), 2)
            due_date = datetime.now().date() + timedelta(days=random.randint(-30, 60))
            status = random.choice(statuses)
            
            payable = Payable(
                supplier_id=supplier.id,
                amount=amount,
                due_date=due_date,
                description=f"مستحق تجريبي {i+1}",
                status=status,
                created_by=self.admin_user.id
            )
            
            if status in ["partial", "paid"]:
                paid_amount = amount if status == "paid" else amount * random.uniform(0.1, 0.9)
                payable.paid_amount = round(paid_amount, 2)
                payable.payment_date = datetime.now().date() - timedelta(days=random.randint(1, 30))
            
            db.session.add(payable)
        
        db.session.commit()
        logger.info(f"تم توليد {count} مستحق تجريبي بنجاح")

    def generate_settings(self):
        """توليد إعدادات تجريبية"""
        logger.info("توليد إعدادات تجريبية")
        
        settings = [
            {"key": "turnover_weight", "value": "30", "description": "وزن معدل دوران المخزون"},
            {"key": "profit_margin_weight", "value": "25", "description": "وزن هامش الربح"},
            {"key": "strategic_importance_weight", "value": "20", "description": "وزن الأهمية الاستراتيجية"},
            {"key": "due_date_weight", "value": "25", "description": "وزن تاريخ الاستحقاق"},
            {"key": "critical_threshold", "value": "8", "description": "حد الأولوية القصوى"},
            {"key": "high_threshold", "value": "6", "description": "حد الأولوية العالية"},
            {"key": "medium_threshold", "value": "4", "description": "حد الأولوية المتوسطة"},
            {"key": "available_budget", "value": "50000", "description": "الميزانية المتاحة للسداد"},
            {"key": "payment_date", "value": datetime.now().date().isoformat(), "description": "تاريخ السداد المقترح"}
        ]
        
        for setting_data in settings:
            setting = Setting.query.filter_by(key=setting_data["key"]).first()
            
            if setting:
                setting.value = setting_data["value"]
                setting.updated_by = self.admin_user.id
                setting.updated_at = datetime.now()
            else:
                setting = Setting(
                    key=setting_data["key"],
                    value=setting_data["value"],
                    description=setting_data["description"],
                    updated_by=self.admin_user.id
                )
                db.session.add(setting)
        
        db.session.commit()
        logger.info("تم توليد الإعدادات التجريبية بنجاح")


class TestRunner:
    """
    فئة تشغيل الاختبارات - تستخدم لاختبار وظائف التطبيق
    """

    def __init__(self):
        """تهيئة مشغل الاختبارات"""
        self.test_results = []

    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        logger.info("بدء تشغيل جميع الاختبارات")
        
        # اختبار إدارة المستخدمين
        self.test_user_management()
        
        # اختبار إدارة الموردين
        self.test_supplier_management()
        
        # اختبار إدارة المنتجات
        self.test_product_management()
        
        # اختبار إدارة المخزون
        self.test_inventory_management()
        
        # اختبار إدارة المبيعات
        self.test_sales_management()
        
        # اختبار إدارة المستحقات
        self.test_payable_management()
        
        # اختبار حساب الأولويات
        self.test_priority_calculation()
        
        # اختبار خطة السداد المقترحة
        self.test_suggested_payments()
        
        # عرض ملخص النتائج
        self.print_summary()
        
        return True

    def test_user_management(self):
        """اختبار إدارة المستخدمين"""
        logger.info("بدء اختبار إدارة المستخدمين")
        
        try:
            # إنشاء مستخدم جديد
            user = User(
                username="testuser",
                email="testuser@example.com",
                full_name="مستخدم اختبار",
                role="user"
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            # التحقق من وجود المستخدم
            saved_user = User.query.filter_by(username="testuser").first()
            if not saved_user:
                logger.error("فشل التحقق من وجود المستخدم")
                self.test_results.append((False, "فشل اختبار إنشاء المستخدم"))
                return False
            
            # التحقق من صحة كلمة المرور
            if not saved_user.check_password("password123"):
                logger.error("فشل التحقق من صحة كلمة المرور")
                self.test_results.append((False, "فشل اختبار التحقق من كلمة المرور"))
                return False
            
            # تحديث المستخدم
            saved_user.full_name = "مستخدم اختبار معدل"
            db.session.commit()
            
            # التحقق من تحديث المستخدم
            updated_user = User.query.get(saved_user.id)
            if updated_user.full_name != "مستخدم اختبار معدل":
                logger.error("فشل التحقق من تحديث المستخدم")
                self.test_results.append((False, "فشل اختبار تحديث المستخدم"))
                return False
            
            # حذف المستخدم
            db.session.delete(updated_user)
            db.session.commit()
            
            # التحقق من حذف المستخدم
            deleted_user = User.query.filter_by(username="testuser").first()
            if deleted_user:
                logger.error("فشل التحقق من حذف المستخدم")
                self.test_results.append((False, "فشل اختبار حذف المستخدم"))
                return False
            
            self.test_results.append((True, "نجاح اختبار إدارة المستخدمين"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار إدارة المستخدمين: {str(e)}")
            self.test_results.append((False, f"فشل اختبار إدارة المستخدمين: {str(e)}"))
            return False

    def test_supplier_management(self):
        """اختبار إدارة الموردين"""
        logger.info("بدء اختبار إدارة الموردين")
        
        try:
            # الحصول على مستخدم إداري
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                logger.error("لا يوجد مستخدم إداري")
                self.test_results.append((False, "فشل اختبار إدارة الموردين: لا يوجد مستخدم إداري"))
                return False
            
            # إنشاء مورد جديد
            supplier = Supplier(
                name="مورد اختبار",
                code="TEST001",
                phone="01012345678",
                email="test@example.com",
                address="عنوان اختبار",
                start_date=datetime.now().date(),
                payment_terms="30 يوم",
                strategic_importance=8,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(supplier)
            db.session.commit()
            
            # التحقق من وجود المورد
            saved_supplier = Supplier.query.filter_by(name="مورد اختبار").first()
            if not saved_supplier:
                logger.error("فشل التحقق من وجود المورد")
                self.test_results.append((False, "فشل اختبار إنشاء المورد"))
                return False
            
            # تحديث المورد
            saved_supplier.phone = "01087654321"
            saved_supplier.strategic_importance = 9
            db.session.commit()
            
            # التحقق من تحديث المورد
            updated_supplier = Supplier.query.get(saved_supplier.id)
            if updated_supplier.phone != "01087654321" or updated_supplier.strategic_importance != 9:
                logger.error("فشل التحقق من تحديث المورد")
                self.test_results.append((False, "فشل اختبار تحديث المورد"))
                return False
            
            # حذف المورد
            db.session.delete(updated_supplier)
            db.session.commit()
            
            # التحقق من حذف المورد
            deleted_supplier = Supplier.query.filter_by(name="مورد اختبار").first()
            if deleted_supplier:
                logger.error("فشل التحقق من حذف المورد")
                self.test_results.append((False, "فشل اختبار حذف المورد"))
                return False
            
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
            # الحصول على مستخدم إداري
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                logger.error("لا يوجد مستخدم إداري")
                self.test_results.append((False, "فشل اختبار إدارة المنتجات: لا يوجد مستخدم إداري"))
                return False
            
            # إنشاء مورد للاختبار
            supplier = Supplier(
                name="مورد اختبار المنتجات",
                code="TEST002",
                phone="01012345678",
                email="test@example.com",
                address="عنوان اختبار",
                start_date=datetime.now().date(),
                payment_terms="30 يوم",
                strategic_importance=8,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(supplier)
            db.session.commit()
            
            # إنشاء منتج جديد
            product = Product(
                name="منتج اختبار",
                code="PROD001",
                supplier_id=supplier.id,
                category="سكر",
                purchase_price=50.0,
                selling_price=75.0,
                is_seasonal=False,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(product)
            db.session.commit()
            
            # التحقق من وجود المنتج
            saved_product = Product.query.filter_by(name="منتج اختبار").first()
            if not saved_product:
                logger.error("فشل التحقق من وجود المنتج")
                self.test_results.append((False, "فشل اختبار إنشاء المنتج"))
                return False
            
            # تحديث المنتج
            saved_product.purchase_price = 55.0
            saved_product.selling_price = 80.0
            db.session.commit()
            
            # التحقق من تحديث المنتج
            updated_product = Product.query.get(saved_product.id)
            if float(updated_product.purchase_price) != 55.0 or float(updated_product.selling_price) != 80.0:
                logger.error("فشل التحقق من تحديث المنتج")
                self.test_results.append((False, "فشل اختبار تحديث المنتج"))
                return False
            
            # حذف المنتج
            db.session.delete(updated_product)
            db.session.commit()
            
            # التحقق من حذف المنتج
            deleted_product = Product.query.filter_by(name="منتج اختبار").first()
            if deleted_product:
                logger.error("فشل التحقق من حذف المنتج")
                self.test_results.append((False, "فشل اختبار حذف المنتج"))
                return False
            
            # حذف المورد
            db.session.delete(supplier)
            db.session.commit()
            
            self.test_results.append((True, "نجاح اختبار إدارة المنتجات"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار إدارة المنتجات: {str(e)}")
            self.test_results.append((False, f"فشل اختبار إدارة المنتجات: {str(e)}"))
            return False

    def test_inventory_management(self):
        """اختبار إدارة المخزون"""
        logger.info("بدء اختبار إدارة المخزون")
        
        try:
            # الحصول على مستخدم إداري
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                logger.error("لا يوجد مستخدم إداري")
                self.test_results.append((False, "فشل اختبار إدارة المخزون: لا يوجد مستخدم إداري"))
                return False
            
            # إنشاء مورد للاختبار
            supplier = Supplier(
                name="مورد اختبار المخزون",
                code="TEST003",
                phone="01012345678",
                email="test@example.com",
                address="عنوان اختبار",
                start_date=datetime.now().date(),
                payment_terms="30 يوم",
                strategic_importance=8,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(supplier)
            db.session.commit()
            
            # إنشاء منتج للاختبار
            product = Product(
                name="منتج اختبار المخزون",
                code="PROD002",
                supplier_id=supplier.id,
                category="سكر",
                purchase_price=50.0,
                selling_price=75.0,
                is_seasonal=False,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(product)
            db.session.commit()
            
            # إنشاء مخزون جديد
            inventory = Inventory(
                product_id=product.id,
                current_stock=100,
                min_stock=20,
                max_stock=200,
                last_stock_update=datetime.now(),
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(inventory)
            db.session.commit()
            
            # التحقق من وجود المخزون
            saved_inventory = Inventory.query.filter_by(product_id=product.id).first()
            if not saved_inventory:
                logger.error("فشل التحقق من وجود المخزون")
                self.test_results.append((False, "فشل اختبار إنشاء المخزون"))
                return False
            
            # تحديث المخزون
            saved_inventory.current_stock = 120
            saved_inventory.last_stock_update = datetime.now()
            db.session.commit()
            
            # التحقق من تحديث المخزون
            updated_inventory = Inventory.query.get(saved_inventory.id)
            if updated_inventory.current_stock != 120:
                logger.error("فشل التحقق من تحديث المخزون")
                self.test_results.append((False, "فشل اختبار تحديث المخزون"))
                return False
            
            # حذف المخزون
            db.session.delete(updated_inventory)
            db.session.commit()
            
            # التحقق من حذف المخزون
            deleted_inventory = Inventory.query.filter_by(product_id=product.id).first()
            if deleted_inventory:
                logger.error("فشل التحقق من حذف المخزون")
                self.test_results.append((False, "فشل اختبار حذف المخزون"))
                return False
            
            # حذف المنتج والمورد
            db.session.delete(product)
            db.session.delete(supplier)
            db.session.commit()
            
            self.test_results.append((True, "نجاح اختبار إدارة المخزون"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار إدارة المخزون: {str(e)}")
            self.test_results.append((False, f"فشل اختبار إدارة المخزون: {str(e)}"))
            return False

    def test_sales_management(self):
        """اختبار إدارة المبيعات"""
        logger.info("بدء اختبار إدارة المبيعات")
        
        try:
            # الحصول على مستخدم إداري
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                logger.error("لا يوجد مستخدم إداري")
                self.test_results.append((False, "فشل اختبار إدارة المبيعات: لا يوجد مستخدم إداري"))
                return False
            
            # إنشاء مورد للاختبار
            supplier = Supplier(
                name="مورد اختبار المبيعات",
                code="TEST004",
                phone="01012345678",
                email="test@example.com",
                address="عنوان اختبار",
                start_date=datetime.now().date(),
                payment_terms="30 يوم",
                strategic_importance=8,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(supplier)
            db.session.commit()
            
            # إنشاء منتج للاختبار
            product = Product(
                name="منتج اختبار المبيعات",
                code="PROD003",
                supplier_id=supplier.id,
                category="سكر",
                purchase_price=50.0,
                selling_price=75.0,
                is_seasonal=False,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(product)
            db.session.commit()
            
            # إنشاء عملية بيع جديدة
            sale = Sale(
                product_id=product.id,
                quantity=10,
                unit_price=75.0,
                total_price=750.0,
                sale_date=datetime.now().date(),
                created_by=admin.id
            )
            db.session.add(sale)
            db.session.commit()
            
            # التحقق من وجود عملية البيع
            saved_sale = Sale.query.filter_by(product_id=product.id).first()
            if not saved_sale:
                logger.error("فشل التحقق من وجود عملية البيع")
                self.test_results.append((False, "فشل اختبار إنشاء عملية البيع"))
                return False
            
            # تحديث عملية البيع
            saved_sale.quantity = 15
            saved_sale.total_price = 1125.0
            db.session.commit()
            
            # التحقق من تحديث عملية البيع
            updated_sale = Sale.query.get(saved_sale.id)
            if updated_sale.quantity != 15 or float(updated_sale.total_price) != 1125.0:
                logger.error("فشل التحقق من تحديث عملية البيع")
                self.test_results.append((False, "فشل اختبار تحديث عملية البيع"))
                return False
            
            # حذف عملية البيع
            db.session.delete(updated_sale)
            db.session.commit()
            
            # التحقق من حذف عملية البيع
            deleted_sale = Sale.query.filter_by(product_id=product.id).first()
            if deleted_sale:
                logger.error("فشل التحقق من حذف عملية البيع")
                self.test_results.append((False, "فشل اختبار حذف عملية البيع"))
                return False
            
            # حذف المنتج والمورد
            db.session.delete(product)
            db.session.delete(supplier)
            db.session.commit()
            
            self.test_results.append((True, "نجاح اختبار إدارة المبيعات"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار إدارة المبيعات: {str(e)}")
            self.test_results.append((False, f"فشل اختبار إدارة المبيعات: {str(e)}"))
            return False

    def test_payable_management(self):
        """اختبار إدارة المستحقات"""
        logger.info("بدء اختبار إدارة المستحقات")
        
        try:
            # الحصول على مستخدم إداري
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                logger.error("لا يوجد مستخدم إداري")
                self.test_results.append((False, "فشل اختبار إدارة المستحقات: لا يوجد مستخدم إداري"))
                return False
            
            # إنشاء مورد للاختبار
            supplier = Supplier(
                name="مورد اختبار المستحقات",
                code="TEST005",
                phone="01012345678",
                email="test@example.com",
                address="عنوان اختبار",
                start_date=datetime.now().date(),
                payment_terms="30 يوم",
                strategic_importance=8,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(supplier)
            db.session.commit()
            
            # إنشاء مستحق جديد
            payable = Payable(
                supplier_id=supplier.id,
                amount=10000.0,
                due_date=datetime.now().date() + timedelta(days=30),
                description="مستحق اختبار",
                created_by=admin.id
            )
            db.session.add(payable)
            db.session.commit()
            
            # التحقق من وجود المستحق
            saved_payable = Payable.query.filter_by(description="مستحق اختبار").first()
            if not saved_payable:
                logger.error("فشل التحقق من وجود المستحق")
                self.test_results.append((False, "فشل اختبار إنشاء المستحق"))
                return False
            
            # تسجيل سداد جزئي
            saved_payable.update_payment(5000.0, datetime.now().date())
            db.session.commit()
            
            # التحقق من تحديث المستحق
            updated_payable = Payable.query.get(saved_payable.id)
            if updated_payable.status != 'partial' or float(updated_payable.paid_amount) != 5000.0:
                logger.error("فشل التحقق من تحديث المستحق")
                self.test_results.append((False, "فشل اختبار تحديث المستحق"))
                return False
            
            # تسجيل سداد كامل
            updated_payable.update_payment(5000.0, datetime.now().date())
            db.session.commit()
            
            # التحقق من تحديث المستحق
            fully_paid_payable = Payable.query.get(updated_payable.id)
            if fully_paid_payable.status != 'paid' or float(fully_paid_payable.paid_amount) != 10000.0:
                logger.error("فشل التحقق من تحديث المستحق")
                self.test_results.append((False, "فشل اختبار تحديث المستحق"))
                return False
            
            # حذف المستحق
            db.session.delete(fully_paid_payable)
            db.session.commit()
            
            # التحقق من حذف المستحق
            deleted_payable = Payable.query.filter_by(description="مستحق اختبار").first()
            if deleted_payable:
                logger.error("فشل التحقق من حذف المستحق")
                self.test_results.append((False, "فشل اختبار حذف المستحق"))
                return False
            
            # حذف المورد
            db.session.delete(supplier)
            db.session.commit()
            
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
            # الحصول على مستخدم إداري
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                logger.error("لا يوجد مستخدم إداري")
                self.test_results.append((False, "فشل اختبار حساب الأولويات: لا يوجد مستخدم إداري"))
                return False
            
            # إنشاء مورد للاختبار
            supplier = Supplier(
                name="مورد اختبار الأولويات",
                code="TEST006",
                phone="01012345678",
                email="test@example.com",
                address="عنوان اختبار",
                start_date=datetime.now().date(),
                payment_terms="30 يوم",
                strategic_importance=8,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(supplier)
            db.session.commit()
            
            # إنشاء منتج للاختبار
            product = Product(
                name="منتج اختبار الأولويات",
                code="PROD004",
                supplier_id=supplier.id,
                category="سكر",
                purchase_price=50.0,
                selling_price=75.0,
                is_seasonal=False,
                notes="ملاحظات اختبار",
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(product)
            db.session.commit()
            
            # إنشاء مخزون للمنتج
            inventory = Inventory(
                product_id=product.id,
                current_stock=100,
                min_stock=20,
                max_stock=200,
                last_stock_update=datetime.now(),
                created_by=admin.id,
                updated_by=admin.id
            )
            db.session.add(inventory)
            db.session.commit()
            
            # إنشاء مبيعات للمنتج
            for i in range(3):
                sale_date = datetime.now().date() - timedelta(days=i * 10)
                sale = Sale(
                    product_id=product.id,
                    quantity=10,
                    unit_price=75.0,
                    total_price=750.0,
                    sale_date=sale_date,
                    created_by=admin.id
                )
                db.session.add(sale)
            
            db.session.commit()
            
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
                    product_id=product.id,
                    month=month,
                    year=year,
                    avg_stock=80
                )
                db.session.add(avg_inventory)
            
            db.session.commit()
            
            # إنشاء مستحق للمورد
            payable = Payable(
                supplier_id=supplier.id,
                amount=10000.0,
                due_date=datetime.now().date() + timedelta(days=30),
                description="مستحق اختبار الأولويات",
                created_by=admin.id
            )
            db.session.add(payable)
            db.session.commit()
            
            # إنشاء حاسبة الأولويات
            from src.utils.priority_calculator import PriorityCalculator
            calculator = PriorityCalculator()
            
            # حساب الأولويات
            result = calculator.calculate_all_priorities(admin.id)
            if not result:
                logger.error("فشل حساب الأولويات")
                self.test_results.append((False, "فشل اختبار حساب الأولويات"))
                return False
            
            # التحقق من وجود حسابات الأولوية
            priority_calcs = PriorityCalculation.query.filter_by(supplier_id=supplier.id).all()
            if not priority_calcs:
                logger.error("لم يتم العثور على حسابات الأولوية")
                self.test_results.append((False, "فشل اختبار التحقق من وجود حسابات الأولوية"))
                return False
            
            # حذف البيانات
            PriorityCalculation.query.filter_by(supplier_id=supplier.id).delete()
            Payable.query.filter_by(supplier_id=supplier.id).delete()
            MonthlyAvgInventory.query.filter_by(product_id=product.id).delete()
            Sale.query.filter_by(product_id=product.id).delete()
            Inventory.query.filter_by(product_id=product.id).delete()
            db.session.delete(product)
            db.session.delete(supplier)
            db.session.commit()
            
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
            # الحصول على مستخدم إداري
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                logger.error("لا يوجد مستخدم إداري")
                self.test_results.append((False, "فشل اختبار خطة السداد المقترحة: لا يوجد مستخدم إداري"))
                return False
            
            # تحديث الميزانية المتاحة
            setting = Setting.query.filter_by(key='available_budget').first()
            if setting:
                setting.value = '50000'
            else:
                setting = Setting(
                    key='available_budget',
                    value='50000',
                    description='الميزانية المتاحة للسداد',
                    updated_by=admin.id
                )
                db.session.add(setting)
            
            db.session.commit()
            
            # إنشاء حاسبة الأولويات
            from src.utils.priority_calculator import PriorityCalculator
            calculator = PriorityCalculator()
            
            # حساب خطة السداد المقترحة
            result = calculator.calculate_suggested_payments(admin.id)
            if not result:
                logger.error("فشل حساب خطة السداد المقترحة")
                self.test_results.append((False, "فشل اختبار حساب خطة السداد المقترحة"))
                return False
            
            # التحقق من وجود خطة السداد المقترحة
            suggested_payments = SuggestedPayment.query.all()
            
            # حذف المدفوعات المقترحة
            SuggestedPayment.query.delete()
            db.session.commit()
            
            self.test_results.append((True, "نجاح اختبار خطة السداد المقترحة"))
            return True
        
        except Exception as e:
            logger.error(f"خطأ في اختبار خطة السداد المقترحة: {str(e)}")
            self.test_results.append((False, f"فشل اختبار خطة السداد المقترحة: {str(e)}"))
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
