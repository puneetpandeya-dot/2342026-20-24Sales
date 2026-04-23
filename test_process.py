from app import process_sales_data
import os

csv_path = r"e:\Sales Data\sales_data.csv"
if os.path.exists(csv_path):
    try:
        results = process_sales_data(csv_path)
        print("Processing Successful!")
        print(f"Total Revenue: {results['summary']['total_revenue']}")
        print(f"Top Product: {results['summary']['top_product']}")
        print(f"Highlights count: {len(results['highlights'])}")
        print(f"Weekly report weeks: {len(results['weekly_report'])}")
    except Exception as e:
        print(f"Processing Failed: {e}")
else:
    print("CSV file not found.")
