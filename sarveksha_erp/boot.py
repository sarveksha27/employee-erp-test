import frappe


def extend_bootinfo(bootinfo):
    """
    Ensure only users with System Manager or Administrator role can see User Management
    in workspace sidebars.
    """
    user = frappe.session.user
    if user == "Administrator":
        return

    user_roles = frappe.get_roles(user)
    if "System Manager" in user_roles or "Administrator" in user_roles:
        return

    # Non-System Manager user: remove User Management from all sidebar items in bootinfo
    sidebar_items_dict = (
        bootinfo.get("workspace_sidebar_item")
        if hasattr(bootinfo, "get")
        else getattr(bootinfo, "workspace_sidebar_item", None)
    )
    if isinstance(sidebar_items_dict, dict):
        for sidebar_name, sidebar in sidebar_items_dict.items():
            if isinstance(sidebar, dict) and "items" in sidebar:
                sidebar["items"] = [
                    item for item in sidebar["items"]
                    if not (
                        item.get("link_to") == "User"
                        or item.get("label") in ["User Management", "User Creation"]
                    )
                ]
