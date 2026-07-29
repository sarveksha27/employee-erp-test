<div align="center">
  <h1>Sarveksha ERP</h1>
  <p><strong>Vendor Procurement & Payment Tracking System</strong></p>
  <p>A collaborative, multi-company ERP portal built on the Frappe Framework and ERPNext.</p>
</div>

---

## 📖 Overview

**Sarveksha ERP** is a full-stack, metadata-driven web application tailored for **Sarveksha Realty and Inframine LLP (SRI)**. Designed to streamline international logistics and heavy engineering procurement, the system manages everything from multi-company accounting across continents to complex Vendor Purchase Order generation.

It leverages the power of **Frappe** (Python/JS) and **MariaDB**, running within a highly standardized **Docker/Dev Container** environment to ensure seamless team collaboration and zero-friction onboarding.

---

## 🌟 Core Modules

### 1. Multi-Company Architecture (Company Master)
The foundation of the ERP supports **9 independent entities** spanning India, Africa, and the Middle East.
- **Global Compartmentalization:** Companies are isolated by jurisdiction, preventing accidental ledger crossing.
- **Regional Fiscal Years:** Built-in programmatic mappings for localized financial calendars (e.g., April-March for India, Jan-Dec for International branches).
- **Default Currencies & Trade Zones:** Automated defaulting of currencies (USD for non-India branches) and designated default shipment ports (e.g., Mundra, Conakry, Durban).

### 2. Vendor Management (Supplier Master)
A robust, categorized vendor database designed to handle high-value international procurement.
- **Granular Data Collection:** Tracks GSTIN, PAN, Bank Details, SWIFT/IBAN, and tax applicability (GST/TDS).
- **Independent Company Flows:** Custom dynamic routing that toggles between standard ERPNext logic and customized vendor portal logic based on User and Supplier profiles.
- **Categorization:** Segmentation by Supplier Groups (Mining & Resources, Equipment, Logistics) for detailed reporting.

### 3. Equipment Master
A specialized catalog for heavy engineering, laboratory, construction, electrical, and chemical equipment.
- **Comprehensive Metadata:** Tracks HSN codes, manufacturer details, warranties, technical specifications, and datasheets.
- **Dual-Currency Costing:** Monitors approximate and historical purchase costs in both INR and USD.
- **Pre-Seeded Data:** Ships with thousands of high-integrity, normalized equipment records.

### 4. Purchase Order Generation
The centerpiece of the system, automating the end-to-end procurement lifecycle.
1. **Child Company Requirement:** International branch requests equipment.
2. **Parent PO Issuance:** SRI (India) generates an automated PO to an Indian Vendor.
3. **Proforma Invoice (PI) Management:** Handles vendor PI and generates a simplified PI for the Child Company (including logistics margins).
4. **Auto-Calculations:** Dynamic JavaScript logic auto-calculates taxes, freight, insurance, and complex payment tranches (Advance, Partial, Final).
5. **Shipping Document Tracking:** Real-time tracking of Bill of Lading, Commercial Invoices, and CFA documents until delivery.

---

## 🛠️ Technology Stack

- **Framework:** Frappe (Python & JavaScript)
- **Base Application:** ERPNext
- **Database:** MariaDB
- **Caching & Queues:** Redis
- **Infrastructure:** Docker, Dev Containers, Ubuntu (WSL2 for Windows users)
- **Deployment:** Gunicorn, NGINX, Supervisor

---

## 🚀 Development Setup

We enforce a strict **Docker Dev Container** workflow. Do not attempt to run this application natively on Windows or macOS outside of the provided container.

### 1. Initialize the Environment
Ensure you have Docker Desktop and VS Code installed. Open the base `frappe_docker` dev container.

### 2. Clone the App
From your VS Code terminal (inside the container), navigate to your bench and fetch the repository:
```bash
cd /workspace/development/frappe-bench
bench get-app https://github.com/manikkDev/employee-erp-test.git
```

### 3. Install on the Development Site
Install the app onto your local tenant database (`development.localhost`):
```bash
bench --site development.localhost install-app sarveksha_erp
```
> [!NOTE] 
> Always use `development.localhost` (without `http://` or ports) in bench commands.

### 4. Run Migrations & Start
Sync the database schemas and load the JSON fixtures (pre-seeded equipment, companies, and custom fields):
```bash
bench --site development.localhost migrate
bench start
```
Your ERP portal is now live at: `http://development.localhost:8000`

---

## 🤝 Collaboration & Version Control

Because Frappe is a metadata-driven framework, most "code" you write is actually JSON configurations (DocTypes, Workspaces, Custom Fields). 

### The Workflow
1. **Pull Latest Changes:** Always start by pulling the latest from the main integration branch.
2. **Branch Out:** `git checkout -b <your-name>/<feature-name>`
3. **Export Your Work:** After making changes in the Frappe UI, you **must** export them to the filesystem before committing:
   ```bash
   # Exporting a new DocType
   bench --site development.localhost export-doc DocType "Vendor Purchase Order"
   
   # Exporting Custom Fields, Roles, or Print Formats (Fixtures)
   bench --site development.localhost export-fixtures
   ```
4. **Commit & Push:** Commit your generated JSON and Python files, then push to GitHub and open a Pull Request.

> [!CAUTION]
> Never make direct database changes using raw SQL if they affect the schema. Always use the Frappe framework's Custom Fields or DocType builder so the changes can be tracked in Git.

---

## 🌍 Production Deployment Architecture

When transitioning from demo to production, we utilize an industry-standard Frappe architecture:
- **Web Server:** **Gunicorn** acts as the Python WSGI HTTP server, handling concurrent backend requests.
- **Reverse Proxy:** **NGINX** serves static assets (CSS/JS) and routes traffic securely via HTTPS.
- **Process Management:** **Supervisor** ensures background workers (Redis queues, scheduled jobs) automatically recover from crashes.
- **CI/CD:** Automated GitHub Actions trigger builds, execute `bench migrate` to safely upgrade the database schema without data loss, and seamlessly restart Gunicorn.

---

<div align="center">
  <i>Developed for Sarveksha Realty and Inframine LLP</i>
</div>
