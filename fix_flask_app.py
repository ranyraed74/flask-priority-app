from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def get_id(self):
        return str(self.id)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    category = db.Column(db.String(100))
    purchase_price = db.Column(db.Float)
    sale_price = db.Column(db.Float)
    in_stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/suppliers', methods=['GET', 'POST'])
def suppliers():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        new_supplier = Supplier(name=name, phone=phone, email=email)
        db.session.add(new_supplier)
        db.session.commit()
        return redirect(url_for('suppliers'))
    suppliers = Supplier.query.all()
    return render_template('suppliers/index.html', suppliers=suppliers)

@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        supplier_id = request.form['supplier_id']
        purchase_price = float(request.form['purchase_price'])
        sale_price = float(request.form['sale_price'])
        in_stock = int(request.form['in_stock'])
        product = Product(
            name=name, category=category, supplier_id=supplier_id,
            purchase_price=purchase_price, sale_price=sale_price, in_stock=in_stock
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))
    products = Product.query.all()
    suppliers = Supplier.query.all()
    return render_template('products/index.html', products=products, suppliers=suppliers, categories=[])

@app.route('/inventory')
def inventory():
    items = Product.query.all()
    return render_template('inventory/index.html', inventory_items=items)

@app.route('/sales')
def sales():
    months = []
    return render_template('sales/index.html', sales=[], months=months)

@app.route('/payables')
def payables():
    upcoming_dates = []
    return render_template('payables/index.html', payables=[], upcoming_dates=upcoming_dates)

@app.route('/priority/settings')
def priority_settings():
    settings = {}
    return render_template('priority/settings.html', settings=settings)

@app.route('/reports')
def reports():
    return render_template('reports/index.html')

@app.route('/inventory/add')
def inventory_add():
    return render_template('inventory/add.html')

@app.route('/suppliers/add')
def suppliers_add():
    return render_template('suppliers/add.html')

@app.route('/suppliers/delete/<int:supplier_id>')
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    return redirect(url_for('suppliers'))

@app.route('/products/delete/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))

@app.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    if request.method == 'POST':
        supplier.name = request.form['name']
        supplier.phone = request.form['phone']
        supplier.email = request.form['email']
        db.session.commit()
        return redirect(url_for('suppliers'))
    return render_template('suppliers/edit.html', supplier=supplier)

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    suppliers = Supplier.query.all()
    if request.method == 'POST':
        product.name = request.form['name']
        product.category = request.form['category']
        product.supplier_id = request.form['supplier_id']
        product.purchase_price = float(request.form['purchase_price'])
        product.sale_price = float(request.form['sale_price'])
        product.in_stock = int(request.form['in_stock'])
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('products/edit.html', product=product, suppliers=suppliers)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
