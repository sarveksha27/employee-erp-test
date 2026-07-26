def check():
    import frappe.desk.desktop as desktop
    result = desktop.get_workspaces()
    pages = result['pages']
    print("=== Workspaces visible to current user ===")
    for p in pages:
        print(f"  {p['name']} | public={p['public']} | is_hidden={p.get('is_hidden')} | module={p.get('module')}")
    names = [p['name'] for p in pages]
    print("Equipment Management in list:", 'Equipment Management' in names)
