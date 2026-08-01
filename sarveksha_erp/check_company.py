import frappe
import json

def run():
    with open('../apps/sarveksha_erp/sarveksha_erp/fixtures/company.json') as f:
        docs = json.load(f)
    for d in docs:
        company = frappe.get_doc(d)
        for field in ['default_cash_account', 'default_bank_account', 'default_payable_account', 'default_expense_account', 'default_income_account']:
            account = company.get(field)
            if account:
                acc_currency = frappe.db.get_value('Account', account, 'account_currency')
                if acc_currency != company.default_currency and acc_currency:
                    print(f'Mismatched {field}: {account} (DB currency: {acc_currency}, Company currency: {company.default_currency}) in Company {company.name}')
