# POS System - Wholesale Business Management

A comprehensive Point of Sale (POS) system designed for wholesale businesses with features for inventory management, sales tracking, and reporting.

## Features

### Core Functionality
- **Load Forms (In/Out)**: Track inventory movements in and out of vans
- **Stock Reports**: Current stock levels and low stock alerts
- **Monthly Stock Reports**: Track stock movements by month
- **Van-wise Sales Monthly**: Sales performance by van
- **Total Investment Tracking**: Monitor purchases and investments
- **Profit/Loss Calculation**: Financial performance analysis
- **Excel Export**: Export reports to Excel format
- **Load Pass System**: Manage van loading/unloading
- **GST Invoice Generation**: Create GST-compliant invoices
- **Non-GST Invoice Option**: For non-GST transactions

### User Management
- User authentication and authorization
- Role-based access control (Admin/Staff)
- Secure login system

### Inventory Management
- Product catalog with SKU management
- Stock level tracking
- Low stock alerts
- Category-wise organization
- Cost and selling price management
- GST rate configuration

### Sales Management
- Point of sale interface
- Customer management
- Van-wise sales tracking
- Multiple payment methods (Cash, Card)
- Invoice generation (GST and Non-GST)
- Sales history and reporting

### Reporting
- Real-time dashboard
- Stock reports with Excel export
- Monthly stock movement reports
- Van-wise sales analysis
- Investment and profit/loss reports
- Sales performance metrics

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**:
   ```bash
   python setup_db.py
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the System**:
   - Open your browser and go to `http://localhost:5000`
   - Login with default credentials: `admin` / `admin123`

## Default Login Credentials

- **Username**: admin
- **Password**: admin123

## System Requirements

- Python 3.7+
- SQLite (included with Python)
- Modern web browser

## Dependencies

- Flask 2.3.3 - Web framework
- Flask-SQLAlchemy 3.0.5 - Database ORM
- Flask-Login 0.6.3 - User authentication
- Flask-WTF 1.1.1 - Form handling
- WTForms 3.0.1 - Form validation
- Werkzeug 2.3.7 - WSGI utilities
- openpyxl 3.1.2 - Excel file handling
- reportlab 4.0.4 - PDF generation
- python-dateutil 2.8.2 - Date utilities
- pandas 2.1.1 - Data manipulation
- matplotlib 3.7.2 - Data visualization

## Usage Guide

### 1. Adding Products
- Go to Products → Add Product
- Fill in product details including SKU, name, category, prices, and stock levels
- Set GST rate for tax calculations

### 2. Managing Load Forms
- Go to Load Forms → Add Load Form
- Select type (Load In/Load Out)
- Choose van and product
- Enter quantity and notes
- System automatically updates stock levels

### 3. Processing Sales
- Go to Sales → New Sale
- Select customer and van
- Choose payment method and invoice type (GST/Non-GST)
- Add products to the sale
- Generate invoice

### 4. Viewing Reports
- **Stock Report**: Current inventory levels
- **Monthly Stock Report**: Stock movements by month
- **Van Sales Monthly**: Sales performance by van
- **Investment Report**: Financial overview and profit/loss

### 5. Exporting Data
- Use Excel export buttons on report pages
- Download reports in Excel format for further analysis

## Database Schema

The system uses SQLite database with the following main tables:
- Users (authentication)
- Products (inventory)
- Suppliers (vendor management)
- Customers (customer information)
- Vans (delivery vehicles)
- LoadForms (inventory movements)
- Sales (sales transactions)
- SaleItems (sale line items)
- Purchases (purchase transactions)
- PurchaseItems (purchase line items)

## Security Features

- Password hashing for secure authentication
- Session management
- Role-based access control
- Input validation and sanitization

## Customization

The system is built with Flask and can be easily customized:
- Modify templates in the `templates/` directory
- Add new features by extending the Flask routes
- Customize database models as needed
- Modify styling using Bootstrap classes

## Support

For technical support or feature requests, please contact the development team.

## License

This software is provided as-is for internal business use.
