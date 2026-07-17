# Sarveksha Vendor Payment Tracking ERPNext Custom App

A production-ready custom Frappe application for tracking vendor contracts, schedules, clearings, shipments, bank details, and payments in ERPNext v16.

## Features Included
- **Multi-Company Setup**: Supports configurations for India, UAE, Guinea, Cameroon, Botswana, and Sierra Leone with local currencies and tax setups.
- **Custom DocTypes**:
  - `Vendor Contract` (Naming: `CON-.YYYY.-`)
  - `Vendor Bank`
  - `Vendor Payment Request` (Naming: `PAY-.YYYY.-`)
  - `Vendor Payment Schedule`
  - `Equipment` (Naming: `EQ-.YYYY.-`)
  - `Shipment` (Naming: `SHIP-.YYYY.-`)
  - `Shipment Item` (Child Table)
  - `Customs Clearance`
  - `Payment Approval`
  - `Payment Batch`
  - `Payment Batch Entry` (Child Table)
  - `Audit Log`
  - `Intercompany Transfer`
- **Setup Script**: `setup_demo.py` automatically initializes:
  - Default payment terms (Immediate, 30 days, 60 days, advance options, LC)
  - Custom roles (Finance Manager, Purchase Manager, etc.)
  - Realistic multi-currency and tax records
  - High-quality dummy data (20+ vendors, 10+ equipments, 15+ POs/Invoices, etc.)
- **Custom Workspace**: A sleek custom workspace called "Vendor Payment Tracking" with Shortcuts, Dashboards, and Reports.
- **Reports**: Standard Script Reports including Vendor Ledger, Outstanding Payments, Payment Aging, etc.
- **Dashboard**: Interactive dashboard for tracking payment metrics.

## Installation

```bash
bench get-app https://github.com/umeshraj2007/sarveksha_vendor.git
bench --site <site-name> install-app sarveksha_vendor
bench migrate
```

## Running Demo Setup

To populate the system with standard currencies, local tax templates, default roles, bank accounts, and high-quality mock data, execute the setup command:

```bash
bench --site <site-name> execute sarveksha_vendor.setup.install.after_install
```
