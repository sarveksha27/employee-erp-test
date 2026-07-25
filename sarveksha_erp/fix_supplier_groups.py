import frappe

def execute():
    # Fix the Supplier Group hierarchy issue that's blocking migration
    # "Agriculture & Food cannot be a leaf node as it has children"
    # This means it has children but is_group = 0
    
    groups = frappe.get_all("Supplier Group", fields=["name", "is_group", "parent_supplier_group"])
    print("All Supplier Groups:")
    for g in groups:
        print(f"  {g['name']} | is_group={g['is_group']} | parent={g['parent_supplier_group']}")
    
    print()
    print("Fixing groups that have children but is_group=0...")
    
    # Find all groups that have children
    all_parents = frappe.db.sql("""
        SELECT DISTINCT parent_supplier_group 
        FROM `tabSupplier Group` 
        WHERE parent_supplier_group IS NOT NULL 
        AND parent_supplier_group != ''
    """, as_dict=True)
    
    parent_names = [p["parent_supplier_group"] for p in all_parents]
    print(f"Groups that are parents: {parent_names}")
    
    for parent_name in parent_names:
        if frappe.db.exists("Supplier Group", parent_name):
            is_group = frappe.db.get_value("Supplier Group", parent_name, "is_group")
            if not is_group:
                frappe.db.set_value("Supplier Group", parent_name, "is_group", 1)
                print(f"  ✓ Fixed: {parent_name} → is_group=1")
            else:
                print(f"  - OK: {parent_name} already is_group=1")
    
    frappe.db.commit()
    print()
    print("✅ Supplier Group hierarchy fixed")
