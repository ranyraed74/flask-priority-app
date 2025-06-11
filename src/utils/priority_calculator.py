"""
وحدة حساب الأولويات - تحتوي على دوال لحساب أولويات السداد للموردين
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
import math
import statistics

from src.models.user import db
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

class PriorityCalculator:
    """
    فئة حساب الأولويات - تستخدم لحساب أولويات السداد للموردين
    """

    def __init__(self):
        """تهيئة حاسبة الأولويات"""
        self.settings = self._load_settings()

    def _load_settings(self):
        """تحميل إعدادات حساب الأولويات من قاعدة البيانات"""
        settings = {}
        
        # الأوزان النسبية للمعايير
        turnover_weight = Setting.query.filter_by(key='turnover_weight').first()
        settings['turnover_weight'] = float(turnover_weight.value) if turnover_weight else 30
        
        profit_margin_weight = Setting.query.filter_by(key='profit_margin_weight').first()
        settings['profit_margin_weight'] = float(profit_margin_weight.value) if profit_margin_weight else 25
        
        strategic_importance_weight = Setting.query.filter_by(key='strategic_importance_weight').first()
        settings['strategic_importance_weight'] = float(strategic_importance_weight.value) if strategic_importance_weight else 20
        
        due_date_weight = Setting.query.filter_by(key='due_date_weight').first()
        settings['due_date_weight'] = float(due_date_weight.value) if due_date_weight else 25
        
        # حدود فئات الأولوية
        critical_threshold = Setting.query.filter_by(key='critical_threshold').first()
        settings['critical_threshold'] = float(critical_threshold.value) if critical_threshold else 8
        
        high_threshold = Setting.query.filter_by(key='high_threshold').first()
        settings['high_threshold'] = float(high_threshold.value) if high_threshold else 6
        
        medium_threshold = Setting.query.filter_by(key='medium_threshold').first()
        settings['medium_threshold'] = float(medium_threshold.value) if medium_threshold else 4
        
        # الميزانية المتاحة للسداد
        available_budget = Setting.query.filter_by(key='available_budget').first()
        settings['available_budget'] = float(available_budget.value) if available_budget else 50000
        
        # تاريخ السداد المقترح
        payment_date = Setting.query.filter_by(key='payment_date').first()
        if payment_date and payment_date.value:
            try:
                settings['payment_date'] = datetime.strptime(payment_date.value, '%Y-%m-%d').date()
            except ValueError:
                settings['payment_date'] = datetime.now().date()
        else:
            settings['payment_date'] = datetime.now().date()
        
        return settings

    def update_settings(self, new_settings, user_id):
        """تحديث إعدادات حساب الأولويات"""
        try:
            # تحديث الأوزان النسبية للمعايير
            if 'turnover_weight' in new_settings:
                self._update_setting('turnover_weight', new_settings['turnover_weight'], user_id)
            
            if 'profit_margin_weight' in new_settings:
                self._update_setting('profit_margin_weight', new_settings['profit_margin_weight'], user_id)
            
            if 'strategic_importance_weight' in new_settings:
                self._update_setting('strategic_importance_weight', new_settings['strategic_importance_weight'], user_id)
            
            if 'due_date_weight' in new_settings:
                self._update_setting('due_date_weight', new_settings['due_date_weight'], user_id)
            
            # تحديث حدود فئات الأولوية
            if 'critical_threshold' in new_settings:
                self._update_setting('critical_threshold', new_settings['critical_threshold'], user_id)
            
            if 'high_threshold' in new_settings:
                self._update_setting('high_threshold', new_settings['high_threshold'], user_id)
            
            if 'medium_threshold' in new_settings:
                self._update_setting('medium_threshold', new_settings['medium_threshold'], user_id)
            
            # تحديث الميزانية المتاحة للسداد
            if 'available_budget' in new_settings:
                self._update_setting('available_budget', new_settings['available_budget'], user_id)
            
            # تحديث تاريخ السداد المقترح
            if 'payment_date' in new_settings:
                self._update_setting('payment_date', new_settings['payment_date'], user_id)
            
            # إعادة تحميل الإعدادات
            self.settings = self._load_settings()
            
            return True, "تم تحديث الإعدادات بنجاح"
        
        except Exception as e:
            logger.error(f"خطأ في تحديث الإعدادات: {str(e)}")
            return False, f"فشل تحديث الإعدادات: {str(e)}"

    def _update_setting(self, key, value, user_id):
        """تحديث إعداد معين في قاعدة البيانات"""
        setting = Setting.query.filter_by(key=key).first()
        
        if setting:
            setting.value = str(value)
            setting.updated_by = user_id
            setting.updated_at = datetime.now()
        else:
            setting = Setting(
                key=key,
                value=str(value),
                description=f"إعداد {key}",
                updated_by=user_id
            )
            db.session.add(setting)
        
        db.session.commit()

    def calculate_turnover_rate(self, product_id):
        """حساب معدل دوران المخزون لمنتج معين"""
        try:
            # الحصول على متوسط المخزون الشهري للمنتج
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # حساب متوسط المخزون للثلاثة أشهر الماضية
            avg_inventory_records = []
            for i in range(3):
                month = current_month - i
                year = current_year
                if month <= 0:
                    month += 12
                    year -= 1
                
                avg_inventory = MonthlyAvgInventory.query.filter_by(
                    product_id=product_id,
                    month=month,
                    year=year
                ).first()
                
                if avg_inventory:
                    avg_inventory_records.append(float(avg_inventory.avg_stock))
            
            # إذا لم يكن هناك سجلات لمتوسط المخزون، استخدم المخزون الحالي
            if not avg_inventory_records:
                inventory = Inventory.query.filter_by(product_id=product_id).first()
                if inventory:
                    avg_inventory_value = float(inventory.current_stock)
                else:
                    return 0
            else:
                # حساب متوسط المخزون
                avg_inventory_value = sum(avg_inventory_records) / len(avg_inventory_records)
            
            # الحصول على إجمالي المبيعات للثلاثة أشهر الماضية
            three_months_ago = datetime.now() - timedelta(days=90)
            sales = Sale.query.filter(
                Sale.product_id == product_id,
                Sale.sale_date >= three_months_ago.date()
            ).all()
            
            total_sales = sum(float(sale.quantity) for sale in sales)
            
            # حساب معدل دوران المخزون
            if avg_inventory_value > 0:
                turnover_rate = total_sales / avg_inventory_value
            else:
                turnover_rate = 0
            
            return turnover_rate
        
        except Exception as e:
            logger.error(f"خطأ في حساب معدل دوران المخزون للمنتج {product_id}: {str(e)}")
            return 0

    def calculate_avg_turnover_rate(self, supplier_id):
        """حساب متوسط معدل دوران المخزون لجميع منتجات مورد معين"""
        try:
            # الحصول على جميع منتجات المورد
            products = Product.query.filter_by(supplier_id=supplier_id).all()
            
            if not products:
                return 0
            
            # حساب معدل دوران المخزون لكل منتج
            turnover_rates = []
            for product in products:
                turnover_rate = self.calculate_turnover_rate(product.id)
                turnover_rates.append(turnover_rate)
            
            # حساب متوسط معدل دوران المخزون
            if turnover_rates:
                avg_turnover_rate = sum(turnover_rates) / len(turnover_rates)
            else:
                avg_turnover_rate = 0
            
            return avg_turnover_rate
        
        except Exception as e:
            logger.error(f"خطأ في حساب متوسط معدل دوران المخزون للمورد {supplier_id}: {str(e)}")
            return 0

    def calculate_turnover_factor(self, supplier_id):
        """حساب معامل معدل دوران المخزون (من 0 إلى 10)"""
        try:
            # حساب متوسط معدل دوران المخزون للمورد
            avg_turnover_rate = self.calculate_avg_turnover_rate(supplier_id)
            
            # تحويل معدل الدوران إلى معامل من 0 إلى 10
            # افتراض: معدل دوران 4 أو أكثر يعتبر ممتاز (10/10)
            if avg_turnover_rate >= 4:
                turnover_factor = 10
            elif avg_turnover_rate <= 0:
                turnover_factor = 0
            else:
                turnover_factor = (avg_turnover_rate / 4) * 10
            
            return turnover_factor
        
        except Exception as e:
            logger.error(f"خطأ في حساب معامل معدل دوران المخزون للمورد {supplier_id}: {str(e)}")
            return 0

    def calculate_profit_margin(self, product_id):
        """حساب هامش الربح لمنتج معين"""
        try:
            # الحصول على المنتج
            product = Product.query.get(product_id)
            
            if not product:
                return 0
            
            # حساب هامش الربح
            purchase_price = float(product.purchase_price)
            selling_price = float(product.selling_price)
            
            if purchase_price > 0:
                profit_margin = (selling_price - purchase_price) / purchase_price
            else:
                profit_margin = 0
            
            return profit_margin
        
        except Exception as e:
            logger.error(f"خطأ في حساب هامش الربح للمنتج {product_id}: {str(e)}")
            return 0

    def calculate_avg_profit_margin(self, supplier_id):
        """حساب متوسط هامش الربح لجميع منتجات مورد معين"""
        try:
            # الحصول على جميع منتجات المورد
            products = Product.query.filter_by(supplier_id=supplier_id).all()
            
            if not products:
                return 0
            
            # حساب هامش الربح لكل منتج
            profit_margins = []
            for product in products:
                profit_margin = self.calculate_profit_margin(product.id)
                profit_margins.append(profit_margin)
            
            # حساب متوسط هامش الربح
            if profit_margins:
                avg_profit_margin = sum(profit_margins) / len(profit_margins)
            else:
                avg_profit_margin = 0
            
            return avg_profit_margin
        
        except Exception as e:
            logger.error(f"خطأ في حساب متوسط هامش الربح للمورد {supplier_id}: {str(e)}")
            return 0

    def calculate_avg_profit_margin_factor(self, supplier_id):
        """حساب معامل هامش الربح (من 0 إلى 10)"""
        try:
            # حساب متوسط هامش الربح للمورد
            avg_profit_margin = self.calculate_avg_profit_margin(supplier_id)
            
            # تحويل هامش الربح إلى معامل من 0 إلى 10
            # افتراض: هامش ربح 0.5 (50%) أو أكثر يعتبر ممتاز (10/10)
            if avg_profit_margin >= 0.5:
                profit_margin_factor = 10
            elif avg_profit_margin <= 0:
                profit_margin_factor = 0
            else:
                profit_margin_factor = (avg_profit_margin / 0.5) * 10
            
            return profit_margin_factor
        
        except Exception as e:
            logger.error(f"خطأ في حساب معامل هامش الربح للمورد {supplier_id}: {str(e)}")
            return 0

    def calculate_strategic_importance_factor(self, supplier_id):
        """حساب معامل الأهمية الاستراتيجية (من 0 إلى 10)"""
        try:
            # الحصول على المورد
            supplier = Supplier.query.get(supplier_id)
            
            if not supplier:
                return 0
            
            # الأهمية الاستراتيجية مخزنة مباشرة في جدول الموردين
            strategic_importance = float(supplier.strategic_importance)
            
            return strategic_importance
        
        except Exception as e:
            logger.error(f"خطأ في حساب معامل الأهمية الاستراتيجية للمورد {supplier_id}: {str(e)}")
            return 0

    def calculate_due_date_factor(self, supplier_id):
        """حساب معامل تاريخ الاستحقاق (من 0 إلى 10)"""
        try:
            # الحصول على جميع المستحقات غير المسددة للمورد
            payables = Payable.query.filter(
                Payable.supplier_id == supplier_id,
                Payable.status.in_(['pending', 'partial'])
            ).all()
            
            if not payables:
                return 0
            
            # حساب عدد الأيام المتبقية حتى تاريخ الاستحقاق لكل مستحق
            today = datetime.now().date()
            days_to_due = []
            
            for payable in payables:
                due_date = payable.due_date
                days = (due_date - today).days
                days_to_due.append(days)
            
            # حساب متوسط عدد الأيام المتبقية
            if days_to_due:
                avg_days_to_due = sum(days_to_due) / len(days_to_due)
            else:
                avg_days_to_due = 0
            
            # تحويل عدد الأيام إلى معامل من 0 إلى 10
            # افتراض: المستحقات المتأخرة (-30 يوم أو أقل) تأخذ أعلى أولوية (10/10)
            # المستحقات التي موعدها بعد 60 يوم أو أكثر تأخذ أقل أولوية (0/10)
            if avg_days_to_due <= -30:
                due_date_factor = 10
            elif avg_days_to_due >= 60:
                due_date_factor = 0
            else:
                # معادلة خطية لتحويل عدد الأيام من [-30, 60] إلى [10, 0]
                due_date_factor = 10 - ((avg_days_to_due + 30) / 90) * 10
            
            return due_date_factor
        
        except Exception as e:
            logger.error(f"خطأ في حساب معامل تاريخ الاستحقاق للمورد {supplier_id}: {str(e)}")
            return 0

    def calculate_priority_score(self, supplier_id):
        """حساب درجة الأولوية الإجمالية للمورد"""
        try:
            # حساب معاملات المعايير المختلفة
            turnover_factor = self.calculate_turnover_factor(supplier_id)
            profit_margin_factor = self.calculate_avg_profit_margin_factor(supplier_id)
            strategic_importance_factor = self.calculate_strategic_importance_factor(supplier_id)
            due_date_factor = self.calculate_due_date_factor(supplier_id)
            
            # حساب درجة الأولوية الإجمالية باستخدام الأوزان النسبية
            priority_score = (
                turnover_factor * (self.settings['turnover_weight'] / 100) +
                profit_margin_factor * (self.settings['profit_margin_weight'] / 100) +
                strategic_importance_factor * (self.settings['strategic_importance_weight'] / 100) +
                due_date_factor * (self.settings['due_date_weight'] / 100)
            )
            
            # تحديد فئة الأولوية
            if priority_score >= self.settings['critical_threshold']:
                priority_category = 'critical'
            elif priority_score >= self.settings['high_threshold']:
                priority_category = 'high'
            elif priority_score >= self.settings['medium_threshold']:
                priority_category = 'medium'
            else:
                priority_category = 'low'
            
            return priority_score, priority_category
        
        except Exception as e:
            logger.error(f"خطأ في حساب درجة الأولوية للمورد {supplier_id}: {str(e)}")
            return 0, 'low'

    def calculate_all_priorities(self, user_id):
        """حساب أولويات جميع الموردين الذين لديهم مستحقات غير مسددة"""
        try:
            # الحصول على جميع الموردين الذين لديهم مستحقات غير مسددة
            suppliers_with_payables = db.session.query(Supplier).join(
                Payable, Supplier.id == Payable.supplier_id
            ).filter(
                Payable.status.in_(['pending', 'partial'])
            ).distinct().all()
            
            # حذف حسابات الأولوية السابقة
            PriorityCalculation.query.delete()
            db.session.commit()
            
            # حساب الأولوية لكل مورد
            for supplier in suppliers_with_payables:
                # حساب درجة الأولوية
                priority_score, priority_category = self.calculate_priority_score(supplier.id)
                
                # حساب إجمالي المستحقات غير المسددة
                total_payable = db.session.query(db.func.sum(
                    Payable.amount - Payable.paid_amount
                )).filter(
                    Payable.supplier_id == supplier.id,
                    Payable.status.in_(['pending', 'partial'])
                ).scalar() or 0
                
                # حفظ حساب الأولوية
                priority_calc = PriorityCalculation(
                    supplier_id=supplier.id,
                    calculation_date=datetime.now().date(),
                    turnover_factor=self.calculate_turnover_factor(supplier.id),
                    profit_margin_factor=self.calculate_avg_profit_margin_factor(supplier.id),
                    strategic_importance_factor=self.calculate_strategic_importance_factor(supplier.id),
                    due_date_factor=self.calculate_due_date_factor(supplier.id),
                    priority_score=priority_score,
                    priority_category=priority_category,
                    total_payable=total_payable,
                    created_by=user_id
                )
                
                db.session.add(priority_calc)
            
            db.session.commit()
            
            return True
        
        except Exception as e:
            logger.error(f"خطأ في حساب أولويات جميع الموردين: {str(e)}")
            db.session.rollback()
            return False

    def calculate_suggested_payments(self, user_id):
        """حساب خطة السداد المقترحة بناءً على الأولويات والميزانية المتاحة"""
        try:
            # التأكد من وجود حسابات الأولوية
            priority_calcs = PriorityCalculation.query.all()
            if not priority_calcs:
                # حساب الأولويات إذا لم تكن موجودة
                self.calculate_all_priorities(user_id)
                priority_calcs = PriorityCalculation.query.all()
            
            # حذف المدفوعات المقترحة السابقة
            SuggestedPayment.query.delete()
            db.session.commit()
            
            # الحصول على الميزانية المتاحة
            available_budget = self.settings['available_budget']
            
            # ترتيب الموردين حسب الأولوية
            priority_calcs = sorted(
                priority_calcs,
                key=lambda x: (
                    # ترتيب تنازلي حسب فئة الأولوية
                    {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x.priority_category],
                    # ثم ترتيب تنازلي حسب درجة الأولوية
                    float(x.priority_score)
                ),
                reverse=True
            )
            
            # حساب المدفوعات المقترحة
            remaining_budget = available_budget
            for priority_calc in priority_calcs:
                supplier_id = priority_calc.supplier_id
                total_payable = float(priority_calc.total_payable)
                
                # الحصول على المستحقات غير المسددة للمورد
                payables = Payable.query.filter(
                    Payable.supplier_id == supplier_id,
                    Payable.status.in_(['pending', 'partial'])
                ).order_by(Payable.due_date).all()
                
                # حساب المبلغ المقترح للسداد
                if priority_calc.priority_category == 'critical':
                    # سداد 100% للأولوية القصوى
                    suggested_percentage = 1.0
                elif priority_calc.priority_category == 'high':
                    # سداد 75% للأولوية العالية
                    suggested_percentage = 0.75
                elif priority_calc.priority_category == 'medium':
                    # سداد 50% للأولوية المتوسطة
                    suggested_percentage = 0.5
                else:
                    # سداد 25% للأولوية المنخفضة
                    suggested_percentage = 0.25
                
                suggested_amount = min(total_payable * suggested_percentage, remaining_budget)
                
                if suggested_amount > 0:
                    # إنشاء دفعة مقترحة
                    suggested_payment = SuggestedPayment(
                        supplier_id=supplier_id,
                        calculation_date=datetime.now().date(),
                        payment_date=self.settings['payment_date'],
                        total_payable=total_payable,
                        suggested_amount=suggested_amount,
                        priority_category=priority_calc.priority_category,
                        priority_score=priority_calc.priority_score,
                        notes=f"دفعة مقترحة بنسبة {suggested_percentage * 100:.0f}% من إجمالي المستحقات",
                        created_by=user_id
                    )
                    
                    db.session.add(suggested_payment)
                    
                    # تحديث الميزانية المتبقية
                    remaining_budget -= suggested_amount
                
                # التوقف إذا نفدت الميزانية
                if remaining_budget <= 0:
                    break
            
            db.session.commit()
            
            return True
        
        except Exception as e:
            logger.error(f"خطأ في حساب خطة السداد المقترحة: {str(e)}")
            db.session.rollback()
            return False

    def get_priority_statistics(self):
        """الحصول على إحصائيات الأولويات"""
        try:
            # الحصول على عدد الموردين في كل فئة أولوية
            priority_counts = {
                'critical': PriorityCalculation.query.filter_by(priority_category='critical').count(),
                'high': PriorityCalculation.query.filter_by(priority_category='high').count(),
                'medium': PriorityCalculation.query.filter_by(priority_category='medium').count(),
                'low': PriorityCalculation.query.filter_by(priority_category='low').count()
            }
            
            # الحصول على إجمالي المستحقات في كل فئة أولوية
            priority_amounts = {}
            for category in ['critical', 'high', 'medium', 'low']:
                total = db.session.query(db.func.sum(PriorityCalculation.total_payable)).filter(
                    PriorityCalculation.priority_category == category
                ).scalar() or 0
                priority_amounts[category] = float(total)
            
            # الحصول على إجمالي المستحقات
            total_payable = sum(priority_amounts.values())
            
            # حساب النسب المئوية
            priority_percentages = {}
            for category in ['critical', 'high', 'medium', 'low']:
                if total_payable > 0:
                    priority_percentages[category] = (priority_amounts[category] / total_payable) * 100
                else:
                    priority_percentages[category] = 0
            
            return {
                'counts': priority_counts,
                'amounts': priority_amounts,
                'percentages': priority_percentages,
                'total': total_payable
            }
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات الأولويات: {str(e)}")
            return {
                'counts': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'amounts': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'percentages': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'total': 0
            }
