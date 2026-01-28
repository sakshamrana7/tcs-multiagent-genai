"""
Database module for customer data and support tickets.
Uses SQLite for structured data storage.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "customers.db"


def init_database():
    """Initialize the SQLite database with customer and ticket tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            signup_date TEXT,
            account_status TEXT,
            account_type TEXT,
            total_orders INTEGER,
            lifetime_value REAL
        )
    """)

    # Create support tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT,
            created_date TEXT,
            resolved_date TEXT,
            category TEXT,
            priority TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT,
            amount REAL,
            status TEXT,
            items TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    conn.commit()
    conn.close()


def seed_sample_data():
    """Seed the database with sample customer data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM support_tickets")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM customers")

    # Sample customers
    customers = [
        (1, "Ema Johnson", "ema.johnson@email.com", "+1-555-0101", "2023-06-15", "active", "premium", 12, 4500.00),
        (2, "John Smith", "john.smith@email.com", "+1-555-0102", "2023-01-20", "active", "standard", 5, 1200.00),
        (3, "Sarah Chen", "sarah.chen@email.com", "+1-555-0103", "2022-11-10", "active", "premium", 25, 8900.00),
        (4, "Michael Davis", "michael.d@email.com", "+1-555-0104", "2023-09-05", "active", "standard", 3, 650.00),
        (5, "Lisa Anderson", "lisa.anderson@email.com", "+1-555-0105", "2022-03-22", "inactive", "standard", 8, 1800.00),
    ]

    cursor.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        customers
    )

    # Sample support tickets for Ema Johnson (customer_id=1)
    today = datetime.now()
    tickets = [
        (
            1, 1, "Refund request for order #5001",
            "I would like to return item received on 2024-01-10 for a refund.",
            "closed", "2024-01-11", "2024-01-18", "refund", "high"
        ),
        (
            2, 1, "Account login issues",
            "Cannot login to my account. Getting error 403.",
            "closed", "2024-01-05", "2024-01-06", "technical", "critical"
        ),
        (
            3, 1, "Shipping delay question",
            "My order #5045 hasn't arrived yet. Ordered on 2024-01-12.",
            "closed", "2024-01-16", "2024-01-17", "shipping", "medium"
        ),
        (
            4, 1, "Subscription upgrade",
            "Want to upgrade from Standard to Premium plan.",
            "open", (today - timedelta(days=2)).strftime("%Y-%m-%d"), None, "account", "low"
        ),
        (
            5, 2, "Product quality complaint",
            "Item received has defects. Requesting replacement.",
            "closed", "2024-01-08", "2024-01-15", "quality", "high"
        ),
    ]

    cursor.executemany(
        "INSERT INTO support_tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        tickets
    )

    # Sample orders
    orders = [
        (1, 1, "2024-01-10", 299.99, "delivered", json.dumps(["Wireless Earbuds", "USB Cable"])),
        (2, 1, "2024-01-12", 450.00, "delivered", json.dumps(["Laptop Stand", "Keyboard", "Mouse Pad"])),
        (3, 2, "2024-01-08", 79.99, "delivered", json.dumps(["Phone Case"])),
        (4, 3, "2024-01-15", 899.99, "processing", json.dumps(["Tablet", "Stylus"])),
    ]

    cursor.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
        orders
    )

    conn.commit()
    conn.close()


def get_customer_profile(customer_name: str) -> Dict[str, Any]:
    """Get customer profile information by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM customers WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{customer_name}%",)
    )
    customer = cursor.fetchone()

    if not customer:
        conn.close()
        return {"error": f"Customer '{customer_name}' not found"}

    customer_dict = dict(customer)

    # Fetch related orders
    cursor.execute(
        "SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC",
        (customer_dict["id"],)
    )
    customer_dict["orders"] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return customer_dict


def get_customer_support_tickets(customer_name: str) -> Dict[str, Any]:
    """Get all support tickets for a customer."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM customers WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{customer_name}%",)
    )
    customer = cursor.fetchone()

    if not customer:
        conn.close()
        return {"error": f"Customer '{customer_name}' not found"}

    customer_id = customer["id"]

    cursor.execute(
        "SELECT * FROM support_tickets WHERE customer_id = ? ORDER BY created_date DESC",
        (customer_id,)
    )
    tickets = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "customer_name": customer_name,
        "customer_id": customer_id,
        "total_tickets": len(tickets),
        "tickets": tickets
    }


def search_customers(query: str) -> List[Dict[str, Any]]:
    """Search customers by name, email, or phone."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM customers WHERE LOWER(name) LIKE LOWER(?) OR email LIKE ? OR phone LIKE ?",
        (f"%{query}%", f"%{query}%", f"%{query}%")
    )
    results = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return results


def query_database(sql_query: str) -> List[Dict[str, Any]]:
    """Execute a custom SQL query on the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Only allow SELECT queries for safety
        if not sql_query.strip().upper().startswith("SELECT"):
            conn.close()
            return {"error": "Only SELECT queries are allowed"}

        cursor.execute(sql_query)
        results = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return results
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Initialize and seed database
    init_database()
    seed_sample_data()
    print("Database initialized and seeded with sample data!")
