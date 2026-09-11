# Sarveksha ERP — Comprehensive Database Schema Reference
This document provides the complete, unabridged relational database schema for all DocTypes, child tables, and master registries utilized within the **Sarveksha ERP** vendor management and procurement ecosystem.
## Entity-Relationship Overview
```mermaid
graph TD
    Company["Company (tabCompany)"] -->|Buyer / Consignee| PI["Proforma Invoice (tabProforma Invoice)"]
    Company -->|Issuer| VPO["Vendor Purchase Order (tabVendor Purchase Order)"]
    Supplier["Supplier (tabSupplier)"] -->|Vendor / Seller| VPO
    VPO -->|Child: items| VPOI["Vendor Purchase Order Item (tabVendor Purchase Order Item)"]
    VPO -->|Child: quotations| VPOQ["Vendor Purchase Order Quotation (tabVendor Purchase Order Quotation)"]
    VPO -->|Child: standard_terms| VPOST["VPO Standard Term (tabVPO Standard Term)"]
    Equipment["Equipment (tabEquipment)"] -.->|Referenced by| VPOI
    VPO -->|Referenced by (Internal PO)| PI
    PI -->|Child: items| PII["Proforma Invoice Item (tabProforma Invoice Item)"]
    Port["Port (tabPort)"] -.->|Logistics| VPO
    Port -.->|Logistics| PI
    LetterHead["Letter Head (tabLetter Head)"] -.->|Stationery| VPO
    LetterHead -.->|Stationery| PI
    Terms["Terms and Conditions"] -.->|Linked| VPOST
    VPO -->|Payments| VP["Vendor Payment (tabVendor Payment)"]
```

---
## Vendor Purchase Order
- **Database Table**: `tabVendor Purchase Order`
- **DocType Classification**: Master / Transaction DocType
- **Module**: Vendor Management
- **Description**: Core document representing both Internal (Child -> SRI) and Vendor (Company -> External) Purchase Orders with workflow progression.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `workflow_state` | `Link` | No | No | `Workflow State` | Workflow State |
| `naming_series` | `Select` | **Yes** | No | `SRI.PO.-.####, SRI.RPO.-.####` | Series |
| `po_type` | `Select` | **Yes** | Yes | `Vendor PO, Internal PO` | PO Type |
| `ref_number` | `Data` | No | Yes | `—` | Reference Number |
| `status` | `Select` | **Yes** | No | `Draft, Pending Verification, Verification Retur...` | Status |
| `revision` | `Int` | No | No | `—` | Revision No. |
| `po_date` | `Date` | **Yes** | No | `—` | PO Date |
| `company` | `Link` | **Yes** | No | `Company` | Company |
| `letter_head` | `Link` | No | No | `Letter Head` | Letter Head |
| `company_gstin` | `Data` | No | Yes | `—` | Company GSTIN |
| `company_pan` | `Data` | No | Yes | `—` | Company PAN |
| `company_address` | `Small Text` | No | Yes | `—` | Company Address & Details |
| `default_port` | `Data` | No | Yes | `—` | Default Port |
| `vendor` | `Link` | **Yes** | No | `Supplier` | Vendor |
| `vendor_address` | `Small Text` | No | Yes | `—` | Vendor Address |
| `vendor_gstin` | `Data` | No | Yes | `—` | Vendor GSTIN |
| `vendor_pan` | `Data` | No | Yes | `—` | Vendor PAN |
| `vendor_bank_name` | `Data` | No | Yes | `—` | Vendor Bank |
| `vendor_account_number` | `Data` | No | Yes | `—` | Vendor Account No. |
| `vendor_ifsc` | `Data` | No | Yes | `—` | IFSC Code |
| `equipment` | `Link` | No | No | `Equipment` | Equipment |
| `equipment_name` | `Data` | No | No | `—` | Equipment Name |
| `hsn_code` | `Data` | No | No | `—` | HSN Code |
| `brand` | `Data` | No | No | `—` | Brand |
| `manufacturer` | `Data` | No | No | `—` | Manufacturer |
| `quantity` | `Float` | No | No | `—` | Quantity |
| `unit` | `Link` | No | No | `UOM` | Unit of Measure |
| `country_of_origin` | `Link` | No | No | `Country` | Country of Origin |
| `specification` | `Text Editor` | No | No | `—` | Specification / Description |
| `add_equipment_btn` | `Button` | No | No | `—` | + Add Equipment to Table |
| `items` | `Table` | No | No | `Vendor Purchase Order Item` | Equipment Line Items |
| `quotation_comparison_sheet` | `Attach` | No | No | `—` | Quotation Comparison Sheet |
| `quotations` | `Table` | No | No | `Vendor Purchase Order Quotation` | Vendor Quotations |
| `currency` | `Link` | **Yes** | No | `Currency` | Currency |
| `exchange_rate` | `Float` | No | No | `—` | Exchange Rate |
| `rate` | `Currency` | No | No | `currency` | Unit Rate |
| `discount_percent` | `Percent` | No | No | `—` | Discount % |
| `taxable_value` | `Currency` | No | Yes | `currency` | Taxable Value (after discount) |
| `is_lut_applicable` | `Check` | No | No | `—` | Is LUT Applicable (0.1% GST Export)? |
| `gst_percentage` | `Percent` | No | Yes | `—` | GST % |
| `gst_type` | `Select` | No | Yes | `, IGST, CGST + SGST` | GST Type |
| `cgst_amount` | `Currency` | No | Yes | `currency` | CGST Amount |
| `sgst_amount` | `Currency` | No | Yes | `currency` | SGST Amount |
| `igst_amount` | `Currency` | No | Yes | `currency` | IGST Amount |
| `tax_amount` | `Currency` | No | Yes | `currency` | Total Tax Amount |
| `freight` | `Currency` | No | No | `currency` | Freight Charges |
| `insurance` | `Currency` | No | No | `currency` | Insurance |
| `packing_charges` | `Currency` | No | No | `currency` | Packing Charges |
| `other_charges` | `Currency` | No | No | `currency` | Other Charges |
| `logistics_cost` | `Currency` | No | Yes | `currency` | Total Logistics Cost |
| `internal_margin_percentage` | `Percent` | No | No | `—` | Internal Margin % |
| `internal_margin_amount` | `Currency` | No | Yes | `currency` | Internal Margin Amount |
| `grand_total` | `Currency` | No | Yes | `currency` | Grand Total |
| `quotation_ref` | `Data` | No | No | `—` | Quotation Reference |
| `quotation_date` | `Date` | No | No | `—` | Quotation Date |
| `pi_number` | `Data` | No | No | `—` | Proforma Invoice No. |
| `pi_date` | `Date` | No | No | `—` | PI Date |
| `expected_delivery` | `Date` | No | No | `—` | Expected Delivery Date |
| `expected_delivery_time` | `Time` | No | No | `—` | Expected Delivery Time |
| `delivery_location` | `Data` | No | No | `—` | Delivery Location |
| `warehouse` | `Link` | No | No | `Warehouse` | Destination Warehouse |
| `port` | `Link` | No | No | `Port` | Port |
| `cha` | `Link` | No | No | `Supplier` | CHA |
| `shipment_type` | `Select` | No | No | `FCL, LCL, Containerized, Flat Rack, Oversized, ...` | Shipment Type |
| `shipment_subtype` | `Select` | No | No | `—` | Shipment Subtype |
| `container_number` | `Data` | No | No | `—` | Container Number |
| `invoice_doc` | `Attach` | No | No | `—` | Invoice |
| `shipping_bill` | `Attach` | No | No | `—` | Shipping Bill |
| `bill_of_lading` | `Attach` | No | No | `—` | Bill of Lading (BL) |
| `packing_list` | `Attach` | No | No | `—` | Packing List |
| `commercial_invoice` | `Attach` | No | No | `—` | Commercial Invoice |
| `certificate_of_origin` | `Attach` | No | No | `—` | Certificate of Origin (COO) |
| `inspection_report` | `Attach` | No | No | `—` | Inspection Report |
| `insurance_doc` | `Attach` | No | No | `—` | Insurance Document |
| `cfa_doc` | `Attach` | No | No | `—` | CFA / Clearing Agent Doc |
| `payment_terms` | `Small Text` | No | No | `—` | Payment Terms |
| `advance_percentage` | `Percent` | No | No | `—` | Advance % |
| `advance_amount` | `Currency` | No | Yes | `currency` | Advance Amount |
| `payment_status` | `Select` | No | No | `Pending, Advance Paid, Partially Paid, Fully Paid` | Payment Status |
| `payment_pending` | `Check` | No | No | `—` | Payment Pending |
| `payment_partially_paid` | `Check` | No | No | `—` | Payment Partially Paid |
| `payment_fully_paid` | `Check` | No | No | `—` | Payment Fully Paid |
| `balance_due` | `Currency` | No | Yes | `currency` | Balance Due |
| `company_bank` | `Data` | No | No | `—` | Company Bank (SRI) |
| `prepared_by` | `Link` | No | Yes | `User` | Prepared By |
| `verified_by` | `Link` | No | Yes | `User` | Verified By |
| `approved_by` | `Link` | No | Yes | `User` | Approved By |
| `signatory` | `Data` | No | Yes | `—` | Authorized Signatory |
| `verifier_comments` | `Small Text` | No | Yes | `—` | Verifier Comments / Notes |
| `verifier_status` | `Select` | No | Yes | `, Pending, Verified, Returned to Generator` | Verifier Status |
| `verified_on` | `Datetime` | No | Yes | `—` | Verified On |
| `approver_comments` | `Small Text` | No | Yes | `—` | Approver Comments / Notes |
| `approver_status` | `Select` | No | Yes | `, Pending, Approved, Returned to Verifier` | Approver Status |
| `approved_on` | `Datetime` | No | Yes | `—` | Approved On |
| `standard_terms` | `Table MultiSelect` | No | No | `VPO Standard Term` | Standard Terms |
| `terms_preview` | `HTML` | No | No | `—` | Standard Terms Preview |
| `custom_terms` | `Text Editor` | No | No | `—` | Custom Terms |
| `remarks` | `Small Text` | No | No | `—` | Remarks |
| `attachments` | `Attach` | No | No | `—` | Additional Attachments |
| `amended_from` | `Link` | No | Yes | `Vendor Purchase Order` | Amended From |
| `workflow_history_html` | `HTML` | No | No | `—` | Approval Audit Trail |

---

## Vendor Purchase Order Item
- **Database Table**: `tabVendor Purchase Order Item`
- **DocType Classification**: Child Table (Sub-table)
- **Module**: Vendor Management
- **Description**: Child table storing individual item rows, equipment link, specifications, quantities, and rates for a Purchase Order.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `parent` | `VARCHAR(140)` | **Yes** | Yes | Parent DocType Key | Parent Document Reference |
| `parentfield` | `VARCHAR(140)` | **Yes** | Yes | String | Child Table Fieldname on Parent |
| `parenttype` | `VARCHAR(140)` | **Yes** | Yes | String | Parent DocType Name |
| `idx` | `INT(8)` | **Yes** | No | Integer | Row Ordering Index |
| `equipment` | `Link` | **Yes** | No | `Equipment` | Equipment Code |
| `equipment_name` | `Data` | **Yes** | No | `—` | Equipment Name |
| `hsn_code` | `Data` | No | No | `—` | HSN Code |
| `brand` | `Data` | No | No | `—` | Brand |
| `manufacturer` | `Data` | No | No | `—` | Manufacturer |
| `unit` | `Data` | No | No | `—` | Unit |
| `quantity` | `Float` | **Yes** | No | `—` | Qty |
| `rate` | `Currency` | **Yes** | No | `—` | Unit Rate |
| `discount_percent` | `Percent` | No | No | `—` | Discount % |
| `gst_percentage` | `Percent` | No | No | `—` | GST % |
| `taxable_amount` | `Currency` | No | Yes | `—` | Taxable Amount |
| `tax_amount` | `Currency` | No | Yes | `—` | Tax Amount |
| `total_amount` | `Currency` | No | Yes | `—` | Total Amount |
| `specification` | `Small Text` | No | No | `—` | Technical Specification / Remarks |

---

## Vendor Purchase Order Quotation
- **Database Table**: `tabVendor Purchase Order Quotation`
- **DocType Classification**: Child Table (Sub-table)
- **Module**: Vendor Management
- **Description**: Child table managing multi-vendor price discovery, attached PDF quotations, delivery timelines, and selection flags.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `parent` | `VARCHAR(140)` | **Yes** | Yes | Parent DocType Key | Parent Document Reference |
| `parentfield` | `VARCHAR(140)` | **Yes** | Yes | String | Child Table Fieldname on Parent |
| `parenttype` | `VARCHAR(140)` | **Yes** | Yes | String | Parent DocType Name |
| `idx` | `INT(8)` | **Yes** | No | Integer | Row Ordering Index |
| `supplier` | `Link` | **Yes** | No | `Supplier` | Supplier |
| `quotation_reference` | `Data` | **Yes** | No | `—` | Quotation Reference Number |
| `quotation_date` | `Date` | **Yes** | No | `—` | Quotation Date |
| `quotation_amount` | `Currency` | **Yes** | No | `—` | Quotation Amount |
| `quotation_pdf` | `Attach` | **Yes** | No | `—` | Upload Quotation File |

---

## VPO Standard Term
- **Database Table**: `tabVPO Standard Term`
- **DocType Classification**: Child Table (Sub-table)
- **Module**: Vendor Management
- **Description**: Child table linking standard procurement, export, and compliance legal terms to a Purchase Order.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `parent` | `VARCHAR(140)` | **Yes** | Yes | Parent DocType Key | Parent Document Reference |
| `parentfield` | `VARCHAR(140)` | **Yes** | Yes | String | Child Table Fieldname on Parent |
| `parenttype` | `VARCHAR(140)` | **Yes** | Yes | String | Parent DocType Name |
| `idx` | `INT(8)` | **Yes** | No | Integer | Row Ordering Index |
| `standard_term` | `Link` | **Yes** | No | `Terms and Conditions` | Standard Term |

---

## Proforma Invoice
- **Database Table**: `tabProforma Invoice`
- **DocType Classification**: Master / Transaction DocType
- **Module**: Vendor Management
- **Description**: Seller-side export invoicing document generated exclusively from Approved Internal Purchase Orders with margin markups and logistics.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `naming_series` | `Select` | **Yes** | No | `SRI/PI/.YYYY.-.####, SRI/BOT/26-27/.###` | Series |
| `pi_number` | `Data` | No | Yes | `—` | Proforma Invoice No. |
| `pi_date` | `Date` | **Yes** | No | `—` | Date |
| `status` | `Select` | No | No | `Draft, Issued, Cancelled` | Status |
| `internal_po` | `Link` | **Yes** | No | `Vendor Purchase Order` | Internal Purchase Order |
| `po_reference_no` | `Data` | No | Yes | `—` | PO Reference Number |
| `po_date` | `Date` | No | Yes | `—` | PO Date |
| `seller` | `Data` | No | Yes | `—` | Seller / Shipper |
| `seller_address` | `Small Text` | No | Yes | `—` | Seller Address |
| `seller_gstin` | `Data` | No | Yes | `—` | Seller GSTIN |
| `seller_pan` | `Data` | No | Yes | `—` | Seller PAN |
| `seller_iec` | `Data` | No | Yes | `—` | Seller IEC Code |
| `buyer` | `Link` | No | Yes | `Company` | Buyer / Consignee |
| `buyer_address` | `Small Text` | No | Yes | `—` | Consignee Address |
| `notify_party` | `Small Text` | No | No | `—` | Notify Party |
| `port_of_loading` | `Data` | No | No | `—` | Port of Loading |
| `port_of_discharge` | `Data` | No | No | `—` | Port of Discharge |
| `final_destination` | `Data` | No | No | `—` | Final Destination |
| `currency` | `Link` | **Yes** | No | `Currency` | Currency |
| `exchange_rate` | `Float` | No | No | `—` | Exchange Rate |
| `items` | `Table` | No | No | `Proforma Invoice Item` | Line Items |
| `total_item_amount` | `Currency` | No | Yes | `currency` | Total Items Base Amount |
| `margin_percentage` | `Float` | **Yes** | No | `—` | Margin Percentage (%) |
| `margin_amount` | `Currency` | No | Yes | `currency` | Margin Amount |
| `freight` | `Currency` | No | No | `currency` | Freight Charges |
| `insurance` | `Currency` | No | No | `currency` | Insurance Charges |
| `packing_charges` | `Currency` | No | No | `currency` | Packing & Forwarding |
| `other_charges` | `Currency` | No | No | `currency` | Other Charges |
| `total_logistics` | `Currency` | No | Yes | `currency` | Total Logistics Cost |
| `grand_total` | `Currency` | No | Yes | `currency` | Grand Total Payable |
| `advance_percentage` | `Percent` | No | No | `—` | % Advance Required |
| `advance_amount` | `Currency` | No | Yes | `currency` | Advance Amount |
| `amount_in_words` | `Small Text` | No | Yes | `—` | Amount in Words |
| `beneficiary_name` | `Data` | No | No | `—` | Beneficiary Account Name |
| `beneficiary_acc_no` | `Data` | No | No | `—` | Beneficiary Account Number |
| `beneficiary_bank` | `Data` | No | No | `—` | Beneficiary Bank Name |
| `beneficiary_swift` | `Data` | No | No | `—` | Beneficiary SWIFT Code |
| `nostro_bank` | `Data` | No | No | `—` | Correspondent / Nostro Bank |
| `nostro_swift` | `Data` | No | No | `—` | Nostro SWIFT Code |
| `prepared_by` | `Data` | No | Yes | `—` | Prepared By |
| `authorized_signatory` | `Data` | No | No | `—` | Authorized Signatory |
| `remarks` | `Small Text` | No | No | `—` | Remarks / Notes |
| `amended_from` | `Link` | No | Yes | `Proforma Invoice` | Amended From |

---

## Proforma Invoice Item
- **Database Table**: `tabProforma Invoice Item`
- **DocType Classification**: Child Table (Sub-table)
- **Module**: Vendor Management
- **Description**: Child table storing line items, HSN codes, UOM, and base equipment rates for a Proforma Invoice.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `parent` | `VARCHAR(140)` | **Yes** | Yes | Parent DocType Key | Parent Document Reference |
| `parentfield` | `VARCHAR(140)` | **Yes** | Yes | String | Child Table Fieldname on Parent |
| `parenttype` | `VARCHAR(140)` | **Yes** | Yes | String | Parent DocType Name |
| `idx` | `INT(8)` | **Yes** | No | Integer | Row Ordering Index |
| `equipment` | `Link` | No | No | `Equipment` | Equipment Code |
| `item_description` | `Small Text` | **Yes** | No | `—` | Item Description |
| `make_model` | `Data` | No | No | `—` | Make / Model |
| `hsn_code` | `Data` | No | No | `—` | HSN Code |
| `unit` | `Link` | No | No | `UOM` | UOM |
| `quantity` | `Float` | **Yes** | No | `—` | Quantity |
| `base_rate` | `Currency` | **Yes** | No | `currency` | Base Rate |
| `amount` | `Currency` | No | Yes | `currency` | Amount |

---

## Vendor Payment
- **Database Table**: `tabVendor Payment`
- **DocType Classification**: Master / Transaction DocType
- **Module**: Vendor Management
- **Description**: Payment and remittance milestone tracking for approved Purchase Orders.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `naming_series` | `Select` | **Yes** | No | `VP-.YYYY.-` | Naming Series |
| `company` | `Link` | **Yes** | No | `Company` | Company |
| `supplier` | `Link` | **Yes** | No | `Supplier` | Supplier |
| `payment_date` | `Date` | **Yes** | No | `—` | Payment Date |
| `amount` | `Currency` | **Yes** | No | `currency` | Amount |
| `currency` | `Link` | **Yes** | No | `Currency` | Currency |
| `mode_of_payment` | `Link` | **Yes** | No | `Mode of Payment` | Mode of Payment |
| `reference_no` | `Data` | No | No | `—` | Reference No / UTR |
| `reference_date` | `Date` | No | No | `—` | Reference Date |
| `status` | `Select` | No | No | `, Draft, Pending Approval, Approved, Paid, Canc...` | Status |
| `remarks` | `Small Text` | No | No | `—` | Remarks |
| `amended_from` | `Link` | No | Yes | `Vendor Payment` | Amended From |

---

## Equipment
- **Database Table**: `tabEquipment`
- **DocType Classification**: Master / Transaction DocType
- **Module**: Equipment Management
- **Description**: Central repository for plant, machinery, heavy equipment, specifications, and serial tracking.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `equipment_code` | `Data` | No | Yes | `—` | Equipment Code |
| `equipment_name` | `Data` | **Yes** | No | `—` | Equipment Name |
| `category` | `Select` | **Yes** | No | `Mining Equipment, Laboratory Equipment, Constru...` | Category |
| `status` | `Select` | No | No | `Active, Discontinued, Pending Approval` | Status |
| `hsn_code` | `Data` | **Yes** | No | `—` | HSN Code |
| `brand` | `Data` | No | No | `—` | Brand |
| `manufacturer` | `Data` | No | No | `—` | Manufacturer |
| `model` | `Data` | No | No | `—` | Model |
| `specification` | `Text Editor` | No | No | `—` | Specification |
| `description` | `Text Editor` | No | No | `—` | Description |
| `image` | `Attach Image` | No | No | `—` | Image |
| `datasheet` | `Attach` | No | No | `—` | Datasheet |
| `country_of_origin` | `Link` | No | No | `Country` | Country of Origin |
| `unit` | `Link` | No | No | `UOM` | Unit |
| `approx_cost_inr` | `Currency` | No | No | `—` | Approx Cost (INR) |
| `approx_cost_usd` | `Currency` | No | No | `—` | Approx Cost (USD) |
| `last_purchase_cost_inr` | `Currency` | No | Yes | `—` | Last Purchase Cost (INR) |
| `last_purchase_cost_usd` | `Currency` | No | Yes | `—` | Last Purchase Cost (USD) |
| `gst_percentage` | `Percent` | No | No | `—` | GST Percentage |
| `preferred_vendor` | `Link` | No | No | `Supplier` | Preferred Vendor |
| `warranty_months` | `Int` | No | No | `—` | Warranty (Months) |
| `calibration_required` | `Check` | No | No | `—` | Calibration Required |
| `amc_applicable` | `Check` | No | No | `—` | AMC Applicable |

---

## Port
- **Database Table**: `tabPort`
- **DocType Classification**: Master / Transaction DocType
- **Module**: Vendor Management
- **Description**: International shipping ports of origin, discharge, and customs clearance.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `port_name` | `Data` | **Yes** | No | `—` | Port Name |
| `country` | `Link` | No | No | `Country` | Country |
| `port_code` | `Data` | No | No | `—` | Port Code |
| `is_active` | `Check` | No | No | `—` | Is Active |

---

## Company
- **Database Table**: `tabCompany`
- **DocType Classification**: Master / Transaction DocType
- **Module**: Setup
- **Description**: Operating entities including Parent LLP (SRI) and African / overseas subsidiaries.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `company_name` | `Data` | **Yes** | No | `—` | Company |
| `abbr` | `Data` | **Yes** | No | `—` | Abbr |
| `default_currency` | `Link` | **Yes** | No | `Currency` | Default Currency |
| `country` | `Link` | **Yes** | No | `Country` | Country |
| `is_group` | `Check` | No | No | `—` | Is Group |
| `default_holiday_list` | `Link` | No | No | `Holiday List` | Default Holiday List |
| `default_letter_head` | `Link` | No | No | `Letter Head` | Default Letter Head |
| `tax_id` | `Data` | No | No | `—` | Tax ID |
| `domain` | `Data` | No | No | `—` | Domain |
| `date_of_establishment` | `Date` | No | No | `—` | Date of Establishment |
| `parent_company` | `Link` | No | No | `Company` | Parent Company |
| `reporting_currency` | `Link` | No | Yes | `Currency` | Reporting Currency |
| `company_logo` | `Attach Image` | No | No | `—` | Company Logo |
| `date_of_incorporation` | `Date` | No | No | `—` | Date of Incorporation |
| `phone_no` | `Data` | No | No | `Phone` | Phone No |
| `email` | `Data` | No | No | `Email` | Email |
| `company_description` | `Text Editor` | No | No | `—` | Company Description |
| `date_of_commencement` | `Date` | No | No | `—` | Date of Commencement |
| `fax` | `Data` | No | No | `Phone` | Fax |
| `website` | `Data` | No | No | `—` | Website |
| `address_html` | `HTML` | No | No | `—` | address_html |
| `custom_registration_no` | `Data` | No | No | `—` | Company Registration No. |
| `custom_pan` | `Data` | No | No | `—` | PAN |
| `custom_tan` | `Data` | No | No | `—` | TAN |
| `custom_tin` | `Data` | No | No | `—` | TIN |
| `custom_vat_number` | `Data` | No | No | `—` | VAT Number |
| `custom_import_export_code` | `Data` | No | No | `—` | IEC (Import Export Code) |
| `custom_default_port` | `Data` | No | No | `—` | Default Port |
| `custom_default_cfa` | `Data` | No | No | `—` | Default CFA (Clearing & Forwarding Agent) |
| `custom_company_seal` | `Attach Image` | No | No | `—` | Company Seal |
| `custom_authorized_signatory` | `Data` | No | No | `—` | Authorized Signatory |
| `registration_details` | `Code` | No | No | `—` | Registration Details |
| `lft` | `Int` | No | Yes | `—` | Lft |
| `rgt` | `Int` | No | Yes | `—` | Rgt |
| `old_parent` | `Data` | No | Yes | `—` | old_parent |
| `create_chart_of_accounts_based_on` | `Select` | No | No | `, Standard Template, Existing Company` | Create Chart Of Accounts Based On |
| `existing_company` | `Link` | No | No | `Company` | Existing Company  |
| `chart_of_accounts` | `Select` | No | No | `—` | Chart Of Accounts Template |
| `default_bank_account` | `Link` | No | No | `Account` | Default Bank Account |
| `default_cash_account` | `Link` | No | No | `Account` | Default Cash Account |
| `default_receivable_account` | `Link` | No | No | `Account` | Default Receivable Account |
| `default_payable_account` | `Link` | No | No | `Account` | Default Payable Account |
| `write_off_account` | `Link` | No | No | `Account` | Write Off Account |
| `unrealized_profit_loss_account` | `Link` | No | No | `Account` | Unrealized Profit / Loss Account |
| `allow_account_creation_against_child_company` | `Check` | No | No | `—` | Allow Account Creation Against Child Company |
| `default_expense_account` | `Link` | No | No | `Account` | Default Cost of Goods Sold Account |
| `default_income_account` | `Link` | No | No | `Account` | Default Income Account |
| `default_discount_account` | `Link` | No | No | `Account` | Default Payment Discount Account |
| `payment_terms` | `Link` | No | No | `Payment Terms Template` | Default Payment Terms Template |
| `cost_center` | `Link` | No | No | `Cost Center` | Default Cost Center |
| `default_finance_book` | `Link` | No | No | `Finance Book` | Default Finance Book |
| `exchange_gain_loss_account` | `Link` | No | No | `Account` | Exchange Gain / Loss Account |
| `unrealized_exchange_gain_loss_account` | `Link` | No | No | `Account` | Unrealized Exchange Gain/Loss Account |
| `round_off_account` | `Link` | No | No | `Account` | Round Off Account |
| `round_off_cost_center` | `Link` | No | No | `Cost Center` | Round Off Cost Center |
| `round_off_for_opening` | `Link` | No | No | `Account` | Round Off for Opening |
| `default_deferred_revenue_account` | `Link` | No | No | `Account` | Default Deferred Revenue Account |
| `default_deferred_expense_account` | `Link` | No | No | `Account` | Default Deferred Expense Account |
| `book_advance_payments_in_separate_party_account` | `Check` | No | No | `—` | Book Advance Payments in Separate Party Account |
| `reconcile_on_advance_payment_date` | `Check` | No | No | `—` | Reconcile on Advance Payment Date |
| `reconciliation_takes_effect_on` | `Select` | No | No | `Advance Payment Date, Oldest Of Invoice Or Adva...` | Reconciliation Takes Effect On |
| `default_advance_received_account` | `Link` | No | No | `Account` | Default Advance Received Account |
| `default_advance_paid_account` | `Link` | No | No | `Account` | Default Advance Paid Account |
| `auto_exchange_rate_revaluation` | `Check` | No | No | `—` | Auto Create Exchange Rate Revaluation |
| `auto_err_frequency` | `Select` | No | No | `Daily, Weekly, Monthly` | Frequency |
| `submit_err_jv` | `Check` | No | No | `—` | Submit ERR Journals? |
| `exception_budget_approver_role` | `Link` | No | No | `Role` | Exception Budget Approver Role |
| `accumulated_depreciation_account` | `Link` | No | No | `Account` | Accumulated Depreciation Account |
| `depreciation_expense_account` | `Link` | No | No | `Account` | Depreciation Expense Account |
| `series_for_depreciation_entry` | `Data` | No | No | `—` | Series for Asset Depreciation Entry (Journal Entry) |
| `disposal_account` | `Link` | No | No | `Account` | Gain/Loss Account on Asset Disposal |
| `depreciation_cost_center` | `Link` | No | No | `Cost Center` | Asset Depreciation Cost Center |
| `capital_work_in_progress_account` | `Link` | No | No | `Account` | Capital Work In Progress Account |
| `asset_received_but_not_billed` | `Link` | No | No | `Account` | Asset Received But Not Billed |
| `accounts_frozen_till_date` | `Date` | No | No | `—` | Accounts Frozen Till Date |
| `role_allowed_for_frozen_entries` | `Link` | No | No | `Role` | Roles Allowed to Set and Edit Frozen Account Entries |
| `default_buying_terms` | `Link` | No | No | `Terms and Conditions` | Default Buying Terms |
| `sales_monthly_history` | `Small Text` | No | Yes | `—` | Sales Monthly History |
| `monthly_sales_target` | `Currency` | No | No | `default_currency` | Monthly Sales Target |
| `total_monthly_sales` | `Currency` | No | Yes | `default_currency` | Total Monthly Sales |
| `default_selling_terms` | `Link` | No | No | `Terms and Conditions` | Default Selling Terms |
| `default_sales_contact` | `Link` | No | No | `Contact` | Default Sales Contact |
| `default_warehouse_for_sales_return` | `Link` | No | No | `Warehouse` | Default Warehouse for Sales Return |
| `credit_limit` | `Currency` | No | No | `default_currency` | Credit Limit |
| `transactions_annual_history` | `Code` | No | Yes | `—` | Transactions Annual History |
| `purchase_expense_account` | `Link` | No | No | `Account` | Purchase Expense Account |
| `service_expense_account` | `Link` | No | No | `Account` | Service Expense Account |
| `purchase_expense_contra_account` | `Link` | No | No | `Account` | Purchase Expense Contra Account |
| `expenses_added_to_stock_account` | `Link` | No | No | `Account` | Expenses Added To Stock Account |
| `expenses_added_to_stock_contra_account` | `Link` | No | No | `Account` | Expenses Added To Stock Contra Account |
| `enable_perpetual_inventory` | `Check` | No | No | `—` | Enable Perpetual Inventory |
| `enable_item_wise_inventory_account` | `Check` | No | No | `—` | Enable Item-wise Inventory Account |
| `enable_provisional_accounting_for_non_stock_items` | `Check` | No | No | `—` | Enable Provisional Accounting For Non Stock Items |
| `default_inventory_account` | `Link` | No | No | `Account` | Default Inventory Account |
| `valuation_method` | `Select` | **Yes** | No | `FIFO, Moving Average, LIFO` | Default Stock Valuation Method |
| `stock_adjustment_account` | `Link` | No | No | `Account` | Stock Adjustment Account |
| `stock_received_but_not_billed` | `Link` | No | No | `Account` | Stock Received But Not Billed |
| `default_provisional_account` | `Link` | No | No | `Account` | Default Provisional Account |
| `default_in_transit_warehouse` | `Link` | No | No | `Warehouse` | Default In-Transit Warehouse |
| `default_operating_cost_account` | `Link` | No | No | `Account` | Default Operating Cost Account |
| `default_wip_warehouse` | `Link` | No | No | `Warehouse` |  Default Work In Progress Warehouse  |
| `default_fg_warehouse` | `Link` | No | No | `Warehouse` | Default Finished Goods Warehouse |
| `default_scrap_warehouse` | `Link` | No | No | `Warehouse` | Default Scrap Warehouse |

---

## Supplier
- **Database Table**: `tabSupplier`
- **DocType Classification**: Master / Transaction DocType
- **Module**: Buying
- **Description**: Approved vendor, contractor, and internal subsidiary party records with banking and tax credentials.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `pan` | `Data` | No | No | `—` | PAN |
| `naming_series` | `Select` | No | No | `SUP-.YYYY.-` | Series |
| `supplier_name` | `Data` | **Yes** | No | `—` | Supplier Name |
| `supplier_name_in_arabic` | `Data` | No | No | `—` | Supplier Name in Arabic |
| `supplier_type` | `Select` | **Yes** | No | `Company, Individual, Partnership` | Supplier Type |
| `custom_independent_company` | `Check` | No | No | `—` | Independent Company |
| `alias` | `Data` | No | No | `—` | Alias |
| `gender` | `Link` | No | No | `Gender` | Gender |
| `supplier_group` | `Link` | No | No | `Supplier Group` | Supplier Group |
| `country` | `Link` | No | No | `Country` | Country |
| `image` | `Attach Image` | No | No | `—` | Image |
| `custom_vendor_code` | `Data` | No | No | `—` | Vendor Code |
| `custom_vendor_type` | `Select` | No | No | `, Manufacturer, Trader, Service Provider, Logis...` | Vendor Type |
| `custom_pan` | `Data` | No | No | `—` | PAN Number |
| `custom_tin` | `Data` | No | No | `—` | TIN Number |
| `custom_website` | `Data` | No | No | `—` | Website |
| `custom_bank_name` | `Data` | No | No | `—` | Bank Name |
| `custom_bank_branch` | `Data` | No | No | `—` | Bank Branch |
| `custom_account_number` | `Data` | No | No | `—` | Account Number |
| `custom_ifsc` | `Data` | No | No | `—` | IFSC Code |
| `custom_swift_code` | `Data` | No | No | `—` | SWIFT Code |
| `custom_iban` | `Data` | No | No | `—` | IBAN |
| `custom_bank_currency` | `Link` | No | No | `Currency` | Bank Currency |
| `custom_gst_applicable` | `Check` | No | No | `—` | GST Applicable |
| `custom_gst_percentage` | `Percent` | No | No | `—` | GST Percentage |
| `custom_tds_applicable` | `Check` | No | No | `—` | TDS Applicable |
| `custom_tds_percentage` | `Percent` | No | No | `—` | TDS Percentage |
| `custom_vendor_rating` | `Rating` | No | No | `—` | Vendor Rating |
| `custom_preferred_vendor` | `Check` | No | No | `—` | Preferred Vendor |
| `custom_lead_time_days` | `Int` | No | No | `—` | Lead Time (Days) |
| `custom_approved` | `Check` | No | No | `—` | Approved Vendor |
| `custom_vendor_remarks` | `Small Text` | No | No | `—` | Vendor Remarks |
| `custom_vendor_documents` | `Attach` | No | No | `—` | Vendor Documents |
| `default_currency` | `Link` | No | No | `Currency` | Billing Currency |
| `default_bank_account` | `Link` | No | No | `Bank Account` | Company Bank Account |
| `default_price_list` | `Link` | No | No | `Price List` | Price List |
| `payment_terms` | `Link` | No | No | `Payment Terms Template` | Payment Terms Template |
| `address_html` | `HTML` | No | Yes | `—` | Address HTML |
| `contact_html` | `HTML` | No | Yes | `—` | Contact HTML |
| `supplier_primary_address` | `Link` | No | No | `Address` | Primary Address |
| `primary_address` | `Text Editor` | No | Yes | `—` | Primary Address Preview |
| `supplier_primary_contact` | `Link` | No | No | `Contact` | Primary Contact |
| `mobile_no` | `Read Only` | No | No | `—` | Mobile No |
| `email_id` | `Read Only` | No | No | `—` | Email ID |
| `accounts` | `Table` | No | No | `Party Account` | Per-Company Accounts |
| `is_internal_supplier` | `Check` | No | No | `—` | Is Internal Supplier |
| `represents_company` | `Link` | No | No | `Company` | Represents Company |
| `companies` | `Table` | No | No | `Allowed To Transact With` | Allowed to transact with |
| `tax_id` | `Data` | No | No | `—` | GSTIN |
| `irs_1099` | `Check` | No | No | `—` | Is IRS 1099 reporting required for supplier? |
| `tax_category` | `Link` | No | No | `Tax Category` | Tax Category |
| `tax_withholding_category` | `Link` | No | No | `Tax Withholding Category` | Tax Withholding Category |
| `tax_withholding_group` | `Link` | No | No | `Tax Withholding Group` | Tax Withholding Group |
| `is_transporter` | `Check` | No | No | `—` | Is Transporter |
| `allow_purchase_invoice_creation_without_purchase_order` | `Check` | No | No | `—` | Allow purchase invoice creation without purchase order |
| `allow_purchase_invoice_creation_without_purchase_receipt` | `Check` | No | No | `—` | Allow purchase invoice creation without purchase receipt |
| `disabled` | `Check` | No | No | `—` | Disabled |
| `is_frozen` | `Check` | No | No | `—` | Is Frozen |
| `on_hold` | `Check` | No | No | `—` | Block Supplier |
| `hold_type` | `Select` | No | No | `All, Invoices, Payments` | Hold Type |
| `release_date` | `Date` | No | No | `—` | Release Date |
| `warn_rfqs` | `Check` | No | Yes | `—` | Warn RFQs |
| `prevent_rfqs` | `Check` | No | Yes | `—` | Prevent RFQs |
| `warn_pos` | `Check` | No | Yes | `—` | Warn POs |
| `prevent_pos` | `Check` | No | Yes | `—` | Prevent POs |
| `portal_users` | `Table` | No | No | `Portal User` | Supplier Portal Users |
| `website` | `Data` | No | No | `—` | Website |
| `language` | `Link` | No | No | `Language` | Print Language |
| `supplier_details` | `Text` | No | No | `—` | Supplier Details |
| `customer_numbers` | `Table` | No | No | `Customer Number At Supplier` | Customer Numbers |

---

## Letter Head
- **Database Table**: `tabLetter Head`
- **DocType Classification**: Master / Transaction DocType
- **Module**: Printing
- **Description**: Corporate stationery assets and full-page letterhead background graphics.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `letter_head_name` | `Data` | **Yes** | No | `—` | Letter Head Name |
| `source` | `Select` | No | No | `Image, HTML` | Letter Head Based On |
| `footer_source` | `Select` | No | No | `Image, HTML` | Footer Based On |
| `disabled` | `Check` | No | No | `—` | Disabled |
| `is_default` | `Check` | No | No | `—` | Default Letter Head |
| `image` | `Attach Image` | No | No | `—` | Image |
| `image_height` | `Float` | No | No | `—` | Image Height (px) |
| `image_width` | `Float` | No | No | `—` | Image Width (px) |
| `align` | `Select` | No | No | `Left, Right, Center` | Align |
| `content` | `HTML Editor` | No | No | `—` | Header HTML |
| `footer` | `HTML Editor` | No | No | `—` | Footer HTML |
| `footer_image` | `Attach Image` | No | No | `—` | Image |
| `footer_image_height` | `Float` | No | No | `—` | Image Height (px) |
| `footer_image_width` | `Float` | No | No | `—` | Image Width (px) |
| `footer_align` | `Select` | No | No | `Left, Right, Center` | Align |
| `header_script` | `Code` | No | No | `Javascript` | Header Script |
| `footer_script` | `Code` | No | No | `Javascript` | Footer Script |
| `instructions` | `HTML` | No | Yes | `—` | Instructions |

---

## Terms and Conditions
- **Database Table**: `tabTerms and Conditions`
- **DocType Classification**: Master / Transaction DocType
- **Module**: Setup
- **Description**: Standardized legal, export, Phytosanitary, and jurisdiction contract templates.

| Column Name (`fieldname`) | SQL / Frappe Type | Req? | Read-Only | Options / Foreign Key | Label / Description |
|---|---|---|---|---|---|
| `name` | `VARCHAR(140)` | **Yes** | Yes | Primary Key | Document Unique Identifier |
| `creation` | `DATETIME(6)` | **Yes** | Yes | System | Creation Timestamp |
| `modified` | `DATETIME(6)` | **Yes** | Yes | System | Last Modified Timestamp |
| `modified_by` | `VARCHAR(140)` | **Yes** | Yes | User | Last Modified By User |
| `owner` | `VARCHAR(140)` | **Yes** | Yes | User | Document Creator / Owner |
| `docstatus` | `INT(1)` | **Yes** | Yes | `0=Draft, 1=Submitted, 2=Cancelled` | Submission Status |
| `title` | `Data` | **Yes** | No | `—` | Title |
| `disabled` | `Check` | No | No | `—` | Disabled |
| `copy_attachments_to_transaction` | `Check` | No | No | `—` | Copy Attachments to Transaction |
| `selling` | `Check` | No | No | `—` | Selling |
| `buying` | `Check` | No | No | `—` | Buying |
| `terms` | `Text Editor` | No | No | `—` | Terms and Conditions |
| `terms_and_conditions_help` | `HTML` | No | No | `<h4>Standard Terms and Conditions Example</h4>,...` | Terms and Conditions Help |

---

