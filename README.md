# Sarveksha ERP

**Sarveksha ERP** is a modular, enterprise-grade Procurement & Equipment Management app built on the Frappe Framework for the Sarveksha Group of companies (India, Sierra Leone, Cameroon, Botswana, Guinea, United States).

---

## Key Features

- **Multi-Entity Company Master**: Supports 6 global entities (SRI, OHL, SSL, SMS, SBPL, SGIN) with country-specific tax rules, default currencies (**INR** for India, **USD** for foreign branches), IEC codes (`AFTFS2557J` for SRI), and default export ports (Mundra, JNPT, Conakry, Durban, Freetown, Douala).
- **Vendor Master & Rating**: Vendor management with commercial terms, bank accounts, SWIFT/IBAN, lead times, tax settings, and rating systems.
- **Equipment Catalogue & HSN Master**: Equipment master indexed by HSN codes with technical specifications, warranty, calibration requirements, AMC tracking, and preferred vendors.
- **Purchase Order & Procurement Lifecycle**: Complete end-to-end tracking for procurement up to PO stage (`Equipment Enquiry ➔ Vendor Selection ➔ Quotation ➔ Purchase Order`).
- **PDF Auto-Filler Engine**: Built-in parser to extract company, vendor, equipment, quotation, and pricing details directly from attached PDF documents.
- **Modular & Extensible Architecture**: Clean module boundaries allowing future modules (e.g. `Sarveksha Procurement`, `Sarveksha Vendor Portal`, `Sarveksha Logistics`, `Sarveksha Finance`) to plug in seamlessly.

---

## Prerequisites

Before installing the Sarveksha ERP app, ensure your environment meets the following requirements:

- **Bench CLI**: v5.x or later
- **Frappe Framework**: v15.x or v16.x
- **Python**: 3.10+
- **Database**: MariaDB 10.6+ / PostgreSQL 14+
- **Cache**: Redis
- **Node.js**: v18+

---

## Installation & Setup

Follow these commands to install and set up `sarveksha_erp` on your bench instance:

### Step 1: Fetch the App
Run from your bench directory:
```bash
bench get-app https://github.com/sarveksha/sarveksha_erp.git
# Or if local directory:
bench get-app /path/to/sarveksha_erp
```

### Step 2: Install App on Target Site
Install the app onto your site:
```bash
bench --site <your-site-name> install-app sarveksha_erp
```

### Step 3: Run Database Migration
Ensure all doctypes and schema changes are applied:
```bash
bench --site <your-site-name> migrate
```

### Step 4: Seed Data Initializer
To automatically create standard tax configurations, default company profiles, vendors, equipment catalogue, and initial purchase orders, run:
```bash
bench --site <your-site-name> execute sarveksha_erp.setup.install.after_install
```

## Equipment & Engineering Goods Input Methods

Equipment details for engineering goods and related materials (from `HSN-Codes-for-GST-Enrolment.pdf`) are filtered by **Engineering HSN Chapters** (**84** Mechanical, **85** Electrical, **87** Heavy Handling/Vehicles, **90** Instrumentation/Lab Testing):

1. **Automated Seed Data Initializer**:
   Initializes core engineering items (Spectrometers, Furnaces, Cranes, Networking setups, Glassware sets) via `bench execute sarveksha_erp.setup.install.after_install`.

2. **Bulk Import via Data Import Tool (Excel / CSV)**:
   - `Sarveksha Equipment` has `"allow_import": 1` enabled.
   - Users can bulk upload engineering catalogues via **Desk ➔ Data Import** using Excel/CSV templates with columns: `HSN Code`, `Equipment Name`, `Category`, `Brand`, `Manufacturer`, `Model`, `GST %`, `Technical Specification`, `Preferred Vendor`.

3. **Engineering HSN Filtering Helper Script**:
   - `sarveksha_erp.setup.hsn_importer.filter_and_import_engineering_equipment(records)` automatically filters raw HSN datasets to ensure only engineering commodities (Chapters 84, 85, 87, 90) are created in the database.

4. **Document PDF Auto-Fill**:
   - Uploading a Quotation or PO PDF on a `Sarveksha Purchase Order` automatically extracts equipment names, HSN codes, rates, and specs into the document.

---

## Module Architecture & Doctypes

| Doctype | Type | Purpose |
| :--- | :--- | :--- |
| `Sarveksha Company` | Setup / Master | Global entity profiles, tax IDs (GST/PAN/TAN/IEC), currencies, ports, and default banks |
| `Sarveksha Vendor` | Master | Vendor registry with billing terms, SWIFT/IBAN bank details, lead times, and ratings |
| `Sarveksha Equipment` | Master | Equipment master catalog keyed by HSN codes with technical specs and warranty details |
| `Sarveksha Tax Configuration` | Setup | Country-specific tax rules (India GST/TDS, Botswana VAT/WHT, Cameroon VAT, Sierra Leone VAT, Guinea VAT) |
| `Sarveksha Purchase Order` | Transaction | Complete procurement lifecycle tracking up to PO creation with pricing calculations and PDF auto-fill |
| `Sarveksha Document` | Media | Centralized file & export document attachments repository |

---

## Modular Extension Guide

`sarveksha_erp` is designed with modular expansion in mind. To add a new module (e.g. `Sarveksha Logistics`):

1. Register the module name in `sarveksha_erp/modules.txt`.
2. Add your Doctype under `sarveksha_erp/sarveksha_erp/doctype/<doctype_name>/`.
3. Link workspace cards or reports in `workspace_sidebar/sarveksha_erp.json`.
4. Run `bench migrate`.

---

## License

Released under the **MIT License**. Copyright (c) 2026 Sarveksha Group.
