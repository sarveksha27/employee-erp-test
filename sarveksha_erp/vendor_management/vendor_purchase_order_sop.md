# Standard Operating Procedure (SOP): Vendor Purchase Order (VPO) Module

**Document ID:** SOP-ERP-VPO-001  
**Version:** 2.0  
**Effective Date:** September 2026  
**Target Audience:** PO Generators, PO Verifiers, PO Approvers, Procurement Managers  

---

## 1. Executive Summary & Scope

This Standard Operating Procedure (SOP) defines the operational guidelines, business policy rules, and end-to-end workflow procedures for the **Vendor Purchase Order (VPO)** module within the Sarveksha ERP system.

### Key Workflows Covered:
- **Internal Purchase Orders**: Procurements between group companies and the parent entity (*Sri Radhe Enterprises*).
- **External Purchase Orders**: Procurement orders placed with registered external suppliers.
- **Logistics & Expense Management**: Boundary enforcement for non-negative freight, insurance, packing, and incidental charges.
- **Quotation Governance**: Mandatory 3-quote policy and comparison sheet audit integrity.
- **Taxation & LuT Policy**: Letter of Undertaking (LuT) zero-rating for exports/SEZ vs fallback Equipment GST taxation.
- **Document Stitching**: Automated PDF bundle creation containing PO details, quotations, invoices, and supporting files.

---

## 2. Role Responsibilities & Access Matrix

| Role | Creation | Edit Draft | Attach Quotes | Verify | Approve | Print / Export |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **PO Generator** | Yes | Yes | Yes | No | No | Read-only |
| **PO Verifier** | No | Read-only | Read-only | Yes | No | Read-only |
| **PO Approver** | No | Read-only | Read-only | No | Yes | Yes (Post-Approval) |
| **Procurement Manager** | Yes | Yes | Yes | Yes | Yes | Yes |

---

## 3. Module 1: PO Generator User Guide

### Step 1: Initiating a Purchase Order
1. Navigate to **Vendor Management Workspace** on the ERP Desk.
2. Select either:
   - **New Internal PO**: For intra-company transfers originating from child entities targeting *Sri Radhe Enterprises*.
   - **New External PO**: For commercial purchases from external suppliers.

### Step 2: General Information & Line Items
- **Company**: Select the purchasing entity.
- **Vendor**: Select the supplier. *(For Internal POs, the vendor is restricted to Sri Radhe Enterprises)*.
- **Item & Quantity**: Input the equipment or service details.
  - Quantity must be strictly greater than zero (`quantity > 0`).
  - Unit rates must be non-negative (`rate >= 0`).

### Step 3: Logistics & Incidentals Entry
Fill in the logistics charge breakdown fields:
- **Freight Charges**: Cost of transportation.
- **Insurance**: Shipment insurance premium.
- **Packing Charges**: Packaging & handling fee.
- **Other Charges**: Incidental costs.

> [!IMPORTANT]
> **Boundary Validation Rule**: Zero values (`0.00`) are accepted when no charges apply. Negative entries (e.g., `-50.00`) will be rejected immediately by server-side validation.

### Step 4: Quotation Attachments & Comparison Governance (External POs)
For external POs, quote evidence must be attached before forwarding out of `Draft`:
1. Upload the **Quotation Comparison Sheet** (`PDF` or `Image`).
2. In the **Quotations Table**, add at least **3 distinct vendor quotes**:
   - Select 3 different suppliers.
   - Enter Quotation Reference, Date, and Amount for each.
   - Attach the vendor quotation PDF for each row.
   - Mark the winning quote using the `Is Selected` checkbox.

### Step 5: Submitting for Verification
Once all details and quote evidence are uploaded, click **Submit / Forward for Verification**.
- Workflow State transitions to: `Generated (Yet to be Verified)`.
- **Note**: Once forwarded, quotation fields become read-only and immutable for audit compliance.

---

## 4. Module 2: Verifier & Approver User Guide

### Step 1: Reviewing Pending Orders
1. Open **Vendor Purchase Order List**.
2. Filter by Status:
   - `Generated (Yet to be Verified)` $\rightarrow$ Assigned to **PO Verifiers**.
   - `Verified (Yet to be approved)` $\rightarrow$ Assigned to **PO Approvers**.

### Step 2: Verification Checklist (PO Verifier)
- [ ] **Quotations Audit**: Inspect the 3 attached vendor quotes and verify that the comparison sheet matches the selected vendor's rate.
- [ ] **Internal PO Margin Check**: For internal orders, verify that the mandatory 5% margin calculation is applied correctly.
- [ ] **LuT & GST Tax Verification**: Verify whether `Is LuT Applicable` is checked.
  - If **Checked**: Tax rate defaults to 0% (zero-rated export/SEZ).
  - If **Unchecked**: System restores GST percentage mapped from Equipment Master HSN schedule.
- [ ] Action: Click **Verify Purchase Order**.
  - System updates `verified_by` and transitions state to `Verified (Yet to be approved)`.

### Step 3: Final Approval Checklist (PO Approver)
- [ ] Confirm budget availability and commercial terms.
- [ ] Action: Click **Approve Purchase Order**.
  - System generates a unique, sequential reference number (e.g., `SRI/PO/2026/00001`).
  - Workflow State transitions to `Approved`.

### Step 4: Printing & PDF Attachment Bundle Generation
1. On the approved Purchase Order form, click **Print / PDF**.
2. The system renders the formal CSS-driven print layout formatted to executive standards:
   - **Header Banner**: Corporate letterhead header cropping.
   - **Structured Line Items**: Clear border tables for descriptions, quantities, rates, and taxes.
   - **Attached Documents List**: Consolidated table listing all quotation files, invoices, and sidebar attachments.
   - **Stitched PDF Output**: Secondary PDFs and images appended directly after the main PO printout.

---

## 5. Module 3: UAT Feedback Log & Department Sign-Off

### Phase 2 Boundary Test Verification Summary

| Test Scenario | Input / Trigger | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Zero Logistics Expense** | Freight = 0, Insurance = 0 | Saved cleanly, total calculated accurately | Handled cleanly | **PASSED** |
| **Negative Logistics Expense** | Freight = -100 | Rejected with `frappe.ValidationError` | Blocked cleanly | **PASSED** |
| **Multi-Currency Purchase** | USD/EUR with exchange rate | Converted cleanly to base currency | Calculated accurately | **PASSED** |
| **Uncheck LuT Flag** | Toggle `Is LuT Applicable` to 0 | Restores HSN GST taxation without crashing | Restored cleanly | **PASSED** |
| **End-to-End Workflow** | Draft $\rightarrow$ Approved $\rightarrow$ PDF | Complete lifecycle run executed successfully | 17/17 Tests Passing | **PASSED** |

### User Feedback & Usability Log
1. **Attachment Visibility**: Attachment list table added to print format so reviewers can see all referenced files directly on page 2.
2. **Page Spacing**: Standardized multi-page `@page` print CSS to prevent header/footer overlap across multi-page POs.
3. **Audit Immutability**: Confirmed quotation evidence remains read-only after leaving the Draft stage.

---

## 6. Operational Readiness Certificate & Sign-Off

**Module Name:** Sarveksha ERP — Vendor Purchase Order (VPO)  
**Testing Phase:** Phase 1 (Core & Print Format) & Phase 2 (Boundary & Negative Testing)  
**Sign-Off Status:** **APPROVED FOR PRODUCTION DEPLOYMENT**  

```
[X] Functional Validation Passed
[X] Boundary & Negative Scenario Tests Passed
[X] Print Format & PDF Bundle Rendering Passed
[X] Workflow Security & Immutability Rules Enforced
```

**Approved By:**  
Procurement Lead: *Umesh Raj (Sarveksha Procurement)*  
System Architect: *Antigravity AI Team (Google DeepMind)*  
Date: *September 2, 2026*  
