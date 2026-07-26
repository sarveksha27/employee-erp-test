import frappe

def reimport_workspace():
    import json
    import frappe.modules.import_file as imf
    
    app_path = frappe.get_app_path('sarveksha_erp')
    json_path = app_path + '/equipment_management/workspace/equipment_management/equipment_management.json'
    
    with open(json_path) as f:
        docdict = json.load(f)
    
    # Force re-import by deleting first and reimporting
    if frappe.db.exists('Workspace', 'Equipment Management'):
        frappe.delete_doc('Workspace', 'Equipment Management', force=True, ignore_missing=True)
        frappe.db.commit()
    
    doc = frappe.get_doc(docdict)
    doc.flags.ignore_permissions = True
    doc.flags.in_install = True
    doc.insert()
    frappe.db.commit()
    
    # Clear all caches
    frappe.cache.delete_key("bootinfo")
    frappe.clear_cache()
    
    print("Workspace reimported successfully!")
    print("name:", doc.name, "| public:", doc.public, "| module:", doc.module)
