"""Acceptance tests for Kshitij's payment terms template validation engine."""

import unittest
from types import SimpleNamespace

import frappe

from sarveksha_erp.payment_tracking.payment_terms_validator import validate_payment_terms_template


def _template(*terms, name="Test Template"):
    return SimpleNamespace(template_name=name, terms=list(terms))


def _term(invoice_portion, credit_days=0):
    return SimpleNamespace(invoice_portion=invoice_portion, credit_days=credit_days)


class TestPaymentTermsEngine(unittest.TestCase):
    def test_valid_template_and_portion_tolerance_pass(self):
        doc = _template(_term(30), _term(70.0005))
        validate_payment_terms_template(doc)

    def test_portions_must_total_100_percent(self):
        doc = _template(_term(30), _term(69.998))
        with self.assertRaisesRegex(frappe.ValidationError, "must total 100%"):
            validate_payment_terms_template(doc)

    def test_each_portion_must_be_positive(self):
        for invalid_portion in (0, -1):
            with self.subTest(invoice_portion=invalid_portion):
                with self.assertRaisesRegex(frappe.ValidationError, "greater than 0%"):
                    validate_payment_terms_template(_template(_term(invalid_portion), name="Invalid Portion"))

    def test_credit_days_cannot_be_negative(self):
        with self.assertRaisesRegex(frappe.ValidationError, "Credit days"):
            validate_payment_terms_template(_template(_term(100, credit_days=-1)))

    def test_template_must_have_at_least_one_term(self):
        with self.assertRaisesRegex(frappe.ValidationError, "at least one payment term"):
            validate_payment_terms_template(_template())


if __name__ == "__main__":
    unittest.main()
