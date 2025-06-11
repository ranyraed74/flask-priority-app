from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.setting import Setting

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
@login_required
def index():
    """صفحة الإعدادات الرئيسية"""
    settings = Setting.query.all()
    return render_template('settings/index.html', settings=settings)

@settings_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل إعداد"""
    setting = Setting.query.get_or_404(id)
    
    if request.method == 'POST':
        value = request.form.get('value')
        
        # تحديث الإعداد
        setting.value = value
        setting.updated_by = current_user.id
        
        db.session.commit()
        
        flash('تم تحديث الإعداد بنجاح', 'success')
        return redirect(url_for('settings.index'))
    
    return render_template('settings/edit.html', setting=setting)

@settings_bp.route('/system')
@login_required
def system():
    """إعدادات النظام"""
    return render_template('settings/system.html')

@settings_bp.route('/backup')
@login_required
def backup():
    """نسخ احتياطي لقاعدة البيانات"""
    # إنشاء نسخة احتياطية لقاعدة البيانات
    import os
    import shutil
    from datetime import datetime
    
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'warehouse_payment_system.db')
    backup_path = os.path.join(backup_dir, f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    
    shutil.copy2(db_path, backup_path)
    
    flash(f'تم إنشاء نسخة احتياطية بنجاح: {os.path.basename(backup_path)}', 'success')
    return redirect(url_for('settings.system'))

@settings_bp.route('/restore', methods=['POST'])
@login_required
def restore():
    """استعادة قاعدة البيانات من نسخة احتياطية"""
    backup_file = request.form.get('backup_file')
    
    if not backup_file:
        flash('يرجى اختيار ملف النسخة الاحتياطية', 'danger')
        return redirect(url_for('settings.system'))
    
    # استعادة قاعدة البيانات من النسخة الاحتياطية
    import os
    import shutil
    
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backups')
    backup_path = os.path.join(backup_dir, backup_file)
    
    if not os.path.exists(backup_path):
        flash('ملف النسخة الاحتياطية غير موجود', 'danger')
        return redirect(url_for('settings.system'))
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'warehouse_payment_system.db')
    
    shutil.copy2(backup_path, db_path)
    
    flash('تم استعادة قاعدة البيانات بنجاح', 'success')
    return redirect(url_for('settings.system'))
