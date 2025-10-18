# Quick Start Guide - POS System

## 🚀 How to Start the Application

### Method 1: Using Batch File (Recommended)
1. Double-click `start_pos.bat`
2. Wait for the server to start
3. Open your browser and go to: `http://localhost:5000`

### Method 2: Using Command Line
1. Open Command Prompt in the project folder
2. Run: `python app.py`
3. Open your browser and go to: `http://localhost:5000`

## 🔑 Login Credentials
- **Username**: admin
- **Password**: admin123

## 📋 System Features

### ✅ Completed Features
- **Load Forms (In/Out)**: Track inventory movements
- **Stock Reports**: Current stock levels and alerts
- **Monthly Stock Reports**: Track stock movements by month
- **Van-wise Sales Monthly**: Sales performance by van
- **Total Investment Tracking**: Monitor purchases and investments
- **Profit/Loss Calculation**: Financial performance analysis
- **Excel Export**: Export reports to Excel format
- **Load Pass System**: Manage van loading/unloading
- **GST Invoice Generation**: Create GST-compliant invoices
- **Non-GST Invoice Option**: For non-GST transactions

### 🎯 Key Functions

1. **Dashboard**: Overview of system status and recent sales
2. **Products**: Manage product catalog with SKU, prices, and stock levels
3. **Load Forms**: Track inventory movements in/out of vans
4. **Sales**: Process sales transactions and generate invoices
5. **Reports**: Various reports including stock, sales, and financial analysis

### 📊 Sample Data Included
The system comes with sample data:
- 5 sample products (Rice, Wheat Flour, Sugar, Cooking Oil, Detergent Powder)
- 1 sample supplier (ABC Suppliers)
- 1 sample customer (XYZ Traders)
- 1 sample van (Van-001)

### 🔧 System Requirements
- Python 3.7+
- Modern web browser
- SQLite database (included)

### 📁 Project Structure
```
pos system/
├── app.py                 # Main application file
├── setup_db.py           # Database initialization
├── requirements.txt      # Python dependencies
├── start_pos.bat        # Windows batch file to start app
├── README.md            # Detailed documentation
└── templates/           # HTML templates
    ├── base.html
    ├── dashboard.html
    ├── login.html
    ├── products.html
    ├── sales.html
    ├── load_forms.html
    ├── stock_report.html
    ├── invoice.html
    └── ... (other templates)
```

## 🎉 Your POS System is Ready!

The comprehensive Point of Sale system for wholesale business is now fully functional with all the requested features:

- ✅ Load forms (in/out)
- ✅ Stock reports
- ✅ Monthly stock reports
- ✅ Van-wise sales monthly
- ✅ Total investment tracking
- ✅ Profit/loss calculation
- ✅ Excel export functionality
- ✅ Load pass system
- ✅ GST and non-GST invoice generation

**Start the application and begin managing your wholesale business!**

