# Sarveksha ERP

Custom Frappe Application for Sarveksha ERP and Vendor Management.

## Features

1. **Vendor Management & Payment Tracking**
   - **Vendor Purchase Orders:** Manage purchase orders raised to vendors with multi-currency support, tax calculation, payment terms, and delivery tracking.
   - **Vendor Payments:** Record and track payment transactions (`VP-.YYYY.-`) linked to companies and suppliers.
   - **Supplier Integration:** Seamlessly integrated with standard ERPNext `Supplier` and `Company` DocTypes.

2. **Automated Data Setup & Initialization**
   - Built-in `after_install` hooks to initialize multi-entity company structures (India, Guinea, Senegal, Botswana, Mauritius, Sierra Leone, UAE).
   - Automatic seeding of Supplier Groups and Fiscal Years.
   - Automatic import of Vendor master lists from Excel datasets (`VendorList-sarveksha.xlsx`).

3. **Workspace & Navigation**
   - Custom **Vendor Management** Workspace and Workspace Sidebar.
   - Quick access shortcuts for Suppliers, Companies, and Vendor Payments.

---

## Installation & Setup

1. **Get the App**
   ```bash
   bench get-app https://github.com/manikkDev/employee-erp-test.git
   ```

2. **Install on Site**
   ```bash
   bench --site <site-name> install-app sarveksha_erp
   ```

3. **Run Migration & Data Setup**
   ```bash
   bench --site <site-name> migrate
   ```

---

## Technical Architecture

| Component | Path |
|---|---|
| Module Definitions | `sarveksha_erp/modules.txt` |
| Vendor Purchase Order DocType | `sarveksha_erp/vendor_management/doctype/vendor_purchase_order/` |
| Vendor Payment DocType | `sarveksha_erp/vendor_management/doctype/vendor_payment/` |
| Workspace Definition | `sarveksha_erp/vendor_management/workspace/vendor_management/` |
| Data Fixtures | `sarveksha_erp/fixtures/` |


