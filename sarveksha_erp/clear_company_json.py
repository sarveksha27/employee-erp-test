import json

def run():
    path = '/workspace/development/frappe-bench/apps/sarveksha_erp/sarveksha_erp/fixtures/company.json'
    with open(path) as f:
        docs = json.load(f)

    fields_to_clear = [
        'default_payable_account',
        'default_expense_account',
        'default_income_account',
        'stock_received_but_not_billed',
        'stock_adjustment_account',
        'write_off_account',
        'default_discount_account',
        'unrealized_profit_loss_account',
        'exchange_gain_loss_account',
        'unrealized_exchange_gain_loss_account',
        'round_off_account',
        'default_deferred_revenue_account',
        'default_deferred_expense_account',
        'accumulated_depreciation_account',
        'depreciation_expense_account',
        'disposal_account',
        'default_cash_account',
        'default_bank_account',
        'default_inventory_account',
        'default_receivable_account',
        'default_advance_paid_account',
        'default_advance_received_account',
    ]

    for doc in docs:
        for field in fields_to_clear:
            if field in doc:
                doc[field] = None

    with open(path, 'w') as f:
        json.dump(docs, f, indent=1)

if __name__ == '__main__':
    run()
