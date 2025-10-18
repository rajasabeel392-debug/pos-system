from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from sqlalchemy import func, and_, or_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pos_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='staff')  # admin, staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=10)
    gst_rate = db.Column(db.Float, default=18.0)  # GST percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    gst_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    gst_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Van(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    driver_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    license_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoadForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_type = db.Column(db.String(10), nullable=False)  # 'in' or 'out'
    van_id = db.Column(db.Integer, db.ForeignKey('van.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    van = db.relationship('Van', backref='load_forms')
    product = db.relationship('Product', backref='load_forms')
    user = db.relationship('User', backref='load_forms')

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    van_id = db.Column(db.Integer, db.ForeignKey('van.id'))
    total_amount = db.Column(db.Float, nullable=False)
    gst_amount = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    final_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), default='cash')
    is_gst_invoice = db.Column(db.Boolean, default=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    customer = db.relationship('Customer', backref='sales')
    van = db.relationship('Van', backref='sales')
    user = db.relationship('User', backref='sales')

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    gst_rate = db.Column(db.Float, default=18.0)
    
    # Relationships
    sale = db.relationship('Sale', backref='sale_items')
    product = db.relationship('Product', backref='sale_items')

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    gst_amount = db.Column(db.Float, default=0)
    final_amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    supplier = db.relationship('Supplier', backref='purchases')
    user = db.relationship('User', backref='purchases')

class PurchaseItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    
    # Relationships
    purchase = db.relationship('Purchase', backref='purchase_items')
    product = db.relationship('Product', backref='purchase_items')

class Return(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    return_number = db.Column(db.String(50), unique=True, nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    van_id = db.Column(db.Integer, db.ForeignKey('van.id'))
    total_amount = db.Column(db.Float, nullable=False)
    gst_amount = db.Column(db.Float, default=0)
    final_amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    sale = db.relationship('Sale', backref='returns')
    customer = db.relationship('Customer', backref='returns')
    van = db.relationship('Van', backref='returns')
    user = db.relationship('User', backref='returns')

class ReturnItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('return.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    gst_rate = db.Column(db.Float, default=18.0)
    
    # Relationships
    return_obj = db.relationship('Return', backref='return_items')
    product = db.relationship('Product', backref='return_items')

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    sku = StringField('SKU', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    cost_price = FloatField('Cost Price', validators=[DataRequired()])
    selling_price = FloatField('Selling Price', validators=[DataRequired()])
    stock_quantity = IntegerField('Stock Quantity', default=0)
    min_stock_level = IntegerField('Min Stock Level', default=10)
    gst_rate = FloatField('GST Rate (%)', default=18.0)
    submit = SubmitField('Add Product')

class LoadFormForm(FlaskForm):
    form_type = SelectField('Type', choices=[('in', 'Load In'), ('out', 'Load Out')], validators=[DataRequired()])
    van_id = SelectField('Van', coerce=int, validators=[DataRequired()])
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    date = DateField('Date', default=date.today, validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')

class SaleForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int)
    van_id = SelectField('Van', coerce=int)
    payment_method = SelectField('Payment Method', choices=[('cash', 'Cash'), ('card', 'Card'), ('upi', 'UPI')], validators=[DataRequired()])
    is_gst_invoice = SelectField('Invoice Type', choices=[('true', 'GST Invoice'), ('false', 'Non-GST Invoice')], validators=[DataRequired()])
    submit = SubmitField('Create Sale')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

class VanForm(FlaskForm):
    name = StringField('Van Name', validators=[DataRequired(), Length(min=1, max=100)])
    driver_name = StringField('Driver Name', validators=[DataRequired(), Length(min=1, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    license_number = StringField('License Number', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('Add Van')

class ExcelImportForm(FlaskForm):
    file = FileField('Excel File', validators=[
        FileRequired(),
        FileAllowed(['xlsx', 'xls'], 'Only Excel files are allowed!')
    ])
    import_type = SelectField('Import Type', choices=[
        ('products', 'Products'),
        ('customers', 'Customers'),
        ('suppliers', 'Suppliers'),
        ('vans', 'Vans')
    ], validators=[DataRequired()])
    submit = SubmitField('Import Data')

class ReturnForm(FlaskForm):
    sale_id = SelectField('Original Sale', coerce=int, validators=[DataRequired()])
    reason = TextAreaField('Return Reason', validators=[DataRequired()])
    submit = SubmitField('Create Return')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def dashboard():
    # Dashboard statistics
    total_products = Product.query.count()
    low_stock_products = Product.query.filter(Product.stock_quantity <= Product.min_stock_level).count()
    total_sales_today = db.session.query(func.sum(Sale.final_amount)).filter(
        func.date(Sale.date) == date.today()
    ).scalar() or 0
    
    recent_sales = Sale.query.order_by(Sale.date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_products=total_products,
                         low_stock_products=low_stock_products,
                         total_sales_today=total_sales_today,
                         recent_sales=recent_sales)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Verify current password
        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect!', 'error')
            return render_template('change_password.html', form=form)
        
        # Check if new password and confirm password match
        if form.new_password.data != form.confirm_password.data:
            flash('New password and confirm password do not match!', 'error')
            return render_template('change_password.html', form=form)
        
        # Update password
        current_user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html', form=form)

@app.route('/vans')
@login_required
def vans():
    vans = Van.query.order_by(Van.created_at.desc()).all()
    return render_template('vans.html', vans=vans)

@app.route('/vans/add', methods=['GET', 'POST'])
@login_required
def add_van():
    form = VanForm()
    if form.validate_on_submit():
        van = Van(
            name=form.name.data,
            driver_name=form.driver_name.data,
            phone=form.phone.data,
            license_number=form.license_number.data
        )
        db.session.add(van)
        db.session.commit()
        flash('Van added successfully!')
        return redirect(url_for('vans'))
    return render_template('add_van.html', form=form)

@app.route('/vans/<int:van_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_van(van_id):
    van = Van.query.get_or_404(van_id)
    form = VanForm(obj=van)
    if form.validate_on_submit():
        van.name = form.name.data
        van.driver_name = form.driver_name.data
        van.phone = form.phone.data
        van.license_number = form.license_number.data
        db.session.commit()
        flash('Van updated successfully!')
        return redirect(url_for('vans'))
    return render_template('edit_van.html', form=form, van=van)

@app.route('/vans/<int:van_id>/delete', methods=['POST'])
@login_required
def delete_van(van_id):
    van = Van.query.get_or_404(van_id)
    
    # Check if van has any sales or load forms
    if van.sales or van.load_forms:
        flash('Cannot delete van with existing sales or load forms!', 'error')
        return redirect(url_for('vans'))
    
    db.session.delete(van)
    db.session.commit()
    flash('Van deleted successfully!')
    return redirect(url_for('vans'))

@app.route('/excel_import', methods=['GET', 'POST'])
@login_required
def excel_import():
    form = ExcelImportForm()
    
    if form.validate_on_submit():
        try:
            # Save uploaded file
            filename = secure_filename(form.file.data.filename)
            file_path = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            form.file.data.save(file_path)
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            import_type = form.import_type.data
            success_count = 0
            error_count = 0
            errors = []
            
            if import_type == 'products':
                success_count, error_count, errors = import_products(df)
            elif import_type == 'customers':
                success_count, error_count, errors = import_customers(df)
            elif import_type == 'suppliers':
                success_count, error_count, errors = import_suppliers(df)
            elif import_type == 'vans':
                success_count, error_count, errors = import_vans(df)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            if success_count > 0:
                flash(f'Successfully imported {success_count} {import_type}!', 'success')
            if error_count > 0:
                flash(f'{error_count} records failed to import. Check the errors below.', 'error')
                for error in errors[:10]:  # Show first 10 errors
                    flash(error, 'error')
            
            return redirect(url_for('excel_import'))
            
        except Exception as e:
            flash(f'Error importing file: {str(e)}', 'error')
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
    
    return render_template('excel_import.html', form=form)

@app.route('/download_sample/<file_type>')
@login_required
def download_sample(file_type):
    if file_type == 'products':
        sample_data = {
            'name': ['Rice 1kg', 'Wheat Flour 1kg', 'Sugar 1kg'],
            'sku': ['RICE001', 'WHEAT001', 'SUGAR001'],
            'category': ['Food', 'Food', 'Food'],
            'cost_price': [45.0, 35.0, 40.0],
            'selling_price': [55.0, 42.0, 48.0],
            'stock_quantity': [100, 80, 60],
            'min_stock_level': [20, 15, 10],
            'gst_rate': [5.0, 5.0, 5.0]
        }
    elif file_type == 'customers':
        sample_data = {
            'name': ['ABC Traders', 'XYZ Enterprises', 'DEF Stores'],
            'phone': ['9876543210', '9876543211', '9876543212'],
            'email': ['abc@traders.com', 'xyz@enterprises.com', 'def@stores.com'],
            'address': ['123 Main St', '456 Business Ave', '789 Market Rd'],
            'gst_number': ['29ABCDE1234F1Z5', '29XYZAB5678C2D6', '29DEFGH9012E3F7']
        }
    elif file_type == 'suppliers':
        sample_data = {
            'name': ['Supplier A', 'Supplier B', 'Supplier C'],
            'contact_person': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'phone': ['9876543210', '9876543211', '9876543212'],
            'email': ['john@suppliera.com', 'jane@supplierb.com', 'bob@supplierc.com'],
            'address': ['123 Supplier St', '456 Vendor Ave', '789 Distributor Rd'],
            'gst_number': ['29SUPPLIER1234F1Z5', '29VENDOR5678C2D6', '29DISTRIBUTOR9012E3F7']
        }
    elif file_type == 'vans':
        sample_data = {
            'name': ['Van-001', 'Van-002', 'Van-003'],
            'driver_name': ['Raj Kumar', 'Suresh Singh', 'Amit Sharma'],
            'phone': ['9876543210', '9876543211', '9876543212'],
            'license_number': ['DL01AB1234', 'DL02CD5678', 'DL03EF9012']
        }
    else:
        flash('Invalid file type!', 'error')
        return redirect(url_for('excel_import'))
    
    df = pd.DataFrame(sample_data)
    filename = f'sample_{file_type}.xlsx'
    df.to_excel(filename, index=False)
    
    return send_file(filename, as_attachment=True, download_name=filename)

@app.route('/returns')
@login_required
def returns():
    returns = Return.query.order_by(Return.date.desc()).all()
    return render_template('returns.html', returns=returns)

@app.route('/returns/add', methods=['GET', 'POST'])
@login_required
def add_return():
    form = ReturnForm()
    form.sale_id.choices = [(s.id, f"{s.invoice_number} - {s.customer.name if s.customer else 'Walk-in'} ({s.date.strftime('%Y-%m-%d')})") for s in Sale.query.order_by(Sale.date.desc()).all()]
    
    if form.validate_on_submit():
        # Generate return number
        return_number = f"RET{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get original sale details
        original_sale = Sale.query.get(form.sale_id.data)
        
        return_obj = Return(
            return_number=return_number,
            sale_id=form.sale_id.data,
            customer_id=original_sale.customer_id,
            van_id=original_sale.van_id,
            total_amount=0.0,  # Will be updated when items are added
            gst_amount=0.0,
            final_amount=0.0,  # Will be updated when items are added
            reason=form.reason.data,
            created_by=current_user.id
        )
        
        db.session.add(return_obj)
        db.session.commit()
        
        return redirect(url_for('add_return_items', return_id=return_obj.id))
    
    return render_template('add_return.html', form=form)

@app.route('/returns/<int:return_id>/items', methods=['GET', 'POST'])
@login_required
def add_return_items(return_id):
    return_obj = Return.query.get_or_404(return_id)
    original_sale = return_obj.sale
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        
        # Check if this product was in the original sale
        original_item = SaleItem.query.filter_by(sale_id=original_sale.id, product_id=product_id).first()
        if not original_item:
            flash('This product was not in the original sale!', 'error')
            return redirect(url_for('add_return_items', return_id=return_id))
        
        # Check if return quantity doesn't exceed original quantity
        total_returned = db.session.query(func.sum(ReturnItem.quantity)).filter_by(
            return_id=return_id, product_id=product_id
        ).scalar() or 0
        
        if total_returned + quantity > original_item.quantity:
            flash(f'Cannot return more than {original_item.quantity - total_returned} units of this product!', 'error')
            return redirect(url_for('add_return_items', return_id=return_id))
        
        product = Product.query.get(product_id)
        unit_price = original_item.unit_price
        total_price = unit_price * quantity
        
        return_item = ReturnItem(
            return_id=return_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            gst_rate=original_item.gst_rate
        )
        
        # Update product stock (add back to inventory)
        product.stock_quantity += quantity
        
        db.session.add(return_item)
        db.session.commit()
        
        flash('Item added to return successfully!')
    
    # Calculate totals
    return_items = ReturnItem.query.filter_by(return_id=return_id).all()
    subtotal = sum(item.total_price for item in return_items)
    gst_amount = sum(item.total_price * item.gst_rate / 100 for item in return_items) if original_sale.is_gst_invoice else 0
    total_amount = subtotal + gst_amount
    
    # Update return totals
    return_obj.total_amount = subtotal
    return_obj.gst_amount = gst_amount
    return_obj.final_amount = total_amount
    db.session.commit()
    
    # Get products from original sale
    original_items = SaleItem.query.filter_by(sale_id=original_sale.id).all()
    available_products = []
    for item in original_items:
        total_returned = db.session.query(func.sum(ReturnItem.quantity)).filter_by(
            return_id=return_id, product_id=item.product_id
        ).scalar() or 0
        remaining = item.quantity - total_returned
        if remaining > 0:
            available_products.append({
                'product': item.product,
                'max_quantity': remaining,
                'unit_price': item.unit_price
            })
    
    return render_template('add_return_items.html', 
                         return_obj=return_obj,
                         return_items=return_items,
                         available_products=available_products,
                         subtotal=subtotal,
                         gst_amount=gst_amount,
                         total_amount=total_amount)

@app.route('/return_receipt/<int:return_id>')
@login_required
def generate_return_receipt(return_id):
    return_obj = Return.query.get_or_404(return_id)
    return_items = ReturnItem.query.filter_by(return_id=return_id).all()
    
    return render_template('return_receipt.html', return_obj=return_obj, return_items=return_items)

def import_products(df):
    success_count = 0
    error_count = 0
    errors = []
    
    required_columns = ['name', 'sku', 'category', 'cost_price', 'selling_price']
    
    for index, row in df.iterrows():
        try:
            # Check required columns
            if not all(col in df.columns for col in required_columns):
                errors.append(f"Row {index + 2}: Missing required columns. Need: {required_columns}")
                error_count += 1
                continue
            
            # Check if product already exists
            existing_product = Product.query.filter_by(sku=row['sku']).first()
            if existing_product:
                errors.append(f"Row {index + 2}: Product with SKU '{row['sku']}' already exists")
                error_count += 1
                continue
            
            product = Product(
                name=row['name'],
                sku=row['sku'],
                category=row['category'],
                cost_price=float(row['cost_price']),
                selling_price=float(row['selling_price']),
                stock_quantity=int(row.get('stock_quantity', 0)),
                min_stock_level=int(row.get('min_stock_level', 10)),
                gst_rate=float(row.get('gst_rate', 18.0))
            )
            
            db.session.add(product)
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {index + 2}: {str(e)}")
            error_count += 1
    
    if success_count > 0:
        db.session.commit()
    
    return success_count, error_count, errors

def import_customers(df):
    success_count = 0
    error_count = 0
    errors = []
    
    required_columns = ['name']
    
    for index, row in df.iterrows():
        try:
            if 'name' not in df.columns:
                errors.append(f"Row {index + 2}: Missing 'name' column")
                error_count += 1
                continue
            
            customer = Customer(
                name=row['name'],
                phone=row.get('phone', ''),
                email=row.get('email', ''),
                address=row.get('address', ''),
                gst_number=row.get('gst_number', '')
            )
            
            db.session.add(customer)
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {index + 2}: {str(e)}")
            error_count += 1
    
    if success_count > 0:
        db.session.commit()
    
    return success_count, error_count, errors

def import_suppliers(df):
    success_count = 0
    error_count = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            if 'name' not in df.columns:
                errors.append(f"Row {index + 2}: Missing 'name' column")
                error_count += 1
                continue
            
            supplier = Supplier(
                name=row['name'],
                contact_person=row.get('contact_person', ''),
                phone=row.get('phone', ''),
                email=row.get('email', ''),
                address=row.get('address', ''),
                gst_number=row.get('gst_number', '')
            )
            
            db.session.add(supplier)
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {index + 2}: {str(e)}")
            error_count += 1
    
    if success_count > 0:
        db.session.commit()
    
    return success_count, error_count, errors

def import_vans(df):
    success_count = 0
    error_count = 0
    errors = []
    
    required_columns = ['name', 'driver_name', 'phone', 'license_number']
    
    for index, row in df.iterrows():
        try:
            if not all(col in df.columns for col in required_columns):
                errors.append(f"Row {index + 2}: Missing required columns. Need: {required_columns}")
                error_count += 1
                continue
            
            van = Van(
                name=row['name'],
                driver_name=row['driver_name'],
                phone=row['phone'],
                license_number=row['license_number']
            )
            
            db.session.add(van)
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {index + 2}: {str(e)}")
            error_count += 1
    
    if success_count > 0:
        db.session.commit()
    
    return success_count, error_count, errors

@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            sku=form.sku.data,
            category=form.category.data,
            cost_price=form.cost_price.data,
            selling_price=form.selling_price.data,
            stock_quantity=form.stock_quantity.data,
            min_stock_level=form.min_stock_level.data,
            gst_rate=form.gst_rate.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('products'))
    return render_template('add_product.html', form=form)

@app.route('/load_forms')
@login_required
def load_forms():
    forms = LoadForm.query.order_by(LoadForm.date.desc()).all()
    return render_template('load_forms.html', forms=forms)

@app.route('/load_forms/add', methods=['GET', 'POST'])
@login_required
def add_load_form():
    form = LoadFormForm()
    form.van_id.choices = [(v.id, v.name) for v in Van.query.all()]
    form.product_id.choices = [(p.id, f"{p.name} ({p.sku})") for p in Product.query.all()]
    
    if form.validate_on_submit():
        load_form = LoadForm(
            form_type=form.form_type.data,
            van_id=form.van_id.data,
            product_id=form.product_id.data,
            quantity=form.quantity.data,
            date=form.date.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        # Update product stock
        product = Product.query.get(form.product_id.data)
        if form.form_type.data == 'in':
            product.stock_quantity += form.quantity.data
        else:  # out
            if product.stock_quantity >= form.quantity.data:
                product.stock_quantity -= form.quantity.data
            else:
                flash('Insufficient stock!')
                return render_template('add_load_form.html', form=form)
        
        db.session.add(load_form)
        db.session.commit()
        flash('Load form submitted successfully!')
        return redirect(url_for('load_forms'))
    
    return render_template('add_load_form.html', form=form)

@app.route('/stock_report')
@login_required
def stock_report():
    products = Product.query.all()
    return render_template('stock_report.html', products=products)

@app.route('/monthly_stock_report')
@login_required
def monthly_stock_report():
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    year, month_num = month.split('-')
    
    # Get stock movements for the month
    load_forms = LoadForm.query.filter(
        and_(
            func.extract('year', LoadForm.date) == int(year),
            func.extract('month', LoadForm.date) == int(month_num)
        )
    ).all()
    
    return render_template('monthly_stock_report.html', 
                         load_forms=load_forms, 
                         selected_month=month)

@app.route('/van_sales_monthly')
@login_required
def van_sales_monthly():
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    year, month_num = month.split('-')
    
    van_sales = db.session.query(
        Van.name,
        func.sum(Sale.final_amount).label('total_sales'),
        func.count(Sale.id).label('total_orders')
    ).join(Sale).filter(
        and_(
            func.extract('year', Sale.date) == int(year),
            func.extract('month', Sale.date) == int(month_num)
        )
    ).group_by(Van.id, Van.name).all()
    
    return render_template('van_sales_monthly.html', 
                         van_sales=van_sales, 
                         selected_month=month)

@app.route('/investment_report')
@login_required
def investment_report():
    # Calculate total investment (purchases)
    total_purchases = db.session.query(func.sum(Purchase.final_amount)).scalar() or 0
    
    # Calculate total sales
    total_sales = db.session.query(func.sum(Sale.final_amount)).scalar() or 0
    
    # Calculate profit/loss
    profit_loss = total_sales - total_purchases
    
    return render_template('investment_report.html',
                         total_purchases=total_purchases,
                         total_sales=total_sales,
                         profit_loss=profit_loss)

@app.route('/sales')
@login_required
def sales():
    sales = Sale.query.order_by(Sale.date.desc()).all()
    return render_template('sales.html', sales=sales)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    form = SaleForm()
    form.customer_id.choices = [(0, 'Walk-in Customer')] + [(c.id, c.name) for c in Customer.query.all()]
    form.van_id.choices = [(0, 'No Van')] + [(v.id, v.name) for v in Van.query.all()]
    
    if form.validate_on_submit():
        # Generate invoice number
        invoice_number = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        sale = Sale(
            invoice_number=invoice_number,
            customer_id=form.customer_id.data if form.customer_id.data != 0 else None,
            van_id=form.van_id.data if form.van_id.data != 0 else None,
            total_amount=0.0,  # Initialize with 0, will be updated when items are added
            gst_amount=0.0,
            discount_amount=0.0,
            final_amount=0.0,  # Initialize with 0, will be updated when items are added
            payment_method=form.payment_method.data,
            is_gst_invoice=form.is_gst_invoice.data == 'true',  # Convert string to boolean
            created_by=current_user.id
        )
        
        db.session.add(sale)
        db.session.commit()
        
        return redirect(url_for('add_sale_items', sale_id=sale.id))
    
    return render_template('add_sale.html', form=form)

@app.route('/sales/<int:sale_id>/items', methods=['GET', 'POST'])
@login_required
def add_sale_items(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        
        product = Product.query.get(product_id)
        if product and product.stock_quantity >= quantity:
            unit_price = product.selling_price
            total_price = unit_price * quantity
            
            sale_item = SaleItem(
                sale_id=sale_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                gst_rate=product.gst_rate
            )
            
            # Update product stock
            product.stock_quantity -= quantity
            
            db.session.add(sale_item)
            db.session.commit()
            
            flash('Item added successfully!')
        else:
            flash('Insufficient stock!')
    
    # Calculate totals
    sale_items = SaleItem.query.filter_by(sale_id=sale_id).all()
    subtotal = sum(item.total_price for item in sale_items)
    gst_amount = sum(item.total_price * item.gst_rate / 100 for item in sale_items) if sale.is_gst_invoice else 0
    total_amount = subtotal + gst_amount
    
    # Update sale totals
    sale.total_amount = subtotal
    sale.gst_amount = gst_amount
    sale.final_amount = total_amount
    db.session.commit()
    
    products = Product.query.filter(Product.stock_quantity > 0).all()
    
    return render_template('add_sale_items.html', 
                         sale=sale, 
                         sale_items=sale_items,
                         products=products,
                         subtotal=subtotal,
                         gst_amount=gst_amount,
                         total_amount=total_amount)

@app.route('/invoice/<int:sale_id>')
@login_required
def generate_invoice(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    sale_items = SaleItem.query.filter_by(sale_id=sale_id).all()
    
    return render_template('invoice.html', sale=sale, sale_items=sale_items)

@app.route('/export_excel/<report_type>')
@login_required
def export_excel(report_type):
    if report_type == 'stock':
        products = Product.query.all()
        df = pd.DataFrame([{
            'SKU': p.sku,
            'Product Name': p.name,
            'Category': p.category,
            'Stock Quantity': p.stock_quantity,
            'Min Stock Level': p.min_stock_level,
            'Cost Price': p.cost_price,
            'Selling Price': p.selling_price
        } for p in products])
        
        filename = f'stock_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
        df.to_excel(filename, index=False)
        
        return send_file(filename, as_attachment=True)
    
    elif report_type == 'sales':
        sales = Sale.query.all()
        df = pd.DataFrame([{
            'Invoice Number': s.invoice_number,
            'Date': s.date.strftime('%Y-%m-%d'),
            'Customer': s.customer.name if s.customer else 'Walk-in',
            'Van': s.van.name if s.van else 'N/A',
            'Total Amount': s.total_amount,
            'GST Amount': s.gst_amount,
            'Final Amount': s.final_amount,
            'Payment Method': s.payment_method
        } for s in sales])
        
        filename = f'sales_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
        df.to_excel(filename, index=False)
        
        return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@pos.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True)
