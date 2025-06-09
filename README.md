
# Flask Prioritization App

تطبيق Flask لإدارة أولويات الدفع للموردين والمنتجات والمخزون.

## 🧱 المتطلبات

- Python 3.9+
- pip

## 🚀 خطوات التشغيل المحلي

```bash
pip install -r requirements.txt
python fix_flask_app.py
```

ثم افتح المتصفح على:
```
http://localhost:5000
```

---

## 🌐 خطوات النشر على Render (استضافة مجانية)

### 1. ارفع المشروع على GitHub

### 2. سجل في [Render.com](https://render.com)

### 3. أنشئ Web Service جديدة:

- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python fix_flask_app.py`
- **Port**: `PORT` ← يُقرأ تلقائيًا داخل الكود

### 4. اضغط Deploy واستلم رابط الموقع!

---

## 📁 هيكل المشروع

```
.
├── fix_flask_app.py
├── requirements.txt
└── templates/
    ├── base.html
    ├── home.html
    ├── suppliers/
    ├── products/
    ├── inventory/
    ├── reports/
    ├── sales/
    └── payables/
```
