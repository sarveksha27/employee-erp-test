import frappe

def run():
    abbr_map = {
        "SMS": "SMSA",
        "OH": "OHSL",
        "SSL": "SSLL",
        "BM": "BMSL"
    }
    
    doctypes = ["Account", "Cost Center", "Warehouse"]
    
    for doctype in doctypes:
        for old_abbr, new_abbr in abbr_map.items():
            old_suffix = f" - {old_abbr}"
            new_suffix = f" - {new_abbr}"
            
            records = frappe.get_all(doctype, filters={"name": ("like", f"%{old_suffix}")}, pluck="name")
            for old_name in records:
                new_name = old_name[: -len(old_suffix)] + new_suffix
                print(f"Renaming {doctype}: {old_name} -> {new_name}")
                try:
                    frappe.rename_doc(doctype, old_name, new_name, force=True)
                except Exception as e:
                    print(f"Failed to rename {old_name}: {e}")
    
    frappe.db.commit()
    print("Done renaming!")
