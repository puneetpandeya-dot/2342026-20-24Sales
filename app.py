import os
import pandas as pd
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Use an absolute path for the uploads folder to avoid issues on hosting platforms
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
    except Exception as e:
        print(f"Warning: Could not create uploads folder: {e}")

def process_sales_data(file_path):
    print(f"Processing file: {file_path}")
    # Load the data - handle spaces and quotes
    df = pd.read_csv(file_path, skipinitialspace=True, quotechar='"')
    
    # Strip whitespace from column names if any
    df.columns = [c.strip() for c in df.columns]
    
    # Clean description and other string columns
    for col in ['Description', 'InvoiceNo', 'Country']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Parse dates: dd-mm-yyyy HH:MM
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], dayfirst=True)
    
    # Calculate Revenue
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    
    # Extract Week information (Start of week - Monday)
    df['Week'] = df['InvoiceDate'].dt.to_period('W').apply(lambda r: r.start_time)
    
    # Weekly aggregation
    weekly_stats = df.groupby('Week').agg({
        'Revenue': 'sum',
        'Quantity': 'sum',
        'InvoiceNo': 'nunique',
        'CustomerID': 'nunique'
    }).reset_index()
    
    # Format Week as string for JSON
    weekly_stats['WeekStr'] = weekly_stats['Week'].dt.strftime('%d %b %Y')
    
    # Overall Summary
    total_revenue = df['Revenue'].sum()
    total_quantity = df['Quantity'].sum()
    total_orders = df['InvoiceNo'].nunique()
    total_customers = df['CustomerID'].nunique()
    
    # Top Products
    top_products_rev = df.groupby('Description')['Revenue'].sum().sort_values(ascending=False).head(5)
    top_product_name = top_products_rev.index[0] if not top_products_rev.empty else "N/A"
    
    # Best Week
    best_week_row = weekly_stats.loc[weekly_stats['Revenue'].idxmax()]
    best_week_name = best_week_row['WeekStr']
    best_week_revenue = best_week_row['Revenue']
    
    # Prepare data for return
    report_data = {
        'weekly_report': weekly_stats.to_dict(orient='records'),
        'summary': {
            'total_revenue': round(total_revenue, 2),
            'total_quantity': int(total_quantity),
            'total_orders': int(total_orders),
            'total_customers': int(total_customers),
            'top_product': top_product_name,
            'best_week': best_week_name,
            'best_week_revenue': round(best_week_revenue, 2)
        },
        'highlights': [
            f"Total revenue for the period reached {total_revenue:,.2f}.",
            f"The best performing week was starting {best_week_name} with {best_week_revenue:,.2f} in sales.",
            f"A total of {total_orders} orders were processed from {total_customers} unique customers.",
            f"The top-selling item by revenue was '{top_product_name}'."
        ]
    }
    
    return report_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        try:
            results = process_sales_data(file_path)
            return jsonify(results)
        except Exception as e:
            print(f"Error processing upload: {e}")
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
