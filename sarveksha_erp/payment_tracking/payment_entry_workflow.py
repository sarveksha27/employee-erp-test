import frappe


def validate_payment_entry_workflow(doc, method=None):
    """
    Member 2 (Manik) - Payment Entry Workflow Validation.

    Enforces the maker-checker governance model:
    - Blocks Accounts Clerk from directly submitting a Payment Entry via raw API calls.
    - The document MUST be in 'Pending Approval' workflow state before it can be submitted
      (i.e., the Accounts Manager must click 'Approve & Submit', not bypass the workflow).
    - System Manager is always allowed to bypass for administrative purposes.
    """
    current_user = frappe.session.user
    user_roles = frappe.get_roles(current_user)

    # System Manager bypass — always allowed
    if "System Manager" in user_roles or "Administrator" in user_roles:
        return

    # Only Accounts Manager can submit
    if "Accounts Manager" not in user_roles:
        frappe.throw(
            "Only an Accounts Manager can submit a Payment Entry. "
            "As an Accounts Clerk, please use 'Send for Approval' to forward it for review.",
            frappe.PermissionError
        )

    # Accounts Manager can only submit if the document was in 'Pending Approval' workflow state
    workflow_state = doc.get("workflow_state")
    db_state = frappe.db.get_value("Payment Entry", doc.name, "workflow_state") if doc.name else None

    # When Frappe applies the 'Approve & Submit' transition, workflow_state is set to 'Completed' in memory
    # while the persisted database state is 'Pending Approval'. Both indicate a legitimate approval transition.
    is_valid_transition = (
        (db_state == "Pending Approval" and workflow_state in ("Pending Approval", "Completed"))
        or (workflow_state == "Pending Approval")
    )

    if not is_valid_transition:
        frappe.throw(
            f"Cannot submit Payment Entry. "
            f"Current workflow state is '{workflow_state}'. "
            f"The document must be in 'Pending Approval' state before it can be approved and submitted. "
            f"Only use the 'Approve & Submit' workflow action button.",
            frappe.ValidationError
        )
