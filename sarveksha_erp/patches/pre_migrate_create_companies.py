import os
import json
import frappe

account_fields = [
    'default_bank_account', 'default_cash_account', 'default_receivable_account',
    'default_payable_account', 'default_expense_account', 'default_income_account',
    'default_discount_account', 'default_operating_cost_account',
    'default_deferred_revenue_account', 'default_deferred_expense_account',
    'default_advance_paid_account', 'default_advance_received_account',
    'accumulated_depreciation_account', 'depreciation_expense_account', 'disposal_account',
    'capital_work_in_progress_account', 'asset_received_but_not_billed',
    'expenses_added_to_stock_account', 'expenses_added_to_stock_contra_account',
    'stock_received_but_not_billed', 'stock_adjustment_account',
    'service_expense_account', 'purchase_expense_account',
    'purchase_expense_contra_account', 'write_off_account',
    'exchange_gain_loss_account', 'unrealized_exchange_gain_loss_account',
    'unrealized_profit_loss_account', 'round_off_account'
]

def ensure_account_exists(account_name, company_name):
    if not account_name or frappe.db.exists("Account", account_name):
        return

    parent = frappe.db.get_value("Account", {"company": company_name, "is_group": 1})
    currency = frappe.db.get_value("Company", company_name, "default_currency") or "USD"
    raw_title = account_name.rsplit(" - ", 1)[0] if " - " in account_name else account_name

    try:
        doc = frappe.get_doc({
            "doctype": "Account",
            "account_name": raw_title,
            "company": company_name,
            "parent_account": parent,
            "account_currency": currency,
            "is_group": 0
        })
        doc.insert(ignore_permissions=True)
    except Exception:
        try:
            frappe.db.sql("""
                INSERT IGNORE INTO `tabAccount`
                (`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`,
                 `account_name`, `company`, `is_group`, `account_currency`)
                VALUES (%s, NOW(), NOW(), 'Administrator', 'Administrator', 0, 0,
                        %s, %s, 0, %s)
            """, (account_name, raw_title, company_name, currency))
        except Exception:
            pass

def execute():
    # 1. Cleanup orphaned references to deleted companies in child tables
    try:
        frappe.db.sql("SET SQL_SAFE_UPDATES = 0;")
        for table in [
            "tabMode of Payment Account",
            "tabSales Taxes and Charges Template",
            "tabPurchase Taxes and Charges Template",
            "tabItem Tax Template"
        ]:
            frappe.db.sql(f"""
                DELETE FROM `{table}` 
                WHERE company IS NOT NULL 
                  AND company != '' 
                  AND company NOT IN (SELECT name FROM `tabCompany`)
            """)
        frappe.db.commit()
    except Exception:
        pass

    # 2. Path to company.json fixture
    fixture_path = frappe.get_app_path("sarveksha_erp", "fixtures", "company.json")
    if not os.path.exists(fixture_path):
        return

    with open(fixture_path, "r") as f:
        try:
            companies = json.load(f)
        except Exception:
            return

    # 3. Initialize missing companies
    for company in companies:
        name = company.get("name") or company.get("company_name")
        if not name:
            continue

        if not frappe.db.exists("Company", name):
            try:
                doc = frappe.get_doc({
                    "doctype": "Company",
                    "company_name": name,
                    "abbr": company.get("abbr"),
                    "default_currency": company.get("default_currency") or "USD",
                    "country": company.get("country") or "India",
                    "create_chart_of_accounts_based_on": "Standard Template"
                })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception:
                pass

    # 4. Ensure all default account links in company.json exist in tabAccount
    for company in companies:
        name = company.get("name") or company.get("company_name")
        if not name:
            continue
            
        for field in account_fields:
            acc = company.get(field)
            if acc:
                ensure_account_exists(acc, name)
                
    frappe.db.commit()
