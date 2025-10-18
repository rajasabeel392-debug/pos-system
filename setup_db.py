from app import app, db, User, Product, Supplier, Customer, Van
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_database():
    with app.app_context():
        # Create all tables
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
            print("Admin user created: admin / admin123")
        
        # Create sample supplier
        supplier = Supplier.query.filter_by(name='ABC Suppliers').first()
        if not supplier:
            supplier = Supplier(
                name='ABC Suppliers',
                contact_person='John Doe',
                phone='9876543210',
                email='john@abcsuppliers.com',
                address='123 Supplier Street, City',
                gst_number='29ABCDE1234F1Z5'
            )
            db.session.add(supplier)
            print("Sample supplier created")
        
        # Create sample customer
        customer = Customer.query.filter_by(name='XYZ Traders').first()
        if not customer:
            customer = Customer(
                name='XYZ Traders',
                phone='9876543211',
                email='contact@xyztraders.com',
                address='456 Customer Avenue, City',
                gst_number='29XYZAB5678C2D6'
            )
            db.session.add(customer)
            print("Sample customer created")
        
        # Create sample van
        van = Van.query.filter_by(name='Van-001').first()
        if not van:
            van = Van(
                name='Van-001',
                driver_name='Raj Kumar',
                phone='9876543212',
                license_number='DL01AB1234'
            )
            db.session.add(van)
            print("Sample van created")
        
        # Create sample products
        sample_products = [
            {
                'name': 'Rice 1kg',
                'sku': 'RICE001',
                'category': 'Food',
                'cost_price': 45.0,
                'selling_price': 55.0,
                'stock_quantity': 100,
                'min_stock_level': 20,
                'gst_rate': 5.0
            },
            {
                'name': 'Wheat Flour 1kg',
                'sku': 'WHEAT001',
                'category': 'Food',
                'cost_price': 35.0,
                'selling_price': 42.0,
                'stock_quantity': 80,
                'min_stock_level': 15,
                'gst_rate': 5.0
            },
            {
                'name': 'Sugar 1kg',
                'sku': 'SUGAR001',
                'category': 'Food',
                'cost_price': 40.0,
                'selling_price': 48.0,
                'stock_quantity': 60,
                'min_stock_level': 10,
                'gst_rate': 5.0
            },
            {
                'name': 'Cooking Oil 1L',
                'sku': 'OIL001',
                'category': 'Food',
                'cost_price': 120.0,
                'selling_price': 140.0,
                'stock_quantity': 50,
                'min_stock_level': 10,
                'gst_rate': 5.0
            },
            {
                'name': 'Detergent Powder 1kg',
                'sku': 'DET001',
                'category': 'Household',
                'cost_price': 80.0,
                'selling_price': 95.0,
                'stock_quantity': 40,
                'min_stock_level': 8,
                'gst_rate': 18.0
            }
        ]
        
        for product_data in sample_products:
            existing_product = Product.query.filter_by(sku=product_data['sku']).first()
            if not existing_product:
                product = Product(**product_data)
                db.session.add(product)
                print(f"Sample product created: {product_data['name']}")
        
        # Commit all changes
        db.session.commit()
        print("\nDatabase setup completed successfully!")
        print("\nYou can now run the application with: python app.py")
        print("Login with: admin / admin123")

if __name__ == '__main__':
    setup_database()
