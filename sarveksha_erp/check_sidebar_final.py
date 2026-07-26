def check_sidebar():
    from frappe.boot import get_sidebar_items
    from frappe.desk.desktop import get_workspaces

    workspaces = get_workspaces()
    allowed_pages = [p['name'] for p in workspaces['pages']]
    sidebar = get_sidebar_items(allowed_pages)
    print("=== Sidebar Keys ===")
    for key in sorted(sidebar.keys()):
        print(f"  {key}")
    print("\nEquipment Management in sidebar:", 'equipment management' in sidebar)
    if 'equipment management' in sidebar:
        em = sidebar['equipment management']
        print("Items:", em['items'])
