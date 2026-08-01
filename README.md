# 📦 Sarveksha ERP - Vendor Purchase Order (VPO) Module

This repository contains the stabilized, secure, and audited **Vendor Purchase Order (VPO)** module for **Sarveksha ERP**. The system automates dynamic company address/letterhead fetching, enforces strict role-based document locking, overrides standard printing mechanisms, and drives an approval workflow using high-visibility action buttons.

---

## 📑 Table of Contents
1. [System Overview & Business Context](#1-system-overview--business-context)
2. [Workflow State Machine & MoM Design](#2-workflow-state-machine--mom-design)
3. [Key Files & Code Architecture](#3-key-files--code-architecture)
4. [Role-Based Access Control (RBAC) & Permissions](#4-role-based-access-control-rbac--permissions)
5. [Key Feature Implementations](#5-key-feature-implementations)
6. [Local Test Accounts](#6-local-test-accounts)
7. [Running & Verifying Tests](#7-running--verifying-tests)

---

## 1. System Overview & Business Context

In the Sarveksha procurement lifecycle, overseas subsidiary entities raise purchase requirements to **Sarveksha Realty and Inframine LLP (SRI India)**. SRI India then reviews these demands and issues a Purchase Order to vendor manufacturers.

The VPO module ensures:
* **Statutory Compliance**: Issuing entities must display correct physical addresses, registration details, PAN, and local tax numbers (e.g., GSTIN).
* **Tax Optimization**: SRI India holds an Export LUT (Letter of Undertaking) allowing a concessional 0.1% GST rate instead of standard GST rates for export-bound goods.
* **T&C Automation**: Multi-selection of standard terms automatically loaded based on company jurisdiction (e.g., LUT terms, country-specific terms).

---

## 2. Workflow State Machine & MoM Design

The workflow replaces standard manual state changes with top-level, role-specific action buttons.

### Revised 4-Stage State Machine
```text
                      +-------------------+
                      |     Generator     |
                      |    (State: Draft) |
                      +---------+---------+
                                |
                   Send Forward | (Generate PO)
                                v
                      +-------------------+
                      |     Verifier      |
                      | (State: Generated)|
                      +----+---------+----+
                           |         |
              Send Forward |         | Send Back
                  (Verify) |         | (Reason prompt)
                           v         v
                      +----+---------+----+
                      |     Approver      |
                      | (State: Verified) |
                      +----+---------+----+
                           |         |
              Send Forward |         | Send Back
                 (Approve) |         | (Reason prompt)
                           v         v
                      +----+---------+----+
                      |     Generator     |
                      | (State: Approved) |
                      +---------+---------+
                                |
                                | Print Allowed
                                v
                          [ PDF / Print ]
```

### Automatic Transitions & Rules (MoM Compliance)
1. **Yet to be Verified (Generated)**: When a PO Generator creates a document, the initial status is `Draft`. Once they click `Send Forward` (Generate PO), the document's state transitions to `Generated` (which represents **Yet to be Verified**). It is no longer in the `Draft` state, and the Generator is locked out of making further edits.
2. **No Manual Status Select**: The `workflow_state` is read-only and automatically updated based on the action button clicked.
3. **List View Visibility**: Only **Pending Approval** (Generated, Verified) and **Approved** POs are visible in the PO list view for verification/approval roles; all other draft stages are filtered out.
4. **Send Back Remarks**: Clicking `Send Back` prompts the user for remarks, writes them to `verifier_comments` or `approver_comments`, and redirects the document back.

### Custom Button & Print Logic Modifications
* **Top-Level Exclusive Buttons**: The custom workflow action buttons (`Send Forward` / `Send Back`) are exposed as prominent top-level buttons on the form, avoiding nested dropdowns.
  * **Primary Styling**: `Send Forward` is styled as a primary action button (`primary`).
  * **Danger Styling**: `Send Back` is styled as a danger action button (`danger`).
* **Unsaved & New Documents Support**: Workflow buttons are shown on all editable forms (`docstatus === 0`), even if the form has unsaved edits or is new (`__islocal` / `__unsaved`). When clicked, the script automatically triggers a form save (`frm.save()`) first before running the workflow RPC transition, ensuring no changes are lost.
* **Toolbar Print Guarding**: The default printer icon/button in the top-right toolbar (`frm.page.btn_print`) and the standard Print/PDF menu options are completely hidden (`frm.page.set_print_btn_display(false)`) for all unapproved documents. Printing is restricted to approved VPOs and authorized roles.

---

## 3. Key Files & Code Architecture

### 1. Python Controller
* **Path**: [`vendor_purchase_order.py`](file:///home/umeshraj/erp/frappe-bench/apps/sarveksha_erp/sarveksha_erp/vendor_management/doctype/vendor_purchase_order/vendor_purchase_order.py)
* **Key Functions**:
  * `validate_generator_edit_rights()`: Prevents `PO Generator` from editing fields once the PO has moved past the `Draft` state (compares state *prior* to current save using `get_doc_before_save()`).
  * `validate_audit_comments_edit_rights()`: Protects verification and approval remark logs from being tampered with outside their active stage.
  * `get_company_details(company)`: Whitelisted RPC endpoint. Safely retrieves company letterhead, port, currency, tax IDs, and physical address from linked `Address` & `Dynamic Link` records, and returns them as a single object.
  * `has_permission()`: Enforces server-side print guarding by blocking PDF printing on unapproved POs for non-admin roles.

### 2. JS Controller
* **Path**: [`vendor_purchase_order.js`](file:///home/umeshraj/erp/frappe-bench/apps/sarveksha_erp/sarveksha_erp/vendor_management/doctype/vendor_purchase_order/vendor_purchase_order.js)
* **Key Functions**:
  * `company()`: Triggers a `frappe.call` to the `get_company_details` Python RPC to cleanly populate address text, PAN, and GSTIN values dynamically.
  * `setup_verification_approval_panel()`: Dynamically enables/disables form inputs based on the user's role and the current state (e.g., locking all inputs for Generators when Generated, unlocking comments for Verifiers, locking everything except comments).
  * `apply_action()`: Save-guarded workflow applicator.
  * `can_print` checks: Toggles the print buttons (`frm.page.btn_print.hide()`, `frm.page.set_print_btn_display(false)`) to completely disable printing for unapproved documents.

### 3. List View Controller
* **Path**: [`vendor_purchase_order_list.js`](file:///home/umeshraj/erp/frappe-bench/apps/sarveksha_erp/sarveksha_erp/vendor_management/doctype/vendor_purchase_order/vendor_purchase_order_list.js)
* **Key Functions**:
  * Prevents displaying the `+ New` creation button in the list view for `PO Verifier` and `PO Approver` roles.
  * Applies standard filters so only Pending and Approved orders are exposed to verification roles.

---

## 4. Role-Based Access Control (RBAC) & Permissions

| Role | Create PO | Edit Draft | Verify Stage | Approve Stage | Print Approved PO | Edit Remarks |
|---|---|---|---|---|---|---|
| **PO Generator** | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| **PO Verifier** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ *(verifier_comments)* |
| **PO Approver** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ *(approver_comments)* |
| **Procurement Manager**| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **System Manager** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 5. Key Feature Implementations

### Concessional LUT Tax Calculations (0.1% GST)
* If `is_lut_applicable` is ticked, the tax calculations inside `calculate_gst_and_totals` apply a concessional rate of `0.1%` IGST (CGST and SGST are zeroed out).
* If unticked, it falls back to standard tax rules based on vendor location.

### Standard Terms Multi-Selection
* Users can select multiple pre-configured terms (e.g. standard export terms + local LUT terms).
* Standard terms are auto-appended to the document's standard terms table based on the company jurisdiction.

---

## 6. Local Test Accounts

All accounts use the password **`admin`** for ease of development and testing.

* **PO Generator**: `po_generator@sarveksha.com`
* **PO Verifier**: `po_verifier@sarveksha.com`
* **PO Approver**: `po_approver@sarveksha.com`
* **Procurement Manager**: `procurement_manager@sarveksha.com`
* **System Admin**: `admin@sarveksha.com`

---

## 7. Running & Verifying Tests

Verify backend compliance and transitions by running the custom test logic script:

```bash
bench --site development execute "exec(\"exec(open('/home/umeshraj/.gemini/antigravity/brain/90d16f09-1927-4b75-b645-5c576024cce9/scratch/test_po_logic.py').read())\ntest_po_logic()\")"
```

*Expected Output:*
```text
1. Standard Terms defaulted successfully:
   Selected standard terms in child table: ['Standard Export PO Terms']
2. Company Address: [Formatted Physical Address + Tax info]
3. Payment Status allow_on_submit: 1
4. Success saving Draft as Generator
5. Success transitioning Draft -> Generated as Generator
6. Correctly blocked Generator from editing Generated document
7. Success: Verifier was able to edit Generated document
SUCCESS: All backend logic checks passed successfully!
```
