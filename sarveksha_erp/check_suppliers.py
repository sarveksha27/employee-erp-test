import frappe, json
def check_suppliers():
    try:
        suppliers = frappe.get_all('Supplier', fields=['name', 'supplier_group'])
        print(f"Total Suppliers: {len(suppliers)}")
        print(suppliers[:5])
    except Exception as e:
        print("Error:", e)
