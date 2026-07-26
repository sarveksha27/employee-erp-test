def check_entity_map():
    from frappe.model.sync import create_entity_file_map
    m = create_entity_file_map(['Workspace'])
    print("Equipment Management in map:", 'Equipment Management' in m['Workspace'])
    for k in sorted(m['Workspace'].keys()):
        print(" ", k)
