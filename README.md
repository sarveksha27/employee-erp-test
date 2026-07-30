# 🚀 Sarveksha ERP — Vendor Procurement & Purchase Order Enhancement
## Executive Presentation & Technical Implementation Guide

---

## 📌 1. Project Overview & Key Objectives

This document serves as the master presentation guide for the **Sarveksha ERP Purchase Order (PO) Enhancement Project**. The application is a custom Frappe app (`sarveksha_erp`) powering equipment procurement, inter-company trading, and payment tracking across global operations in **India, Cameroon, Botswana, Sierra Leone, and Guinea**.

### 🎯 Primary Objectives Accomplished:
- **Multi-Equipment Procurement**: Transitioned from a single-item constraint to a multi-equipment line-item architecture.
- **Multi-Currency Sourcing**: Automated currency assignment (**INR** for Indian parent entity, **USD** for international child entities).
- **Terms & Conditions Library**: Integrated 4 standard legal T&C templates with live UI previews and custom terms editor.
- **LUT Export Tax Engine**: Implemented server-side 0.1% concessional GST calculation for merchant exports under Letter of Undertaking (LUT).
- **Inter-Company Sourcing Rules**: Enforced strict routing where child companies purchase through **Sarveksha Realty and Inframine LLP (SRI)**, which issues master POs to external OEMs.

---

## ✨ 2. Pointwise Feature Breakdown (Deep Dive)

---

### 🚜 Feature 2.1: Multi-Equipment Line Item Architecture

#### A. Schema Structure (`Vendor Purchase Order Item` Child DocType)
- **`equipment`** *(Link → Equipment, Mandatory)*: Equipment catalog code.
- **`equipment_name`** *(Data, Mandatory)*: Name of equipment auto-fetched from catalog.
- **`hsn_code`** *(Data)*: Harmonized System of Nomenclature (HSN/SAC) code for tax compliance.
- **`brand`** *(Data)*: Brand / Make of equipment.
- **`manufacturer`** *(Data)*: OEM Manufacturer details.
- **`unit`** *(Data)*: Unit of Measure (UOM - default `Nos`).
- **`quantity`** *(Float, Mandatory)*: Number of units ordered.
- **`rate`** *(Currency, Mandatory)*: Unit rate in PO currency.
- **`discount_percent`** *(Percent)*: Line item discount percentage.
- **`gst_percentage`** *(Percent)*: Applicable GST rate.
- **`taxable_amount`** *(Currency, Read-Only)*: Calculated net taxable value of row.
- **`tax_amount`** *(Currency, Read-Only)*: Calculated GST tax amount of row.
- **`total_amount`** *(Currency, Read-Only)*: Net total (Taxable Amount + Tax Amount).
- **`specification`** *(Small Text)*: Detailed technical specifications per line item.

#### B. Mathematical Calculation Engine
For each line item row $i$:
$$\text{Base Amount}_i = \text{Rate}_i \times \text{Quantity}_i$$
$$\text{Discount Amount}_i = \text{Base Amount}_i \times \left( \frac{\text{Discount \%}_i}{100} \right)$$
$$\text{Taxable Amount}_i = \text{Base Amount}_i - \text{Discount Amount}_i$$
$$\text{Tax Amount}_i = \text{Taxable Amount}_i \times \left( \frac{\text{GST \%}_i}{100} \right)$$
$$\text{Total Row Amount}_i = \text{Taxable Amount}_i + \text{Tax Amount}_i$$

#### C. Backwards Compatibility Layer
- Automatically syncs row #1 data to legacy fields (`equipment`, `equipment_name`, `quantity`, `rate`, `gst_percentage`) to ensure legacy reports and integrations continue functioning seamlessly.

---

### 💱 Feature 2.2: Multi-Currency Engine (USD vs INR)

#### A. Currency Assignment Rules
- **Rule 1 (Indian Entities)**:
  - If Company country is India (`Sarveksha Realty and Inframine LLP`) $\rightarrow$ Default Currency: **`INR`**.
- **Rule 2 (International Child Entities)**:
  - If Company country is outside India (`Sarveksha Mining SARL` - Cameroon, `Sarveksha Botswana Proprietary Limited` - Botswana, `Sarveksha SL Limited` - Sierra Leone, `Sarveksha BSTP SAS` - Guinea) $\rightarrow$ Default Currency: **`USD`**.

#### B. Form & PDF Print Presentation
- **Client-Side JS**: Selecting an international company automatically updates `currency` field to `USD`.
- **Print Format**: Table column headers dynamically format as `Rate (USD)` and `Amount (USD)` when `doc.currency == 'USD'`, and `Rate (INR)` / `Amount (INR)` when `doc.currency == 'INR'`.

---

### 📜 Feature 2.3: Legal Terms & Conditions Library & Preview

#### A. 4 Standard Legal Templates & Clauses

1. **`Standard Export PO Terms`**:
   - **Payment Milestones**: Payment made against commercial invoice, packing list, and bill of lading.
   - **Pre-Shipment Inspection**: Mandatory third-party quality inspection (SGS / Bureau Veritas).
   - **Liquidated Damages (LD)**: 0.5% of total PO value per week of delay, capped at 10%.
   - **Warranty**: 12 months from commissioning or 18 months from shipment.
   - **ISPM-15 Packaging**: Wooden packaging heat treated and stamped per ISPM-15 standards.
   - **Force Majeure**: Excuses non-performance during acts of God, war, or maritime blockades.
   - **Jurisdiction**: Subject to exclusive jurisdiction of courts in Mumbai, Maharashtra, India.

2. **`Export to Africa Terms`**:
   - **Export Packaging**: Heavy-duty sea-worthy containers with moisture absorbers.
   - **Pre-Shipment Inspection (PSI)**: Mandatory PSI certificate for African import customs clearance.
   - **Demurrage & Port Charges**: All destination port demurrage and duties in Africa on buyer's account.
   - **Documentation SLA**: Original shipping documents delivered within 7 days of vessel departure.

3. **`Domestic India Terms`**:
   - **GST Invoicing**: Valid Tax Invoice with HSN/SAC codes and supplier GSTIN mandatory.
   - **E-Way Bill**: Transport E-Way Bill generated prior to dispatch.
   - **Delivery & Transit Cover**: Transit insurance cover required from origin to site yard.
   - **Service SLA**: On-site service support provided within 48 hours of call logging.

4. **`LUT Certificate Terms`**:
   - **Zero-Rated Export**: Supplies under Letter of Undertaking (LUT) per Section 16 of IGST Act 2017.
   - **Concessional GST (0.1%)**: Merchant export concessional 0.1% GST applied.
   - **Proof of Export SLA**: Export invoice proof provided within 90 days of invoice date.

#### B. UI & Print Format Integration
- **`standard_terms` Field**: Link to `Terms and Conditions` master.
- **`terms_preview` Field**: Read-only HTML preview box populated automatically upon selecting template.
- **`custom_terms` Field**: Rich text editor for adding special transaction-specific clauses.
- **Print Format**: HTML template renders both standard template text and custom terms at the document footer.

---

### 🏛️ Feature 2.4: LUT Certificate Tax Override Engine (0.1% GST)

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

### 🏢 Feature 2.5: Inter-Company Procurement Routing Rules

#### A. Corporate Sourcing Hierarchy
- **Rule 1 (Child Companies)**:
  - `Sarveksha Mining SARL` (Cameroon) & `Sarveksha Botswana Proprietary Limited` (Botswana) MUST issue Purchase Orders to **Sarveksha Realty and Inframine LLP (SRI)**.
- **Rule 2 (Central Entity - SRI)**:
  - **Sarveksha Realty and Inframine LLP (SRI)** acts as central procurement hub and issues master export POs to external vendors (**Action Construction Equipment**, **Tata Motors**).

---

## 📊 3. Master Purchase Orders Summary Table

| PO Number | Sector | Purchaser (Company) | Supplier (Vendor) | Currency | LUT (0.1% GST) | Workflow Approval State | Line Items Count | Grand Total |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`SRIPO-0001`** | ⛏️ Mining | Sarveksha Mining SARL *(Cameroon)* | Sarveksha Realty & Inframine LLP *(SRI)* | **USD** | No (0%) | `Draft` (DocStatus: 0) | 2 Items | **USD 12,459.00** |
| **`SRIPO-0002`** | ⛏️ Mining | Sarveksha Realty & Inframine LLP *(India)* | Action Construction Equipment | **INR** | **YES (0.1%)** | `Pending Verification` (DocStatus: 0) | 2 Items | **INR 8,91,850.00** |
| **`SRIPO-0003`** | 🏗️ Construction | Sarveksha Botswana Proprietary Limited | Sarveksha Realty & Inframine LLP *(SRI)* | **USD** | No (0%) | `Pending Approval` (DocStatus: 0) | 2 Items | **USD 73,490.00** |
| **`SRIPO-0004`** | 🏗️ Construction | Sarveksha Realty & Inframine LLP *(India)* | Tata Motors | **INR** | No (18%) | `Approved` (DocStatus: 1) | 2 Items | **INR 78,63,000.00** |

---

## 📂 4. Complete File Inventory & Code Map

### Core Module Directory:
`frappe-bench/apps/sarveksha_erp/sarveksha_erp/vendor_management/`

1. **Child DocType Schema & Controller**:
   - `doctype/vendor_purchase_order_item/vendor_purchase_order_item.json`
   - `doctype/vendor_purchase_order_item/vendor_purchase_order_item.py`
2. **Parent DocType Schema & Controller**:
   - `doctype/vendor_purchase_order/vendor_purchase_order.json`
   - `doctype/vendor_purchase_order/vendor_purchase_order.py`
   - `doctype/vendor_purchase_order/vendor_purchase_order.js`
3. **Print Format Template**:
   - `print_format/vendor_purchase_order_format/vendor_purchase_order_format.html`
4. **Fixture Exports**:
   - `fixtures/company.json`
   - `fixtures/terms_and_conditions.json`
   - `fixtures/equipment.json`
   - `fixtures/supplier.json`
   - `fixtures/port.json`
   - `fixtures/print_format.json`

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
*Document Version: 2.0 (Final Presentation Grade) | Sarveksha ERP Team*
