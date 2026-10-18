# 🚀 Swarajya Staging Automation Master Framework

Production-grade, end-to-end test automation framework powered by **Playwright (Python)** and **Pytest** for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/).

Built with a **modular Page Object Model (POM)**, a **centralized shared architecture**, a **single source of truth for test data**, and **strict zero hardcoded values** across all functional areas.

---

## 👥 Team Module Ownership & Division of Responsibilities

| Contributor / Scope | Modules Covered | Dedicated Branches (Click to View) | Target Sheets in `shared/test_data/` |
| :--- | :--- | :--- | :--- |
| **Himanshu** | • **Core Shared Framework** & Excel Engine<br>• **Login Suite** (Employee & Manager)<br>• **Create Employee** Module<br>• **Create Vendor** Module<br>• **Create Customer** Module<br>• **Create Invoice** Module<br>• **Update Purchase Order** Module | [`shared`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/shared)<br>[`login/emp-manager`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/emp-manager)<br>[`create/emp-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/emp-mgmt)<br>[`create/customer-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/customer-mgmt)<br>[`create/vendor-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/vendor-mgmt)<br>[`create/invoice-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/invoice-mgmt)<br>[`update/purchase-orders`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/purchase-orders) | • `loginhr_admin`<br>• `loginemp-manager`<br>• `createemp-mgmt`<br>• `createvendor-mgmt`<br>• `createcutomer-mgmt`<br>• `createinvoice-mgmt`<br>• `updatepurchase-order` |
| **Mrugank** | • **HR / Admin Login** Suite<br>• **Create Consultant** Module<br>• **Create Purchase Order** Module<br>• **Update Employee** Module<br>• **Update Customer** Module<br>• **Update Invoice** Module | [`login/hr_admin`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/hr_admin)<br>[`create/consultant_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/consultant_mgmt)<br>[`create/purchase_order`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/purchase_order)<br>[`update/emp_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/emp_mgmt)<br>[`update/customer_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/customer_mgmt)<br>[`update/invoice_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/invoice_mgmt) | • `loginhr_admin`<br>• `createconsultant_mgmt`<br>• `createpurchase_order`<br>• `updateemp_mgmt`<br>• `updatecustomer_mgmt`<br>• `updateinvoice-mgmt` |

---

## 🏗️ Unified Master Architecture

The repository adheres to a strict **zero-redundancy** and **zero-hardcoding** layout. All shared page objects, utilities, configuration constants, and test data workbooks reside centrally in the `shared/` package. Individual module branches contain strictly their automation scripts and page objects — **no local `test_data/` folders or duplicate `.xlsx` files**.

```
swarajya-stg-automation/
│
├── shared/                             # 🌐 Centralized Core Framework & Test Data
│   ├── config/                         # Central configuration
│   │   └── constants.py                # Single source of truth (Selectors, dynamic auth defaults)
│   ├── pages/                          # Reusable Page Objects
│   │   ├── base_page.py                # Base page with robust synchronization & error handlers
│   │   ├── login_page.py               # Shared login & 2FA page object
│   │   └── auth_setup_page.py          # Session bootstrap utility
│   ├── reporter/                       # Custom test reporting
│   │   ├── html_reporter.py            # Standalone HTML summary generator
│   │   └── pytest_html_reporter.py     # Session report generator
│   ├── utils/                          # Framework utilities
│   │   ├── paths.py                    # Multi-environment central path resolver
│   │   ├── excel_base.py               # Core Excel sheet parsing & Base URL discovery
│   │   ├── excel_loader.py             # Bi-directional Excel provider & result logger
│   │   ├── logger.py                   # Centralized thread-safe logger
│   │   └── popup.py                    # Desktop execution summary dialog
│   └── test_data/                      # 📊 SINGLE SOURCE OF TRUTH (Universal Workbooks)
│       ├── Swarajya-test-cases.xlsx    # Master test definitions & bi-directional write-back
│       ├── Swarajya-test-data.xlsx     # Data-driven test inputs & dynamic credentials
│       ├── sample_po.pdf               # Mock attachment for document upload tests
│       └── auth_state_*.json           # Cached session tokens (gitignored)
│
├── swarajya-login/                     # 🔐 Authentication Suites
│   ├── emp-manager/                    # 👥 Employee & Manager Login Suite (22 Tests)
│   │   ├── pages/                      # Page Objects & TFA Handlers
│   │   └── tests/                      # UI, 2FA, Negative Creds, SQLi/XSS Flows
│   └── hr_admin/                       # 🛡️ HR & Admin Authentication Suite (14 Tests)
│       ├── pages/                      # Page Objects & TFA Handlers
│       └── tests/                      # Login & 2FA Test Flows
│
├── swarajya-create/                    # 📋 Master Create Operations Suite
│   ├── employee-management/            # 👤 Create Employee Module (27 Tests)
│   │   ├── emp_pages/                  # Page Objects & Form Executor
│   │   ├── emp_utils/                  # Excel Reader & Utilities
│   │   └── tests/                      # Positive & Negative Test Suites
│   ├── vendor-management/              # 🏢 Create Vendor Module (31 Tests)
│   │   ├── vendor_pages/               # Page Objects & Form Executor
│   │   ├── vendor_utils/               # Excel Reader & Utilities
│   │   └── tests/                      # Positive & Negative Test Suites
│   ├── customer-management/            # 👥 Create Customer Module (36 Tests)
│   │   ├── customer_pages/             # Page Objects & Form Executor
│   │   ├── customer_utils/             # Excel Reader & Utilities
│   │   └── tests/                      # Positive & Negative Test Suites
│   ├── invoice-management/             # 🧾 Create Invoice Module (27 Tests)
│   │   ├── invoice_pages/              # Page Objects & Form Executor
│   │   ├── invoice_utils/              # Excel Reader & Utilities
│   │   └── tests/                      # Positive & Negative Test Suites
│   ├── consultant-management/          # 💼 Create Consultant Module (47 Tests)
│   │   ├── consultant_pages/           # Page Objects & Form Executor
│   │   ├── consultant_utils/           # Excel Reader & Utilities
│   │   └── tests/                      # Positive & Negative Test Suites
│   └── purchase-order/                 # 📦 Create Purchase Order Module (33 Tests)
│       ├── po_pages/                   # Page Objects & Form Executor
│       ├── po_utils/                   # Excel Reader & Utilities
│       └── tests/                      # Positive & Negative Test Suites
│
├── swarajya-update/                    # 🔄 Master Update Operations Suite
│   ├── purchase-orders/                # 📑 Update Purchase Order Module (31 Tests)
│   │   ├── po_update_pages/            # Page Objects & Form Executor
│   │   ├── po_update_utils/            # Excel Reader & Utilities
│   │   └── tests/                      # Positive & Negative Test Suites
│   ├── employee-management/            # 📝 Update Employee Module (29 Tests)
│   │   ├── emp_update_pages/           # Page Objects & Form Executor
│   │   ├── emp_update_utils/           # Excel Reader & Utilities
│   │   └── tests/                      # Positive & Negative Test Suites
│   ├── customer-management/            # 👥 Update Customer Module (49 Tests)
│   │   ├── customer_update_pages/      # Page Objects & Form Executor
│   │   ├── customer_update_utils/      # Excel Reader & Utilities
│   │   └── tests/                      # Positive & Negative Test Suites
│   └── invoice-management/             # 🧾 Update Invoice Module
│       ├── invoice_update_pages/       # Page Objects & Form Executor
│       ├── invoice_update_utils/       # Excel Reader & Utilities
│       └── tests/                      # Positive & Negative Test Suites
│
├── pytest.ini                          # Root Pytest Configuration & Unified Markers
└── README.md                           # Master Architecture Documentation
```

---

## 📊 Comprehensive Test Coverage Matrix

All modules dynamically load test definitions and input data from `shared/test_data/` workbooks:

| Category | Sub-Module | Ownership | Reference Sheet (`Swarajya-test-cases.xlsx`) | Input Sheet (`Swarajya-test-data.xlsx`) | Tests Collected | Execution Mode |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **Authentication** | Employee & Manager Login | **Himanshu** | `loginemp-manager` | `loginemp-manager` | **22** | Automated |
| **Authentication** | HR & Admin Login | **Mrugank** | `loginhr_admin` | `loginhr_admin` | **14** | Automated |
| **Create Operations** | Employee Management | **Himanshu** | `createemp-mgmt` | `createemp-mgmt` | **27** | Automated |
| **Create Operations** | Vendor Management | **Himanshu** | `createvendor-mgmt` | `createvendor-mgmt` | **31** | Automated |
| **Create Operations** | Customer Management | **Himanshu** | `createcutomer-mgmt` | `createcustomer-mgmt` | **36** | Automated |
| **Create Operations** | Invoice Management | **Himanshu** | `createinvoice-mgmt` | `createinvoice-mgmt` | **27** | Automated |
| **Create Operations** | Consultant Management | **Mrugank** | `createconsultant_mgmt` | `createconsultant_mgmt` | **47** | Automated |
| **Create Operations** | Purchase Order Creation | **Mrugank** | `createpurchase_order` | `createpurchase_order` | **33** | Automated |
| **Update Operations** | Purchase Order Updates | **Himanshu** | `updatepurchase-order` | `updatepurchase-order` | **31** | Automated |
| **Update Operations** | Employee Updates | **Mrugank** | `updateemp_mgmt` | `updateemp_mgmt` | **29** | Automated |
| **Update Operations** | Customer Updates | **Mrugank** | `updatecustomer_mgmt` | `updatecustomer_mgmt` | **49** | Automated |
| **Update Operations** | Invoice Updates | **Mrugank** | `updateinvoice-mgmt` | `updateinvoice-mgmt` | — | Automated |

---

## ⚙️ CI/CD Pipeline & Zero Hardcoded Configuration

The framework enforces a strict **Zero Hardcoded Values** policy. All environments, credentials, endpoints, and run flags are dynamically discovered and can be seamlessly overridden via CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI).

### Dynamic Resolution Hierarchy

```
1. CI/CD Environment Variables (Highest Priority)
        ↓ (if not set)
2. Central Test Data Excel Sheets (`shared/test_data/Swarajya-test-data.xlsx`)
        ↓ (if not present)
3. Dynamic In-Memory Generation (Timestamps, unique UUID suffixes)
```

### Supported CI/CD Environment Variables

| Variable Name | Description | Example / Default |
| :--- | :--- | :--- |
| `SWARAJYA_BASE_URL` or `BASE_URL` | Target environment Base URL | `https://swarajya-stg.corecotechnologies.com` |
| `SWARAJYA_EMPLOYEE_ID` or `EMPLOYEE_ID` | Master Employee/Admin Login ID | Fetched dynamically from Excel banner/sheet |
| `SWARAJYA_PASSWORD` or `PASSWORD` | Master Login Password | Fetched dynamically from Excel banner/sheet |
| `SWARAJYA_AUTH_CODE` or `AUTH_CODE` | Master 2FA Authentication Code | Fetched dynamically from Excel or env |
| `ADMIN_EMPLOYEE_ID` / `ADMIN_PASSWORD` | Role-specific Admin Credentials | `admin` |
| `MANAGER_EMPLOYEE_ID` / `MANAGER_PASSWORD` | Role-specific Manager Credentials | Fetched from `loginemp-manager` sheet |
| `HEADLESS` / `CI` | Run browser in headless mode (`true`/`false`) | `true` in CI pipelines |

---

## ⚡ Core Engineering & Architecture Highlights

1. **Zero Redundant Test Data**:
   - `shared/test_data/Swarajya-test-cases.xlsx` and `shared/test_data/Swarajya-test-data.xlsx` serve as the universal single source of truth.
   - Module branches contain zero `.xlsx` files, ensuring clean Git diffs and preventing merge conflicts.
2. **Dynamic Bi-Directional Result Logging**:
   - Automatic execution status updates (`Passed`, `Failed`, `Skipped`), standardized `AUT_*` automation IDs, execution durations, and timestamps are written directly back to `Swarajya-test-cases.xlsx` in real-time.
3. **Smart Session Reuse (`auth_state_*.json`)**:
   - Centralized authentication caching via `shared.utils.paths.AUTH_STATE_FILE` prevents repetitive logins across test cases and avoids session collision between staging and production environments.
4. **100% Dynamic Synchronization (Zero Arbitrary Sleeps)**:
   - Event-driven Playwright assertions (`wait_for(state="visible")`, `wait_for_dom_ready()`, `wait_for_url()`).
5. **1-to-1 Screenshot Audit & Auto-Retention**:
   - Captures exactly 1 screenshot per test case (`{STATUS}_{TC_ID}__{TIMESTAMP}.png`).
   - Automatically purges screenshots older than 24 hours.
6. **Desktop Summary Dialogs & Standalone HTML Reports**:
   - Instant Tkinter popup summary displaying execution metrics (Total, Passed, Failed, Duration) at the end of each session.
   - Standalone HTML reports generated per module run.

---

## 🔀 Branch Management & Conflict-Free PR Strategy

To guarantee **zero merge conflicts** during team collaboration:
1. Every contributor works on their designated isolated branch.
2. Changes to shared core files (`shared/`) are pushed to `origin/shared` and merged to `main` first via Pull Request.
3. Each module branch re-syncs with latest `main` before raising a Pull Request.
4. Binary Excel files reside exclusively in `shared/test_data/`, eliminating binary merge conflicts.

---

## 🚀 Quick Execution Commands

### 👤 Himanshu's Modules

#### 1. Login Suite (Employee & Manager)
```powershell
cd swarajya-login\emp-manager
pytest
```

#### 2. Create Employee Management
```powershell
cd swarajya-create\employee-management
pytest
```

#### 3. Create Vendor Management
```powershell
cd swarajya-create\vendor-management
pytest
```

#### 4. Create Customer Management
```powershell
cd swarajya-create\customer-management
pytest
```

#### 5. Create Invoice Management
```powershell
cd swarajya-create\invoice-management
pytest
```

#### 6. Update Purchase Order Management
```powershell
cd swarajya-update\purchase-orders
pytest
```

---

### 👤 Mrugank's Modules

#### 1. HR / Admin Login Suite
```powershell
cd swarajya-login\hr_admin
pytest
```

#### 2. Create Consultant Management
```powershell
cd swarajya-create\consultant-management
pytest
```

#### 3. Create Purchase Order Management
```powershell
cd swarajya-create\purchase-order
pytest
```

#### 4. Update Employee Management
```powershell
cd swarajya-update\employee-management
pytest
```

#### 5. Update Customer Management
```powershell
cd swarajya-update\customer-management
pytest
```

#### 6. Update Invoice Management
```powershell
cd swarajya-update\invoice-management
pytest
```

---

### 🌐 Full Suite Runs

```powershell
# Run all Create operations (Employee, Vendor, Consultant, Customer, PO, Invoice)
pytest swarajya-create

# Run all Update operations (Customer, Employee, Purchase Orders, Invoice)
pytest swarajya-update

# Run all Login verification suites
pytest swarajya-login

# Run all tests across the entire repository
pytest
```
