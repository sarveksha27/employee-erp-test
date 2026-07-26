import frappe

def compare_workspaces():
    vm = frappe.db.get_value('Workspace', 'Vendor Management', 
        ['name', 'title', 'public', 'is_hidden', 'module', 'app', 'parent_page', 
         'type', 'sequence_id', 'icon', 'indicator_color', 'for_user', 'restrict_to_domain'],
        as_dict=True)
    em = frappe.db.get_value('Workspace', 'Equipment Management', 
        ['name', 'title', 'public', 'is_hidden', 'module', 'app', 'parent_page', 
         'type', 'sequence_id', 'icon', 'indicator_color', 'for_user', 'restrict_to_domain'],
        as_dict=True)
    
    print("=== Vendor Management ===")
    for k, v in vm.items():
        print(f"  {k}: {repr(v)}")
    
    print("\n=== Equipment Management ===")
    for k, v in em.items():
        print(f"  {k}: {repr(v)}")
    
    print("\n=== DIFFERENCES ===")
    for k in vm:
        if vm[k] != em[k]:
            print(f"  {k}: VM={repr(vm[k])} vs EM={repr(em[k])}")
