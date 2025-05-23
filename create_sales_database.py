import sqlite3
import random
from datetime import datetime, timedelta

# List of product names for variety
products = [
    'Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Mouse', 'Keyboard', 
    'Monitor', 'Printer', 'Camera', 'Speaker', 'Charger', 'External Hard Drive',
    'USB Drive', 'Router', 'Webcam', 'Microphone', 'Projector', 'Smartwatch'
]

def random_date(start_date, end_date):
    """Generate a random date between start_date and end_date."""
    time_between = end_date - start_date
    days_between = time_between.days
    random_number_of_days = random.randrange(days_between)
    return start_date + timedelta(days=random_number_of_days)

def create_sales_data():
    """Create a SQLite database with 50 random sales records over the past 3 months."""
    # Connect to SQLite database (creates a new database if it doesn't exist)
    conn = sqlite3.connect('product_sales.db')
    cursor = conn.cursor()
    
    # Create sales table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        date_sold TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)
    
    # Clear any existing data
    cursor.execute("DELETE FROM sales")
    
    # Set date range for the past 3 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # Approximately 3 months
    
    # Generate 50 random sales records
    for _ in range(50):
        product = random.choice(products)
        sale_date = random_date(start_date, end_date).strftime('%Y-%m-%d')
        price = round(random.uniform(10.0, 1500.0), 2)  # Random price between $10 and $1500
        cursor.execute("INSERT INTO sales (product_name, date_sold, price) VALUES (?, ?, ?)", 
                      (product, sale_date, price))
    
    conn.commit()
    conn.close()
    print("Database created with 50 sales records.")

if __name__ == "__main__":
    create_sales_data()
