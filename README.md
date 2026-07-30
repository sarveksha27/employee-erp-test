# 🚀 Sarveksha ERP — Vendor Procurement & Purchase Order Enhancement

Welcome to the **Sarveksha ERP Purchase Order (PO) Enhancement Project**. This repository contains the custom Frappe application `sarveksha_erp` powering the procurement, equipment sourcing, inter-company trading, and payment tracking for **Sarveksha Group** across global operations (India, Cameroon, Botswana, Sierra Leone, and Guinea).

---

## 📌 Executive Summary & Architecture Overview

The Purchase Order module was successfully upgraded from a legacy single-equipment structure to a **production-grade, multi-equipment, multi-currency, inter-company procurement platform**.

Key enhancements delivered:
1. **Multi-Equipment Child Table Architecture**: Sourcing multiple heavy equipment items in a single Purchase Order with row-level tax calculations.
2. **Multi-Currency Sourcing (USD & INR)**: Indian parent entity operates in **INR**, while international child companies operate in **USD**.
3. **Terms & Conditions Engine**: Integrated 4 standard legal T&C templates with live UI previews and custom terms editor.
4. **LUT Export Tax Logic (0.1% GST)**: Server-side tax engine automatically applying concessional 0.1% GST for merchant exports under Letter of Undertaking (LUT).
5. **Strict Inter-Company Procurement Routing**: Child companies order through central entity **Sarveksha Realty and Inframine LLP (SRI)**, which then places master POs to external vendors.

---

## ✨ Features & Functional Enhancements

### 1. 🚜 Multi-Equipment Line Item Architecture
- **Child DocType (`Vendor Purchase Order Item`)**:
  - Enables adding multiple equipment entries per PO.
  - Fields: `equipment`, `equipment_name`, `hsn_code`, `brand`, `manufacturer`, `unit`, `quantity`, `rate`, `discount_percent`, `gst_percentage`, `taxable_amount`, `tax_amount`, `total_amount`, `specification`.
- **Dynamic JS Grid Triggers**: Auto-fetches equipment details (HSN, brand, unit cost, GST %) upon selection and updates line totals live in the browser.
- **Server-Side Aggregation**: Py controller aggregates row-level taxable values, taxes, freight, insurance, packing, and grand totals.

---

### 2. 💱 Multi-Currency Engine (USD vs INR)
- **Automatic Currency Assignment**:
  - **Indian Parent Entity** (`Sarveksha Realty and Inframine LLP`): **`INR`**
  - **International Child Companies** (`Sarveksha Mining SARL` - Cameroon, `Sarveksha Botswana Proprietary Limited` - Botswana, etc.): **`USD`**
- **Dynamic Print Formatting**: Print headers dynamically update to display `Rate (USD)` and `Amount (USD)` for international orders vs `Rate (INR)` and `Amount (INR)` for Indian domestic/LUT orders.

---

### 3. 📜 Legal Terms & Conditions Library
Integrated 4 pre-configured legal T&C templates:
1. **`Standard Export PO Terms`**: Payment milestones, inspection, Liquidated Damages (LD @ 0.5%/wk, max 10%), 12-month warranty, ISPM-15 packaging compliance, force majeure, and Indian legal jurisdiction.
2. **`Export to Africa Terms`**: Sea-worthy export packaging, SGS/Bureau Veritas pre-shipment inspection, and African port clearance rules.
3. **`Domestic India Terms`**: GST tax invoice compliance, E-Way bill generation, site delivery, and local warranty.
4. **`LUT Certificate Terms`**: Zero-rated export under Letter of Undertaking (LUT) per Section 16 of IGST Act 2017 with 0.1% concessional GST.

- **Live UI Preview**: Selecting `standard_terms` populates a read-only preview box on the form.
- **Custom Terms**: `custom_terms` rich text editor allows adding special clauses per PO.

---

### 4. 🏛️ LUT Certificate Tax Override (0.1% GST)
- **Checkbox (`is_lut_applicable`)**: Triggers merchant export tax calculations.
- **Python Calculation Override**:
  - When `is_lut_applicable` is checked for an Indian company, the tax engine automatically overrides GST percentage across line items to **`0.1%`**.
  - Recalculates CGST, SGST, IGST, and Grand Total accurately.

---

### 5. 🏢 Inter-Company Procurement Routing Rules
Strictly enforces corporate procurement flow:
- **Child Entities** → Issue Purchase Orders to **Sarveksha Realty and Inframine LLP (SRI)**.
- **Central Entity (SRI)** → Issues primary procurement Purchase Orders to external OEMs (**Action Construction Equipment**, **Tata Motors**, etc.).

---

## 📊 Summary of Master Purchase Orders Created

| PO Number | Sector | Purchaser (Company) | Supplier (Vendor) | Currency | Workflow Approval State | Line Items | Grand Total |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`SRIPO-0001`** | ⛏️ Mining | Sarveksha Mining SARL *(Cameroon)* | Sarveksha Realty & Inframine LLP *(SRI)* | **USD** | `Draft` (DocStatus: 0) | 2 Items | **USD 12,459.00** |
| **`SRIPO-0002`** | ⛏️ Mining | Sarveksha Realty & Inframine LLP *(India)* | Action Construction Equipment | **INR** | `Pending Verification` (DocStatus: 0) | 2 Items *(LUT 0.1% GST)* | **INR 8,91,850.00** |
| **`SRIPO-0003`** | 🏗️ Construction | Sarveksha Botswana Proprietary Limited | Sarveksha Realty & Inframine LLP *(SRI)* | **USD** | `Pending Approval` (DocStatus: 0) | 2 Items | **USD 73,490.00** |
| **`SRIPO-0004`** | 🏗️ Construction | Sarveksha Realty & Inframine LLP *(India)* | Tata Motors | **INR** | `Approved` (DocStatus: 1) | 2 Items | **INR 78,63,000.00** |

---

## 🛠️ Technical Details & File Mapping

| File Path | Description |
| :--- | :--- |
| `sarveksha_erp/vendor_management/doctype/vendor_purchase_order_item/` | New Child DocType definition for multi-equipment line items. |
| `sarveksha_erp/vendor_management/doctype/vendor_purchase_order/vendor_purchase_order.json` | Updated parent PO schema with `items` table, `is_lut_applicable`, and terms fields. |
| `sarveksha_erp/vendor_management/doctype/vendor_purchase_order/vendor_purchase_order.py` | Python controller with multi-item calculation engine and LUT 0.1% tax override. |
| `sarveksha_erp/vendor_management/doctype/vendor_purchase_order/vendor_purchase_order.js` | Client-side form handlers, equipment auto-fetch, live T&C preview, and calculations. |
| `sarveksha_erp/vendor_management/print_format/vendor_purchase_order_format/` | HTML/Jinja print format rendering logo, multi-item table, dynamic currency headers, T&C, and signatures. |
| `sarveksha_erp/fixtures/` | Exported fixtures for `company.json`, `terms_and_conditions.json`, `equipment.json`, `supplier.json`, etc. |

---

## 🌿 Git & Deployment

- **Repository**: `git@github.com:manikkDev/employee-erp-test.git`
- **Current Active Branch**: `umesh-test`
- **To Deploy / Sync**:
  ```bash
  git checkout umesh-test
  git pull upstream umesh-test
  bench --site development migrate
  ```

---
*Built with ❤️ by the Sarveksha ERP Development Team.*
