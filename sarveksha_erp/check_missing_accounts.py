import frappe
import json

def run():
    with open('../apps/sarveksha_erp/sarveksha_erp/fixtures/company.json') as f:
        docs = json.load(f)
    for d in docs:
        company = frappe.get_doc(d)
        accounts = [
            ['Default Payable Account', 'default_payable_account'],
            ['Default Expense Account', 'default_expense_account'],
            ['Default Income Account', 'default_income_account'],
            ['Stock Received But Not Billed Account', 'stock_received_but_not_billed'],
            ['Stock Adjustment Account', 'stock_adjustment_account'],
            ['Write Off Account', 'write_off_account'],
            ['Default Payment Discount Account', 'default_discount_account'],
            ['Unrealized Profit / Loss Account', 'unrealized_profit_loss_account'],
            ['Exchange Gain / Loss Account', 'exchange_gain_loss_account'],
            ['Unrealized Exchange Gain / Loss Account', 'unrealized_exchange_gain_loss_account'],
            ['Round Off Account', 'round_off_account'],
            ['Default Deferred Revenue Account', 'default_deferred_revenue_account'],
            ['Default Deferred Expense Account', 'default_deferred_expense_account'],
            ['Accumulated Depreciation Account', 'accumulated_depreciation_account'],
            ['Depreciation Expense Account', 'depreciation_expense_account'],
            ['Gain/Loss Account on Asset Disposal', 'disposal_account'],
            ['Default Cash Account', 'default_cash_account']
        ]
        for account in accounts:
            if company.get(account[1]):
                val = frappe.db.get_value('Account', company.get(account[1]), ['company', 'is_group', 'disabled'])
                if val is None:
                    print(f'MISSING ACCOUNT: {company.get(account[1])} in {company.name}')
