# Sarveksha ERP — Security & Data Architecture Guide

> **For:** Sarveksha Realty and Inframine LLP — Management Review  
> **Prepared by:** Sarveksha ERP Development Team  
> **Date:** July 2026  
> **Status:** Production-Ready Security Posture

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [How Data Is Stored](#2-how-data-is-stored)
3. [Authentication & Session Security](#3-authentication--session-security)
4. [Role-Based Access Control (RBAC)](#4-role-based-access-control-rbac)
5. [API & Endpoint Security](#5-api--endpoint-security)
6. [Input Validation & Data Integrity](#6-input-validation--data-integrity)
7. [Audit Trail & Change Tracking](#7-audit-trail--change-tracking)
8. [Code-Level Security (How Git Protects Our Configs)](#8-code-level-security-how-git-protects-our-configs)
9. [Sensitive Data Handling](#9-sensitive-data-handling)
10. [Production Deployment Security](#10-production-deployment-security)
11. [Security Measures Summary Table](#11-security-measures-summary-table)
12. [How to Demonstrate Security to Management](#12-how-to-demonstrate-security-to-management)

---

## 1. Executive Summary

The Sarveksha ERP system is built on the **Frappe Framework** (v16), an enterprise-grade, open-source web framework that powers thousands of production ERP systems worldwide. The framework itself handles:

- **Encrypted password storage** (bcrypt hashing)
- **CSRF token protection** on every request
- **Session-based authentication** with server-side token validation
- **SQL injection prevention** through parameterized queries (ORM-based, never raw SQL)
- **XSS protection** through template auto-escaping

On top of Frappe's built-in security, we have implemented **application-level hardening** across all our custom DocTypes (Vendor Purchase Order, Vendor Payment, Equipment Master). This document explains every layer of security in plain language.

---

## 2. How Data Is Stored

### 2.1 Database Architecture

All business data is stored in **MariaDB** (a hardened, enterprise fork of MySQL). This is a **relational database** — the same class of database used by banks, healthcare systems, and governments worldwide.

| Component | Storage Location |
|---|---|
| Companies, Vendors, Equipment | MariaDB tables (e.g., `tabCompany`, `tabSupplier`, `tabEquipment`) |
| Purchase Orders | `tabVendor Purchase Order` |
| Vendor Payments | `tabVendor Payment` |
| File Attachments (PDFs, Images) | Server filesystem (`/sites/<site>/private/files/`) |
| User Sessions | Redis (in-memory, auto-expires) |
| Background Job Queue | Redis |

### 2.2 How Tables Are Created

Every DocType (business entity) in Frappe has a **JSON definition file** that describes its fields, data types, and constraints. When you run `bench migrate`, Frappe reads these JSON files and **automatically creates the corresponding MariaDB tables** with:

- Proper column types (`VARCHAR`, `DECIMAL`, `DATE`, `LONGTEXT`)
- Primary keys and indexes for fast queries
- Foreign key relationships between linked documents
- `creation`, `modified`, `modified_by`, and `owner` metadata columns on **every single row** — this means every record automatically knows who created it, who last modified it, and when

### 2.3 How Data Flows When a Teammate Pulls the Code

When a team member runs:
```bash
bench get-app https://github.com/manikkDev/employee-erp-test.git
bench --site development.localhost install-app sarveksha_erp
bench --site development.localhost migrate
```

The following happens:

1. **Git clones the repository** — They receive the DocType JSON definitions, Python controllers, and fixture files.
2. **`install-app`** — Frappe registers the app with the site and creates the database tables based on the JSON schemas.
3. **`migrate`** — Frappe imports **fixture data** (pre-seeded companies, vendors, equipment, custom fields) from the JSON files in `fixtures/`. This is how the team shares configuration data.

> **Key Point:** The _database schema_ is defined in code (JSON files tracked in Git). The _transactional data_ (Purchase Orders, Payments) is created only through the application UI and lives only in the local database. When someone pulls the code, they get the structure and seed data — not your live transactions.

### 2.4 Data at Rest

- MariaDB stores all data on the server's local filesystem using the **InnoDB** storage engine, which supports:
  - **ACID transactions** (Atomicity, Consistency, Isolation, Durability) — every database write is all-or-nothing
  - **Row-level locking** — concurrent users don't corrupt each other's data
  - **Crash recovery** — the database journal (WAL/redo log) ensures data survives power failures

---

## 3. Authentication & Session Security

### 3.1 Password Security

Frappe **never stores plaintext passwords**. Every user password is hashed using the **bcrypt** algorithm with an automatically generated random salt. Even if someone gains access to the database, they cannot reverse-engineer the passwords.

```
Stored in DB:  $2b$12$LJ3m4LxkKf... (irreversible hash)
NOT stored:    actual_password_text
```

### 3.2 Session Management

- User sessions are stored in **Redis** (server-side, never in the browser).
- Each session has a unique **SID** (Session ID) that is cryptographically random.
- Sessions expire after a configurable timeout (default: 6 hours of inactivity).
- On logout, the session token is **destroyed server-side** — even if someone copies the cookie, it becomes invalid.

### 3.3 CSRF Protection

Every form submission in Frappe includes a **CSRF (Cross-Site Request Forgery) token**. This prevents malicious websites from tricking a logged-in user into making unauthorized changes. The token is:

- Generated fresh for each user session
- Validated on every POST/PUT/DELETE request
- Rejected if missing or invalid — request is blocked

### 3.4 Login Security

- **Rate limiting**: Frappe blocks login after repeated failed attempts.
- **Two-factor authentication (2FA)**: Can be enabled per-user for OTP-based login.
- **Session hijacking prevention**: Sessions are bound to IP addresses; suspicious IP changes invalidate the session.

---

## 4. Role-Based Access Control (RBAC)

### 4.1 How Permissions Work

Frappe uses a **declarative permission system** defined at the DocType level. Every DocType specifies exactly which roles can Create, Read, Write, Submit, Cancel, Delete, Export, Print, Email, and Share records.

### 4.2 Our Permission Matrix

#### Vendor Purchase Order

| Permission | System Manager | Purchase Manager | Purchase User | Accounts User | Accounts Manager |
|---|:---:|:---:|:---:|:---:|:---:|
| Create | ✅ | ✅ | ✅ | ❌ | ❌ |
| Read | ✅ | ✅ | ✅ | ✅ | ✅ |
| Write | ✅ | ✅ | ✅ | ❌ | ❌ |
| Submit | ✅ | ✅ | ❌ | ❌ | ❌ |
| Cancel | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ | ❌ | ❌ |
| Export | ✅ | ✅ | ❌ | ❌ | ❌ |
| Print | ✅ | ✅ | ✅ | ❌ | ❌ |
| Report | ✅ | ✅ | ✅ | ❌ | ✅ |

**Key controls:**
- A **Purchase User** can create and draft a PO, but **cannot submit** it — a Purchase Manager or System Manager must review and submit.
- **Only System Manager can delete** a PO — prevents destruction of financial records.
- **Purchase Users cannot export** raw data — prevents bulk data extraction.
- **Accounts Users have read-only access** — they can view POs for accounting reconciliation but cannot modify them.

#### Vendor Payment

| Permission | System Manager | Accounts Manager | Accounts User |
|---|:---:|:---:|:---:|
| Create | ✅ | ✅ | ✅ |
| Read | ✅ | ✅ | ✅ |
| Write | ✅ | ✅ | ✅ |
| Submit | ✅ | ✅ | ❌ |
| Cancel | ✅ | ✅ | ❌ |
| Delete | ✅ | ✅ | ❌ |
| Export | ✅ | ✅ | ❌ |

**Key controls:**
- An **Accounts User** can create payment entries, but **cannot submit, cancel, or delete** them — only Accounts Manager or System Manager can.
- This creates a natural **maker-checker** workflow.

#### Equipment Master

| Permission | System Manager | Purchase User | Purchase Manager |
|---|:---:|:---:|:---:|
| Create | ✅ | ❌ | ❌ |
| Read | ✅ | ✅ | ✅ |
| Write | ✅ | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ |
| Report | ✅ | ✅ | ✅ |

**Key controls:**
- Only System Manager can add, modify, or delete equipment — prevents unauthorized catalog changes.
- Purchase Users can read equipment data (needed for PO creation) but cannot modify it.

### 4.3 API-Level Authorization

Our custom whitelisted API methods (`mark_advance_paid`, `mark_fully_paid`) perform **explicit role verification**:

```python
def _check_payment_role(self):
    allowed_roles = {"System Manager", "Accounts Manager", "Purchase Manager"}
    user_roles = set(frappe.get_roles(frappe.session.user))
    if not allowed_roles.intersection(user_roles):
        frappe.throw("You do not have permission...", frappe.PermissionError)
```

Even if someone discovers the API endpoint URL, they cannot invoke it without the correct role.

---

## 5. API & Endpoint Security

### 5.1 REST API Protection

Frappe exposes REST APIs at `/api/resource/<DocType>`. These are **always protected**:

- **Authentication required**: Every API call must include a valid session cookie or API key.
- **Permission enforcement**: The same RBAC rules from Section 4 apply to API calls — a user with `read` permission can GET but not POST/PUT.
- **Rate limiting**: Frappe limits API requests to prevent abuse.

### 5.2 No Raw SQL Exposure

Our application code **never uses raw SQL queries**. All database access goes through the Frappe ORM:

```python
# We use THIS (parameterized, safe):
frappe.get_doc("Supplier", supplier_name)
frappe.db.get_value("Company", company_name, ["default_currency"])

# We NEVER use this (vulnerable):
frappe.db.sql(f"SELECT * FROM tabSupplier WHERE name = '{user_input}'")
```

The ORM automatically uses **parameterized queries** which make SQL injection impossible.

### 5.3 Web Page Indexing Disabled

All our custom DocTypes have `index_web_pages_for_search: 0`, which means:
- Financial documents (POs, Payments) are **not indexed** for website search
- They cannot be discovered via the public-facing search functionality
- Only authenticated desk users with proper roles can access them

---

## 6. Input Validation & Data Integrity

### 6.1 Server-Side Validation (Cannot Be Bypassed)

All validation happens **server-side** in Python controllers. Even if someone bypasses the browser-side JavaScript, the server will reject invalid data.

#### Vendor Purchase Order Validation

| Check | What It Prevents |
|---|---|
| **Non-negative monetary values** | Negative rates, freight, or charges that could create fraudulent credits |
| **Quantity > 0** | Zero-quantity POs that have no business purpose |
| **Discount % between 0-100** | Discounts above 100% (which would result in negative amounts) |
| **Advance % between 0-100** | Invalid advance payment percentages |
| **Exchange rate > 0** | Zero exchange rates that would cause division errors |
| **Delivery date >= PO date** | Logically impossible delivery dates |
| **Grand total > 0 before submit** | Empty POs from being submitted |
| **XSS sanitization on text fields** | Script injection in remarks, payment terms, delivery locations |
| **Immutable fields after submit** | Vendor, Company, Equipment, Rate, Quantity, Grand Total cannot be changed after submission |

#### Vendor Payment Validation

| Check | What It Prevents |
|---|---|
| **Amount > 0** | Zero or negative payments |
| **Payment date <= today** | Future-dated payments |
| **Reference date <= payment date** | Reference dates that are logically impossible |
| **Mandatory UTR/reference before submit** | Submitting payments without a bank reference number |
| **Status transition enforcement** | Jumping directly from Draft to Paid (must go through approval) |

### 6.2 Document Immutability

Financial documents follow strict lifecycle rules:

```
Purchase Order:   Draft -> Submitted -> Vendor Confirmed -> Partially Paid -> Fully Paid -> Shipped -> Delivered
                                                                                                       |
                  Any status can go to -> Cancelled (but only by System Manager)
```

```
Vendor Payment:   Draft -> Pending Approval -> Approved -> Paid
                                                            |
                  Any status can go to -> Cancelled (but only by Accounts Manager+)
```

Once a document is **Submitted**, critical fields (vendor, company, equipment, amounts) are **locked**. To make changes, you must use the **Amend** workflow, which creates a new revision while preserving the original record — complete audit trail, no data loss.

### 6.3 Document Naming Integrity

All three DocTypes have **rename disabled** (`allow_rename: 0`):

- **PO numbers** (e.g., `SRI.PO.-.0001`) are legal document identifiers — they appear on invoices, shipping documents, and bank transfers. Renaming would create discrepancies with external parties.
- **Payment IDs** are referenced in bank statements and audit reports.
- **Equipment codes** (e.g., `EQ-00001`) are auto-generated and immutable — they serve as stable references across POs.

### 6.4 Bulk Edit Disabled

Bulk editing is **disabled** on all financial DocTypes. This prevents:
- Accidental mass-modification of payment records
- Unauthorized bulk changes to PO amounts
- Data corruption from poorly targeted bulk operations

---

## 7. Audit Trail & Change Tracking

### 7.1 Automatic Change Tracking

All three custom DocTypes have `track_changes: 1` enabled. This means **every single change** to any field is automatically logged:

- **Who** made the change (username)
- **When** the change was made (timestamp)
- **What** was changed (old value -> new value)
- **Which field** was modified

This audit log is visible in the document sidebar under "Activity" and **cannot be deleted** by any user, including System Manager.

### 7.2 Built-in Metadata on Every Row

Frappe automatically maintains four metadata columns on every database record:

| Column | Purpose |
|---|---|
| `owner` | The user who created the record |
| `creation` | Exact timestamp of record creation |
| `modified_by` | The user who last modified the record |
| `modified` | Exact timestamp of last modification |

These are set by the framework and **cannot be spoofed** by the user.

### 7.3 Comment-Based Audit Trail

Critical actions (payment status changes, submission, cancellation) automatically create **system comments** on the document:

```
"Advance payment marked by john@sarveksha.com" -- 2026-07-27 15:30:45
"Marked as Fully Paid by admin@sarveksha.com" -- 2026-07-28 10:00:12
"Payment cancelled by admin@sarveksha.com" -- 2026-07-29 09:15:00
```

### 7.4 View Tracking

The Vendor Payment DocType has `track_seen: 1` enabled, which records **which users have viewed** each payment record. This is useful for compliance — you can verify that the approver actually reviewed the payment before approving it.

---

## 8. Code-Level Security (How Git Protects Our Configs)

### 8.1 Repository Security

- The GitHub repository is **private** — only authorized team members can access the code.
- All code changes go through **Pull Requests** — no one can push directly to the main branch without review.
- Git maintains a **complete, immutable history** of every change ever made to every file.

### 8.2 What Git Tracks

| What | Tracked in Git? | Why |
|---|---|---|
| DocType schemas (JSON) | Yes | Defines database structure — must be version-controlled |
| Python controllers | Yes | Business logic and validation rules |
| JavaScript (client scripts) | Yes | UI behavior and calculation logic |
| Print formats (HTML) | Yes | PO document templates |
| Fixture data (seed data) | Yes | Companies, Vendors, Equipment catalog |
| Workspace/sidebar configs | Yes | Navigation structure |
| Live transactional data | No | POs, Payments exist only in the database |
| User passwords | No | Stored only in MariaDB as bcrypt hashes |
| Database dumps | No | Blocked by `.gitignore` |
| Environment secrets | No | Blocked by `.gitignore` |
| Log files | No | Blocked by `.gitignore` |

### 8.3 .gitignore Protection

Our `.gitignore` is hardened to prevent accidental commit of:

- `.env` / environment variable files (API keys, database passwords)
- `*.sql` / `*.sql.gz` (database dumps)
- `*.log` (application logs that may contain sensitive data)
- `*.bak` / `*.tmp` (temporary files)
- `node_modules/` (dependency code)

---

## 9. Sensitive Data Handling

### 9.1 What Sensitive Data Exists

| Data Type | Where It Lives | Protection |
|---|---|---|
| Vendor bank account numbers | MariaDB `tabSupplier` + Git fixtures | RBAC (only authorized roles can view Supplier records) |
| Vendor GSTIN / PAN | MariaDB `tabSupplier` + Git fixtures | RBAC + Private repository |
| Company registration numbers | MariaDB `tabCompany` + Git fixtures | RBAC + Private repository |
| IEC Code (AFTFS2557J) | MariaDB `tabCompany` | RBAC |
| User passwords | MariaDB (bcrypt hashed) | Hashing — irreversible |
| Session tokens | Redis (in-memory) | Auto-expiry, server-side only |

### 9.2 Fixture Data Tradeoff

The vendor and company fixture files contain real registration data (GSTIN, PAN, bank details). This is a deliberate architectural choice:

- **Why it's there**: Frappe's fixture system is the official mechanism for sharing master data across team members. Without fixtures, each developer would need to manually re-enter all 22 vendors, 9 companies, and 3,000+ equipment records.
- **How it's protected**: The GitHub repository is **private** — only authorized team members have access. The repository has no public forks.
- **Production mitigation**: In production, fixtures are only imported once during initial setup. After that, all data changes happen through the UI with full RBAC enforcement.

### 9.3 Bank Account Fields

The `statement_password` field in bank account fixtures is always `null` — we never store bank statement download passwords in the codebase.

---

## 10. Production Deployment Security

When deploying to production (beyond the current dev container), the following security stack is used:

### 10.1 Network Layer

| Component | Purpose |
|---|---|
| **NGINX** | Reverse proxy — terminates HTTPS/TLS, serves static files, blocks direct database access |
| **Let's Encrypt SSL** | Free, auto-renewing TLS certificates — all traffic encrypted in transit |
| **Firewall (ufw/iptables)** | Only ports 80 (redirects to 443) and 443 (HTTPS) are open — MariaDB port 3306 is blocked from external access |

### 10.2 Application Layer

| Component | Purpose |
|---|---|
| **Gunicorn** | Production-grade WSGI server — handles concurrent requests securely |
| **Supervisor** | Process manager — auto-restarts crashed workers |
| **Redis** | Session store and job queue — not exposed to the network |
| **MariaDB** | Listens only on `127.0.0.1` (localhost) — no external database access possible |

### 10.3 Deployment Security Checklist

- [ ] HTTPS enforced on all endpoints
- [ ] MariaDB bound to localhost only (`bind-address = 127.0.0.1`)
- [ ] Redis bound to localhost only
- [ ] Firewall rules: only 80/443 open
- [ ] Default Frappe administrator password changed
- [ ] Guest access disabled
- [ ] Maintenance mode during updates
- [ ] Regular database backups (`bench backup --with-files`)
- [ ] Backups stored on separate server/cloud (not on the same machine)
- [ ] Log rotation configured to prevent disk exhaustion

---

## 11. Security Measures Summary Table

| # | Security Measure | Type | Status |
|---|---|---|---|
| 1 | Bcrypt password hashing | Authentication | Built-in (Frappe) |
| 2 | CSRF token protection | Request Security | Built-in (Frappe) |
| 3 | Session-based auth with server-side tokens | Session Security | Built-in (Frappe) |
| 4 | SQL injection prevention (ORM) | Data Security | Built-in (Frappe) |
| 5 | Role-Based Access Control (RBAC) | Authorization | Configured per DocType |
| 6 | Financial document rename disabled | Data Integrity | Implemented |
| 7 | Bulk edit disabled on financial docs | Data Integrity | Implemented |
| 8 | Full audit trail (track_changes) | Compliance | Implemented |
| 9 | View tracking on payments (track_seen) | Compliance | Implemented |
| 10 | Negative value rejection | Input Validation | Implemented |
| 11 | XSS sanitization on text fields | Input Validation | Implemented |
| 12 | Immutable fields after PO submission | Data Integrity | Implemented |
| 13 | Status transition enforcement (Payments) | Workflow Security | Implemented |
| 14 | Role-checked payment API methods | API Security | Implemented |
| 15 | Audit comments on critical actions | Compliance | Implemented |
| 16 | Mandatory UTR before payment submission | Financial Control | Implemented |
| 17 | Web page indexing disabled | Data Privacy | Implemented |
| 18 | Private GitHub repository | Code Security | Active |
| 19 | .gitignore hardened | Secret Protection | Implemented |
| 20 | Maker-checker workflow (Purchase User can't submit) | Segregation of Duties | Implemented |

---

## 12. How to Demonstrate Security to Management

Use the following live demonstrations during your meeting:

### Demo 1: Show the Audit Trail
1. Open any Vendor Purchase Order.
2. Change a field (e.g., payment terms) and save.
3. In the right sidebar, click **Activity** — Show the change log: old value, new value, who changed it, when.
4. **Talking point:** _"Every single change to every document is permanently recorded. Even System Manager cannot delete this log."_

### Demo 2: Show Permission Enforcement
1. Log in as a **Purchase User** (not admin).
2. Try to delete a PO — **Error: Permission denied.**
3. Try to submit a PO — **Error: Permission denied.** (Only Purchase Manager can submit.)
4. **Talking point:** _"We enforce segregation of duties — the person who creates a PO cannot submit it. This is a standard financial control used in banking."_

### Demo 3: Show Input Validation
1. Open a new Vendor Purchase Order.
2. Enter a **negative rate** (e.g., -5000) — **Error: Unit Rate cannot be negative.**
3. Enter a **discount of 150%** — **Error: Discount % must be between 0 and 100.**
4. Enter **quantity 0** — **Error: Quantity must be greater than zero.**
5. **Talking point:** _"All validation happens server-side. Even if someone bypasses the browser, the server will reject invalid data."_

### Demo 4: Show Immutable Fields After Submission
1. Submit a PO (as Purchase Manager).
2. Click **Menu > Amend** to show the proper amendment workflow.
3. **Talking point:** _"Once a PO is submitted, the vendor, company, equipment, and amounts are locked. The only way to change them is to formally amend the document — which creates a new version while preserving the original. This maintains a complete paper trail."_

### Demo 5: Show Data in the Database (Ultimate Proof)
1. Open terminal and run `bench --site development.localhost mariadb`
2. Run: `SELECT name, owner, creation, modified, modified_by FROM \`tabVendor Purchase Order\` LIMIT 5;`
3. Show the automatic metadata columns.
4. **Talking point:** _"Every record in the database automatically tracks who created it, who last modified it, and when. This is enforced at the framework level — our code cannot bypass it."_

### Demo 6: Show Password Security
1. In the MariaDB console, run: `SELECT name, password FROM __Auth LIMIT 3;`
2. Show that passwords are stored as `$2b$12$...` hashes.
3. **Talking point:** _"We use bcrypt hashing — even if someone gains access to the database server, they cannot extract user passwords. This is the same algorithm used by banks and government systems."_

### Demo 7: Show the Rename Block
1. Open a Purchase Order.
2. Try **Menu > Rename** — Show the error or that the option is not available.
3. **Talking point:** _"PO numbers are legal identifiers that appear on invoices and shipping documents. We've locked them so they can never be changed — this prevents fraud and maintains document integrity across systems."_

---

> _This document should be treated as confidential and shared only with authorized Sarveksha management personnel._
