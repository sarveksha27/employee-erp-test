import frappe

def compare_workspace_sidebars():
    vm = frappe.db.get_value('Workspace Sidebar', 'Vendor Management', '*', as_dict=True)
    em = frappe.db.get_value('Workspace Sidebar', 'Equipment Management', '*', as_dict=True)
    
    print("=== Vendor Management Sidebar ===")
    if vm:
        for k, v in vm.items():
            if k not in ('creation', 'modified', 'owner', 'modified_by'):
                print(f"  {k}: {repr(v)}")
        items = frappe.get_all('Workspace Sidebar Item', filters={'parent': 'Vendor Management'}, fields=['*'], order_by='idx')
        for i in items:
            print(f"  - Item: {i.label} (type={i.type}, link_type={i.link_type}, link_to={i.link_to})")
    else:
        print("  Not found")
        
    print("\n=== Equipment Management Sidebar ===")
    if em:
        for k, v in em.items():
            if k not in ('creation', 'modified', 'owner', 'modified_by'):
                print(f"  {k}: {repr(v)}")
        items = frappe.get_all('Workspace Sidebar Item', filters={'parent': 'Equipment Management'}, fields=['*'], order_by='idx')
        for i in items:
            print(f"  - Item: {i.label} (type={i.type}, link_type={i.link_type}, link_to={i.link_to})")
    else:
        print("  Not found")
