# 🚀 Sarveksha ERP — Vendor Procurement & Purchase Order Enhancement
## Technical Documentation & Master Implementation Guide

---

## 📌 1. System Architecture & Executive Summary

The **Sarveksha ERP Purchase Order (PO)** module is a custom Frappe application (`sarveksha_erp`) powering equipment procurement, inter-company trading, multi-currency accounting, and payment tracking for **Sarveksha Group** across global operations (**India, Cameroon, Botswana, Sierra Leone, and Guinea**).

The module has been enhanced into a **production-grade enterprise procurement platform** featuring:
- **Master Data & Port Management** with dedicated Port catalog and standardized shipping channels.
- **Role-Based Access Control (RBAC) & 7-State Workflow Engine** regulating PO generation, verification, return, approval, and submission.
- **Dynamic Company GSTIN / PAN Auto-Fetch System**.
- **Legal Terms & Conditions Library** with live UI preview and rich-text custom terms support.
- **LUT Certificate Tax Override Engine** applying 0.1% GST for merchant export POs.
- **Multi-Equipment Line Item Architecture & Multi-Currency Processing** (**INR** for India, **USD** for international entities).

---

## ✨ 2. Detailed Pointwise Feature Specifications

---

### 📍 2.1. Port Master & Shipping Management

#### A. Port Master DocType (`Port`)
- **Doctype Definition**: Created standalone `Port` master DocType with permissions and fixture export.
- **Fields**:
  - `port_name` *(Data, Mandatory)*: Full name of sea/air port.
  - `country` *(Link → Country)*: Jurisdiction country.
  - `port_code` *(Data, Unique)*: UN/LOCODE or custom port identifier.
  - `is_active` *(Check, Default: 1)*: Active status flag.
- **Seeded Master Records**:
  1. `Mundra` (India — Port Code: `INMUN`)
  2. `JNPT` (India — Port Code: `INNSA`)
  3. `Conakry` (Guinea — Port Code: `GNCKY`)
  4. `Durban` (South Africa / Botswana transit — Port Code: `ZADUR`)
  5. `Freetown` (Sierra Leone — Port Code: `SLFNA`)
  6. `Douala` (Cameroon — Port Code: `CMDLA`)
- **PO Integration**: `port` field on `Vendor Purchase Order` converted to a **Link** field pointing to `Port`.

#### B. Shipment Type Selection Dropdown
- Converted `shipment_type` field on `Vendor Purchase Order` from generic text to a strict **Select** dropdown with 12 standardized logistics options:
  - `FCL` (Full Container Load)
  - `LCL` (Less than Container Load)
  - `Containerized`
  - `Flat Rack`
  - `Oversized`
  - `Hazardous Cargo`
  - `Part Shipment`
  - `Height Cargo`
  - `Break Bulk`
  - `RoRo` (Roll-on/Roll-off)
  - `Air Freight`
  - `Express Courier`

---

### 🏢 2.2. Company GSTIN & PAN Auto-Display System

#### A. Schema Enhancement
Added read-only audit fields to `Vendor Purchase Order`:
- `company_gstin` *(Data, Read-Only)*: Auto-fetched GST Identification Number of purchasing company.
- `company_pan` *(Data, Read-Only)*: Auto-fetched Permanent Account Number (PAN) of purchasing company.

#### B. Client-Side JS Auto-Fetch (`vendor_purchase_order.js`)
When `company` is selected on the PO form, client-side JS queries `Company` master data and populates GSTIN and PAN instantly:
```javascript
frappe.db.get_value('Company', frm.doc.company, ['tax_id', 'custom_pan'], (r) => {
    if (r) {
        if (r.tax_id) frm.set_value('company_gstin', r.tax_id);
        if (r.custom_pan) frm.set_value('company_pan', r.custom_pan);
    }
});
```

#### C. Print Format Representation
Rendered in the vendor and SRI company tax reference block of `vendor_purchase_order_format.html`:
- Displays `SRI GSTIN: {{ company.tax_id }}` and `PAN: {{ company.custom_pan }}`.

---

### 👥 2.3. User Accounts & Role-Based Access Control (RBAC)

#### A. 5 Pre-Configured Workflow Test User Accounts
1. **`po_generator@sarveksha.com`**: Purchase Order Generator / Sourcing Officer.
2. **`po_verifier@sarveksha.com`**: Technical & Commercial Verifier.
3. **`po_approver@sarveksha.com`**: Senior Director / Final Approver.
4. **`procurement_manager@sarveksha.com`**: Procurement Department Manager.
5. **`admin@sarveksha.com`**: System Administrator / System Manager.

#### B. 4 Custom System Roles
1. **`PO Generator`**: Permission to create, view, edit draft POs, and submit for verification.
2. **`PO Verifier`**: Permission to review, verify details, or return PO for revision.
3. **`PO Approver`**: Permission to perform final commercial sign-off and approve POs.
4. **`Procurement Manager`**: Full read, write, submit, cancel, and administrative permissions.

---

### 🔄 2.4. 7-State PO Workflow Engine

#### A. Workflow DocType Configuration (`Vendor Purchase Order Workflow`)
A native Frappe State Machine workflow governing the full lifecycle of Purchase Orders.

#### B. 7 Workflow States & Document Status Matrix

| Workflow State | DocStatus | Allowed Role(s) | Next Action |
| :--- | :--- | :--- | :--- |
| **`Draft`** | `0` (Draft) | `PO Generator`, `Procurement Manager` | Submit for Verification |
| **`Pending Verification`** | `0` (Draft) | `PO Verifier`, `Procurement Manager` | Verify PO OR Return to Generator |
| **`Verification Returned`**| `0` (Draft) | `PO Generator`, `Procurement Manager` | Re-submit for Verification |
| **`Pending Approval`** | `0` (Draft) | `PO Approver`, `Procurement Manager` | Approve PO OR Return to Verifier |
| **`Approval Returned`** | `0` (Draft) | `PO Verifier`, `Procurement Manager` | Re-verify OR Return to Generator |
| **`Approved`** | `1` (Submitted) | `PO Approver`, `Procurement Manager` | Lock & Issue PO |
| **`Printed`** | `1` (Submitted) | All Roles | View & Print Official PDF |

#### C. Transition Table
- `Draft` $\rightarrow$ `Pending Verification` *(Action: Submit for Verification)*
- `Pending Verification` $\rightarrow$ `Pending Approval` *(Action: Verify & Forward)*
- `Pending Verification` $\rightarrow$ `Verification Returned` *(Action: Return for Revision)*
- `Verification Returned` $\rightarrow$ `Pending Verification` *(Action: Resubmit)*
- `Pending Approval` $\rightarrow$ `Approved` *(Action: Approve Purchase Order)*
- `Pending Approval` $\rightarrow$ `Approval Returned` *(Action: Return to Verifier)*
- `Approved` $\rightarrow$ `Printed` *(Action: Mark Printed)*

---

### 📜 2.5. Legal Terms & Conditions Library & Live Preview

#### A. 4 Standard Legal T&C Templates
1. **`Standard Export PO Terms`**: Payment milestones, inspection SLA, Liquidated Damages (LD @ 0.5%/wk, max 10%), 12-month warranty, ISPM-15 packaging, force majeure, Indian court jurisdiction.
2. **`Export to Africa Terms`**: Sea-worthy export packaging, SGS/Bureau Veritas PSI certificate, African port clearance & demurrage rules.
3. **`Domestic India Terms`**: GST tax invoice compliance, E-Way Bill generation, site delivery, 1-year local warranty.
4. **`LUT Certificate Terms`**: Zero-rated export under Letter of Undertaking (LUT) per Section 16 of IGST Act 2017, 0.1% GST compliance.

#### B. UI & Print Format Integration
- **`standard_terms` Field**: Link to `Terms and Conditions` master.
- **`terms_preview` Field**: Read-only HTML preview box populated automatically upon selecting template.
- **`custom_terms` Field**: Rich text editor for adding transaction-specific clauses.
- **Print Format**: HTML template renders both standard template text and custom terms at the document footer.

---

### 🏛️ 2.6. LUT Certificate Tax Override Engine (0.1% GST)

#### A. Technical Workflow
1. User checks **`is_lut_applicable`** on the PO form.
2. In Python controller (`vendor_purchase_order.py`), if `is_lut_applicable == 1` and Company is `Sarveksha Realty...`:
   - Overrides `gst_percentage` across all child table items to **`0.1%`**.
   - Calculates IGST = $\text{Taxable Value} \times 0.001$.
   - Sets CGST = 0 and SGST = 0.

#### B. Financial Impact Comparison (`SRIPO-0002`)
- **Standard Tax (18% IGST)**:
  - Taxable Value: ₹8,70,000.00
  - IGST (18%): ₹1,56,600.00
  - Freight & Other Charges: ₹41,000.00
  - **Total**: **₹10,67,600.00**
- **LUT Concessional Tax (0.1% IGST)**:
  - Taxable Value: ₹8,70,000.00
  - IGST (0.1%): ₹870.00
  - Freight & Other Charges: ₹41,000.00
  - **Total**: **₹8,91,850.00** *(Direct Tax Liability Reduction: ₹1,55,730.00)*

---

### 🚜 2.7. Multi-Equipment Line Item & Multi-Currency Platform

#### A. Child DocType (`Vendor Purchase Order Item`)
Enables adding multiple equipment entries per PO. Fields include: `equipment`, `equipment_name`, `hsn_code`, `brand`, `manufacturer`, `unit`, `quantity`, `rate`, `discount_percent`, `gst_percentage`, `taxable_amount`, `tax_amount`, `total_amount`, `specification`.

#### B. Multi-Currency Sourcing
- **Indian Parent Entity** (`Sarveksha Realty and Inframine LLP`): **`INR`**
- **International Subsidiaries** (`Sarveksha Mining SARL`, `Sarveksha Botswana Proprietary Limited`, etc.): **`USD`**
- Dynamic PDF table headers formatting rates and totals in `USD` or `INR`.

---

## 📊 3. Master Purchase Orders Summary Table

| PO Number | Sector | Purchaser (Company) | Supplier (Vendor) | Currency | LUT (0.1% GST) | Workflow Approval State | Line Items Count | Grand Total |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`SRIPO-0001`** | ⛏️ Mining | Sarveksha Mining SARL *(Cameroon)* | Sarveksha Realty & Inframine LLP *(SRI)* | **USD** | No (0%) | `Draft` (DocStatus: 0) | 2 Items | **USD 12,459.00** |
| **`SRIPO-0002`** | ⛏️ Mining | Sarveksha Realty & Inframine LLP *(India)* | Action Construction Equipment | **INR** | **YES (0.1%)** | `Pending Verification` (DocStatus: 0) | 2 Items | **INR 8,91,850.00** |
| **`SRIPO-0003`** | 🏗️ Construction | Sarveksha Botswana Proprietary Limited | Sarveksha Realty & Inframine LLP *(SRI)* | **USD** | No (0%) | `Pending Approval` (DocStatus: 0) | 2 Items | **USD 73,490.00** |
| **`SRIPO-0004`** | 🏗️ Construction | Sarveksha Realty & Inframine LLP *(India)* | Tata Motors | **INR** | No (18%) | `Approved` (DocStatus: 1) | 2 Items | **INR 78,63,000.00** |

---

## 📂 4. Complete Directory Inventory & Fixtures Map

### Core Module Directory:
`frappe-bench/apps/sarveksha_erp/sarveksha_erp/vendor_management/`

1. **Port DocType**:
   - `doctype/port/port.json`
   - `doctype/port/port.py`
2. **Child DocType Schema & Controller**:
   - `doctype/vendor_purchase_order_item/vendor_purchase_order_item.json`
   - `doctype/vendor_purchase_order_item/vendor_purchase_order_item.py`
3. **Parent DocType Schema & Controller**:
   - `doctype/vendor_purchase_order/vendor_purchase_order.json`
   - `doctype/vendor_purchase_order/vendor_purchase_order.py`
   - `doctype/vendor_purchase_order/vendor_purchase_order.js`
4. **Print Format Template**:
   - `print_format/vendor_purchase_order_format/vendor_purchase_order_format.html`
5. **Fixture Exports (`sarveksha_erp/fixtures/`)**:
   - `port.json` (6 Seeded Ports)
   - `terms_and_conditions.json` (4 Standard T&C Templates)
   - `role.json` (4 Custom System Roles)
   - `workflow.json` (7-State PO Workflow)
   - `workflow_state.json` & `workflow_action_master.json`
   - `company.json`, `equipment.json`, `supplier.json`, `print_format.json`

---

## 🌿 5. Git & Deployment Instructions

### Repository Info:
- **Repository**: `git@github.com:manikkDev/employee-erp-test.git`
- **Active Branch**: **`umesh-test`**

### Commands to Deploy & Sync on Server:
```bash
# 1. Fetch latest changes from branch
cd /home/umeshraj/erp/frappe-bench/apps/sarveksha_erp
git checkout umesh-test
git pull upstream umesh-test

# 2. Run Bench Migrate to sync MariaDB schema & fixtures
cd /home/umeshraj/erp/frappe-bench
bench --site development migrate

# 3. Clear cache and restart bench
bench --site development clear-cache
bench restart
```

---
*Document Version: 3.0 (Master Unified Architecture Guide) | Sarveksha ERP Team*
