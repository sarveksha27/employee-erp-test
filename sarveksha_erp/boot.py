import frappe


def extend_bootinfo(bootinfo):
    """
    1. Ensure only users with System Manager or Administrator role can see User Management in workspace sidebars.
    2. Ensure only authorized Finance users (Accounts Manager, Accounts Clerk, Accounts User, System Manager, Administrator)
       can see the Payment Tracking desktop icon and workspace sidebar on the main desk.
    """
    user = frappe.session.user
    if user == "Administrator":
        return

    user_roles = set(frappe.get_roles(user))
    is_system_manager = bool(user_roles.intersection({"System Manager", "Administrator"}))
    allowed_finance_roles = {"Accounts Manager", "Accounts Clerk", "Accounts User", "System Manager", "Administrator"}
    is_finance_user = bool(user_roles.intersection(allowed_finance_roles))

    sidebar_items_dict = (
        bootinfo.get("workspace_sidebar_item")
        if hasattr(bootinfo, "get")
        else getattr(bootinfo, "workspace_sidebar_item", None)
    )

    # 1. Non-System Manager user: remove User Management from all sidebar items in bootinfo
    if not is_system_manager and isinstance(sidebar_items_dict, dict):
        for sidebar_name, sidebar in sidebar_items_dict.items():
            if isinstance(sidebar, dict) and "items" in sidebar:
                sidebar["items"] = [
                    item for item in sidebar["items"]
                    if not (
                        item.get("link_to") == "User"
                        or item.get("label") in ["User Management", "User Creation"]
                    )
                ]

    # 2. Non-Finance user: remove Payment Tracking from desktop icons, sidebars, and workspaces
    if not is_finance_user:
        # Filter desktop icons
        desktop_icons = (
            bootinfo.get("desktop_icons")
            if hasattr(bootinfo, "get")
            else getattr(bootinfo, "desktop_icons", None)
        )
        if isinstance(desktop_icons, list):
            bootinfo["desktop_icons"] = [
                icon for icon in desktop_icons
                if not (
                    (isinstance(icon, dict) and (icon.get("name") == "Payment Tracking" or icon.get("label") == "Payment Tracking"))
                    or (isinstance(icon, str) and icon == "Payment Tracking")
                )
            ]

        # Filter workspace sidebars
        if isinstance(sidebar_items_dict, dict):
            sidebar_items_dict.pop("Payment Tracking", None)
        elif isinstance(sidebar_items_dict, list):
            bootinfo["workspace_sidebar_item"] = [
                s for s in sidebar_items_dict
                if not (
                    (isinstance(s, dict) and (s.get("name") == "Payment Tracking" or s.get("title") == "Payment Tracking" or s.get("label") == "Payment Tracking"))
                    or (isinstance(s, str) and s == "Payment Tracking")
                )
            ]


        # Filter allowed workspaces
        allowed_workspaces = (
            bootinfo.get("allowed_workspaces")
            if hasattr(bootinfo, "get")
            else getattr(bootinfo, "allowed_workspaces", None)
        )
        if isinstance(allowed_workspaces, list):
            bootinfo["allowed_workspaces"] = [
                ws for ws in allowed_workspaces
                if not (
                    (isinstance(ws, dict) and (ws.get("name") == "Payment Tracking" or ws.get("title") == "Payment Tracking"))
                    or (isinstance(ws, str) and ws == "Payment Tracking")
                )
            ]
