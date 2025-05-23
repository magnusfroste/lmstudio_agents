import sqlite3
from datetime import datetime

def get_sales_by_month(month: str) -> str:
    """Retrieve total sales for a specified month from the product sales database.
    Month should be in 'YYYY-MM' format (e.g., '2025-01')."""
    try:
        conn = sqlite3.connect('/Users/mafr/Code/lmstudio/product_sales.db')
        cursor = conn.cursor()
        
        # Query to sum the prices for the specified month
        query = """
        SELECT SUM(price) as total_sales
        FROM sales
        WHERE strftime('%Y-%m', date_sold) = ?
        """
        cursor.execute(query, (month,))
        result = cursor.fetchone()
        total_sales = result[0] if result[0] is not None else 0.0
        
        # Also get the number of items sold in that month
        cursor.execute("SELECT COUNT(*) FROM sales WHERE strftime('%Y-%m', date_sold) = ?", (month,))
        item_count = cursor.fetchone()[0]
        
        conn.close()
        
        if item_count > 0:
            return f"In {month}, there were {item_count} items sold, generating a total revenue of ${total_sales:.2f}."
        else:
            return f"No sales data found for {month}."
    except Exception as e:
        return f"Error accessing sales data: {str(e)}"

def list_all_sold_products() -> str:
    """Retrieve a list of all unique products sold along with the total quantity sold for each."""
    try:
        conn = sqlite3.connect('/Users/mafr/Code/lmstudio/product_sales.db')
        cursor = conn.cursor()
        
        # Query to get unique products and their count
        query = """
        SELECT product_name, COUNT(*) as quantity_sold, SUM(price) as total_revenue
        FROM sales
        GROUP BY product_name
        ORDER BY quantity_sold DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        conn.close()
        
        if results:
            response = "Here are the products sold along with the quantity sold and total revenue:\n"
            for product, qty, revenue in results:
                response += f"- {product}: {qty} units sold, total revenue ${revenue:.2f}\n"
            return response
        else:
            return "No products found in the sales database."
    except Exception as e:
        return f"Error accessing sales data: {str(e)}"

def get_top_expensive_products(limit: int = 5) -> str:
    """Retrieve the top N most expensive products sold based on individual sale price.
    Default limit is 5 if not specified."""
    try:
        conn = sqlite3.connect('/Users/mafr/Code/lmstudio/product_sales.db')
        cursor = conn.cursor()
        
        # Query to get the top N most expensive individual sales
        query = """
        SELECT product_name, price, date_sold
        FROM sales
        ORDER BY price DESC
        LIMIT ?
        """
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        conn.close()
        
        if results:
            response = f"Here are the top {limit} most expensive individual product sales:\n"
            for i, (product, price, date) in enumerate(results, 1):
                response += f"{i}. {product} sold for ${price:.2f} on {date}\n"
            return response
        else:
            return "No sales data found in the database."
    except Exception as e:
        return f"Error accessing sales data: {str(e)}"
