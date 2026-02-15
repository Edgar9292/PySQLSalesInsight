import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 1. DATABASE MANAGEMENT CLASS
class SalesDatabase:
    def __init__(self, db_name):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self._create_table()
        except sqlite3.Error as e:
            print(f"❌ Connection Error: {e}")

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT NOT NULL,
                amount REAL,
                sale_date DATE
            )
        ''')
        self.conn.commit()

    def insert_sale(self, product, amount, date):
        try:
            # Using parameterized queries for security (Prevention against SQL Injection)
            query = "INSERT INTO sales (product, amount, sale_date) VALUES (?, ?, ?)"
            self.cursor.execute(query, (product, amount, date))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Error inserting data: {e}")

    def get_growth_data(self):
        try:
            query = "SELECT sale_date, amount FROM sales"
            df = pd.read_sql_query(query, self.conn)
            
            # Data Transformation
            df['sale_date'] = pd.to_datetime(df['sale_date'])
            
            # Resampling using 'ME' (Month End) for latest Pandas compatibility
            monthly_sales = df.resample('ME', on='sale_date')['amount'].sum().reset_index()
            
            # Calculating Monthly Growth Rate (%)
            monthly_sales['growth_rate'] = monthly_sales['amount'].pct_change() * 100
            return monthly_sales
        except Exception as e:
            print(f"❌ Analysis Error: {e}")
            return None

# 2. ANALYZER CLASS WITH EXPORT FEATURES
class SalesAnalyzer(SalesDatabase):
    def populate_test_data(self):
        test_sales = [
            ('Laptop', 3500, '2025-11-10'),
            ('Mouse', 150, '2025-11-25'),
            ('Monitor', 1200, '2025-12-05'),
            ('Keyboard', 300, '2025-12-20'),
            ('Gaming Chair', 1500, '2026-01-15'),
            ('Webcam', 450, '2026-01-28'),
            ('Headset', 600, '2026-02-05')
        ]
        for product, price, date in test_sales:
            self.insert_sale(product, price, date)
        print("✅ Database populated with test data!")

# --- EXECUTION ---
if __name__ == "__main__":
    # Initialize
    db = SalesAnalyzer("sales_insight.db")
    db.populate_test_data()

    # Process Data
    report = db.get_growth_data()

    if report is not None:
        print("\n--- Monthly Performance Report ---")
        print(report)

        # Export to Excel
        report.to_excel("sales_report.xlsx", index=False)
        print("\n📊 Excel report 'sales_report.xlsx' generated.")

        # Visualization
        plt.figure(figsize=(10, 6))
        plt.bar(report['sale_date'].dt.strftime('%b/%Y'), report['amount'], color='#2E59FF')
        
        plt.title('Monthly Sales Performance', fontsize=14, fontweight='bold')
        plt.xlabel('Month/Year')
        plt.ylabel('Total Revenue ($)')
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        
        # Save Chart as Image
        plt.savefig("sales_chart.png", dpi=300)
        print("📈 Chart saved as 'sales_chart.png'.")
        
        plt.show()