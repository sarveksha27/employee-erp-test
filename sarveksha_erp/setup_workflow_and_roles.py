import frappe
from frappe.model.workflow import apply_workflow

def setup():
    print("Starting Workflow & Roles setup...")

    # 1. Create Custom Roles
    roles = ["PO Generator", "PO Verifier", "PO Approver", "Procurement Manager"]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.insert(ignore_permissions=True)
            print(f"Created Role: {role_name}")
        else:
            print(f"Role already exists: {role_name}")

    # 2. Setup Permissions (Custom DocPerm)
    print("Setting up Custom DocPerm matrix...")
    
    # Enable custom permissions for Vendor Purchase Order if not already done
    if not frappe.db.exists("Custom DocPerm", {"parent": "Vendor Purchase Order"}):
        from frappe.permissions import setup_custom_perms
        setup_custom_perms("Vendor Purchase Order")
    
    # Delete existing Custom DocPerms so we start fresh
    frappe.db.delete("Custom DocPerm", {"parent": "Vendor Purchase Order"})

    # Setup permissions helper
    def add_custom_perm(role, read=0, write=0, create=0, delete=0, submit=0, cancel=0, amend=0, print_perm=0, export=0):
        docperm = frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": "Vendor Purchase Order",
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "permlevel": 0,
            "read": read,
            "write": write,
            "create": create,
            "delete": delete,
            "submit": submit,
            "cancel": cancel,
            "amend": amend,
            "print": print_perm,
            "export": export,
            "share": 1 if role == "Procurement Manager" or role == "System Manager" else 0
        })
        docperm.insert(ignore_permissions=True)
        print(f"Added permission for {role}")

    # PO Generator: Create, Read, Write, Print (at Final stage/Printed, handled in print format), Export
    add_custom_perm("PO Generator", read=1, write=1, create=1, print_perm=1, export=1)
    
    # PO Verifier: Read, Write
    add_custom_perm("PO Verifier", read=1, write=1, create=0, print_perm=0, export=0)
    
    # PO Approver: Read, Write
    add_custom_perm("PO Approver", read=1, write=1, create=0, print_perm=0, export=0)
    
    # Procurement Manager: Full access
    add_custom_perm("Procurement Manager", read=1, write=1, create=1, delete=1, submit=1, cancel=1, amend=1, print_perm=1, export=1)
    
    # System Manager: Full access (to avoid locking out admin)
    add_custom_perm("System Manager", read=1, write=1, create=1, delete=1, submit=1, cancel=1, amend=1, print_perm=1, export=1)

    # 3. Create Custom Workflow Action Master records
    actions = [
        "Submit for Verification", "Verify", "Reject / Return",
        "Resubmit for Verification", "Approve", "Resubmit for Approval", "Mark as Printed"
    ]
    for action in actions:
        if not frappe.db.exists("Workflow Action Master", action):
            act_doc = frappe.new_doc("Workflow Action Master")
            act_doc.workflow_action_name = action
            act_doc.insert(ignore_permissions=True)
            print(f"Created Workflow Action Master: {action}")

    # 3.5 Create Workflow State records in master list
    states = [
        "Draft", "Pending Verification", "Verification Returned",
        "Pending Approval", "Approval Returned", "Approved", "Printed"
    ]
    for state in states:
        if not frappe.db.exists("Workflow State", state):
            ws_doc = frappe.new_doc("Workflow State")
            ws_doc.workflow_state_name = state
            ws_doc.insert(ignore_permissions=True)
            print(f"Created Workflow State: {state}")

    # 4. Create/Recreate Workflow
    workflow_name = "Vendor Purchase Order Workflow"
    if frappe.db.exists("Workflow", workflow_name):
        frappe.delete_doc("Workflow", workflow_name, force=True)
        print("Deleted existing Workflow.")

    workflow = frappe.new_doc("Workflow")
    workflow.workflow_name = workflow_name
    workflow.document_type = "Vendor Purchase Order"
    workflow.workflow_state_field = "workflow_state"
    workflow.is_active = 1
    
    # States
    # Format: [state, doc_status, allow_edit]
    states_config = [
        ["Draft", "0", "PO Generator"],
        ["Pending Verification", "0", "PO Verifier"],
        ["Verification Returned", "0", "PO Generator"],
        ["Pending Approval", "0", "PO Approver"],
        ["Approval Returned", "0", "PO Generator"],
        ["Approved", "1", "Procurement Manager"],
        ["Printed", "1", "Procurement Manager"]
    ]
    
    for s_name, doc_status, allow_edit in states_config:
        workflow.append("states", {
            "state": s_name,
            "doc_status": doc_status,
            "allow_edit": allow_edit
        })

    # Transitions
    # Format: [state, action, next_state, allowed]
    transitions_config = [
        # Draft -> Pending Verification
        ["Draft", "Submit for Verification", "Pending Verification", "PO Generator"],
        ["Draft", "Submit for Verification", "Pending Verification", "Procurement Manager"],
        
        # Pending Verification -> Pending Approval / Verification Returned
        ["Pending Verification", "Verify", "Pending Approval", "PO Verifier"],
        ["Pending Verification", "Verify", "Pending Approval", "Procurement Manager"],
        ["Pending Verification", "Reject / Return", "Verification Returned", "PO Verifier"],
        ["Pending Verification", "Reject / Return", "Verification Returned", "Procurement Manager"],
        
        # Verification Returned -> Pending Verification
        ["Verification Returned", "Resubmit for Verification", "Pending Verification", "PO Generator"],
        ["Verification Returned", "Resubmit for Verification", "Pending Verification", "Procurement Manager"],
        
        # Pending Approval -> Approved / Approval Returned
        ["Pending Approval", "Approve", "Approved", "PO Approver"],
        ["Pending Approval", "Approve", "Approved", "Procurement Manager"],
        ["Pending Approval", "Reject / Return", "Approval Returned", "PO Approver"],
        ["Pending Approval", "Reject / Return", "Approval Returned", "Procurement Manager"],
        
        # Approval Returned -> Pending Approval
        ["Approval Returned", "Resubmit for Approval", "Pending Approval", "PO Generator"],
        ["Approval Returned", "Resubmit for Approval", "Pending Approval", "PO Verifier"],
        ["Approval Returned", "Resubmit for Approval", "Pending Approval", "Procurement Manager"],
        
        # Approved -> Printed
        ["Approved", "Mark as Printed", "Printed", "PO Generator"],
        ["Approved", "Mark as Printed", "Printed", "Procurement Manager"]
    ]
    
    for state, action, next_state, allowed in transitions_config:
        workflow.append("transitions", {
            "state": state,
            "action": action,
            "next_state": next_state,
            "allowed": allowed
        })

    workflow.insert(ignore_permissions=True)
    print("Workflow created and activated.")
    
    # 5. Clear permissions validation cache
    from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype
    validate_permissions_for_doctype("Vendor Purchase Order")
    
    frappe.db.commit()
    print("Setup completed successfully!")


def test_workflow():
    print("Starting Workflow transitions verification test...")
    companies = frappe.get_all("Company", limit=1)
    vendors = frappe.get_all("Supplier", limit=1)
    equipments = frappe.get_all("Equipment", limit=1)
    
    company = companies[0].name if companies else None
    vendor = vendors[0].name if vendors else None
    equipment = equipments[0].name if equipments else None
    
    if not company or not vendor or not equipment:
        print("Error: Missing Company, Supplier, or Equipment to create a test Vendor Purchase Order.")
        return

    # Create a test PO using direct document fields
    po = frappe.new_doc("Vendor Purchase Order")
    po.company = company
    po.vendor = vendor
    po.equipment = equipment
    po.quantity = 1
    po.rate = 15000
    po.is_lut_applicable = 1
    
    # Save as Draft
    po.insert(ignore_permissions=True)
    print(f"PO {po.name} created. Initial State: {po.workflow_state}")

    # Test transitions
    try:
        # 1. Draft -> Pending Verification
        po = apply_workflow(po, "Submit for Verification")
        print(f"Transition 1 Successful -> State: {po.workflow_state}, DocStatus: {po.docstatus}")

        # 2. Pending Verification -> Pending Approval
        po = apply_workflow(po, "Verify")
        print(f"Transition 2 Successful -> State: {po.workflow_state}, DocStatus: {po.docstatus}")

        # 3. Pending Approval -> Approved (Docstatus becomes 1)
        po = apply_workflow(po, "Approve")
        print(f"Transition 3 Successful -> State: {po.workflow_state}, DocStatus: {po.docstatus}")

        # 4. Approved -> Printed
        po = apply_workflow(po, "Mark as Printed")
        print(f"Transition 4 Successful -> State: {po.workflow_state}, DocStatus: {po.docstatus}")

    except Exception as e:
        print(f"Transition test failed with exception: {e}")
    finally:
        # Cleanup
        try:
            # Reload to get correct docstatus
            po.load_from_db()
            if po.docstatus == 1:
                po.cancel()
            frappe.delete_doc("Vendor Purchase Order", po.name, force=True)
            print("Test PO successfully deleted.")
        except Exception as delete_err:
            print(f"Cleanup failed: {delete_err}")
            # Force direct delete in DB if cancel/delete fails
            frappe.db.delete("Vendor Purchase Order", {"name": po.name})
            print("Force deleted PO record directly from database.")
        
        frappe.db.commit()
        print("Database committed.")
