import frappe

def execute():
    # Fix all account currencies to match their company's default currency
    # This prevents ValidationError during fixture sync if the teammate changed Company currencies
    frappe.db.sql("SET SQL_SAFE_UPDATES = 0;")
    frappe.db.sql("""
        UPDATE tabAccount a 
        JOIN tabCompany c ON a.company = c.name 
        SET a.account_currency = c.default_currency 
        WHERE a.account_currency != c.default_currency
    """)
