import frappe

def execute():
    # Deep diagnostic of everything
    print("=" * 60)
    print("DEEP DIAGNOSTIC REPORT")
    print("=" * 60)

    # 1. Check Workspace doc
    ws = frappe.get_doc("Workspace", "Vendor Management")
    print(f"\n--- Workspace ---")
    print(f"Name: {ws.name}")
    print(f"Public: {ws.public}")
    print(f"Is Hidden: {ws.is_hidden}")
    print(f"Module: {ws.module}")
    print(f"Parent Page: '{ws.parent_page}'")
    print(f"Sequence ID: {ws.sequence_id}")
    print(f"Icon: {ws.icon}")
    print(f"Shortcuts count: {len(ws.shortcuts)}")
    for s in ws.shortcuts:
        print(f"  - Shortcut: {s.label} -> {s.link_to} (icon: {s.icon})")
    
    # 2. Check Workspace Sidebar
    ws_sb = frappe.get_doc("Workspace Sidebar", "Vendor Management")
    print(f"\n--- Workspace Sidebar ---")
    print(f"Name: {ws_sb.name}")
    print(f"Standard: {ws_sb.standard}")
    print(f"Header Icon: {ws_sb.header_icon}")
    print(f"Items count: {len(ws_sb.items)}")
    for item in ws_sb.items:
        print(f"  - Item: {item.label} -> {item.link_to}")
    
    # 3. Check Module def
    module_def = frappe.get_value("Module Def", "Vendor Management", ["name", "module_name", "app_name"], as_dict=True)
    print(f"\n--- Module Def ---")
    print(module_def)
    
    # 4. Check if the user has admin role
    user = frappe.get_doc("User", "Administrator")
    roles = [r.role for r in user.roles]
    print(f"\n--- Admin User Roles ---")
    print(f"Has System Manager: {'System Manager' in roles}")
    print(f"Has Accounts Manager: {'Accounts Manager' in roles}")
    
    # 5. Check roles on workspace
    ws_roles = [r.role for r in ws.roles]
    print(f"\n--- Workspace Roles ---")
    print(f"Workspace roles: {ws_roles}")
    print(f"Is public (no role restriction): {len(ws_roles) == 0}")
