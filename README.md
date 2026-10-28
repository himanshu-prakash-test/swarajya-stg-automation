# 🚀 Swarajya Staging Automation Framework

An enterprise-grade, data-driven end-to-end test automation framework for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), engineered with **Python 3.12+**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 👥 Branch Distribution & Module Ownership Matrix

This repository follows a strict **Isolated Branch Architecture** to guarantee zero merge conflicts and seamless parallel collaboration. All modules are distributed between **Himanshu** and **Mrugank**, with shared infrastructure maintained centrally in `shared/`.

### 📌 Master Branch Distribution Table

| Contributor | Operation Category | Sub-Module | Isolated Branch (Click to View) | Target Directory Path | Test Cases Sheet | Input Data Sheet | Tests | Status on `main` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **Himanshu** | 🔐 Authentication | Employee & Manager Login | [`login/emp-manager`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/emp-manager) | `swarajya-login/emp-manager` | `loginemp-manager` | `loginemp-manager` | **22** | ✅ Merged |
| **Himanshu** | 📋 Create Operations | Employee Management | [`create/emp-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/emp-mgmt) | `swarajya-create/employee-management` | `createemp-mgmt` | `createemp-mgmt` | **25** | ✅ Merged |
| **Himanshu** | 📋 Create Operations | Vendor Management | [`create/vendor-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/vendor-mgmt) | `swarajya-create/vendor-management` | `createvendor-mgmt` | `createvendor-mgmt` | **29** | ✅ Merged |
| **Himanshu** | 📋 Create Operations | Customer Management | [`create/customer-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/customer-mgmt) | `swarajya-create/customer-management` | `createcutomer-mgmt` | `createcustomer-mgmt` | **34** | ✅ Merged |
| **Himanshu** | 📋 Create Operations | Invoice Management | [`create/invoice-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/invoice-mgmt) | `swarajya-create/invoice-management` | `createinvoice-mgmt` | `createinvoice-mgmt` | **27** | ✅ Merged |
| **Himanshu** | 🔄 Update Operations | Purchase Order Updates | [`update/purchase-order`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/purchase-order) | `swarajya-update/purchase-orders` | `updatepurchase-order` | `updatepurchase-order` | **31** | ✅ Merged |
| **Mrugank** | 🔐 Authentication | HR & Admin Login | [`login/hr_admin`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/hr_admin) | `swarajya-login/hr_admin` | `loginhr_admin` | `loginhr_admin` | **39** | 🌿 Isolated Branch |
| **Mrugank** | 📋 Create Operations | Consultant Management | [`create/consultant_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/consultant_mgmt) | `swarajya-create/consultant-management` | `createconsultant_mgmt` | `createconsultant_mgmt` | **47** | 🌿 Isolated Branch |
| **Mrugank** | 📋 Create Operations | Purchase Order Creation | [`create/purchase_order`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/purchase_order) | `swarajya-create/purchase-order` | `createpurchase_order` | `createpurchase_order` | **33** | 🌿 Isolated Branch |
| **Mrugank** | 🔄 Update Operations | Employee Updates | [`update/emp_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/emp_mgmt) | `swarajya-update/employee-management` | `updateemp_mgmt` | `updateemp_mgmt` | **31** | ✅ Merged |
| **Mrugank** | 🔄 Update Operations | Customer Updates | [`update/customer_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/customer_mgmt) | `swarajya-update/customer-management` | `updatecustomer_mgmt` | `updatecustomer_mgmt` | **51** | ✅ Merged |
| **Mrugank** | 🔄 Update Operations | Invoice Updates | [`update/invoice_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/invoice_mgmt) | `swarajya-update/invoice-management` | `updateinvoice_mgmt` | `updateinvoice_mgmt` | **32** | ✅ Merged |
| **Collaborative** | 🌐 Core Framework | Shared Infrastructure | [`shared`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/shared) | `shared/` | *Universal Base* | *Universal Base* | **Core** | ✅ Integrated |
| **Collaborative** | 🚀 Production / Master | Integrated Suite | [`main`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/main) | *Root* | *All Sheets (12)* | *All Sheets (12)* | **390+** | 🚀 Production |

---

### 👤 Himanshu's Modules & Branch Responsibilities

Himanshu owns the core framework architecture, employee/manager authentication, full creation lifecycle for Employees, Vendors, Customers, and Invoices, as well as the Purchase Order update suite.

| Branch | Module Scope | Key Automated Scenarios & Highlights | Test Count | Status |
| :--- | :--- | :--- | :---: | :---: |
| [`login/emp-manager`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/emp-manager) | **Employee & Manager Authentication** | • Dual-role login flows (Employee, Manager)<br>• 2FA verification & session persistence<br>• Negative error states, locked accounts & role RBAC checks | **22** | Merged |
| [`create/emp-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/emp-mgmt) | **Create Employee Management** | • Multi-tab onboarding form automation<br>• Datepicker selection & department dropdowns<br>• Validation assertions, duplicate email/ID handling & Excel writeback | **25** | Merged |
| [`create/vendor-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/vendor-mgmt) | **Create Vendor Management** | • Full vendor profile creation & PAN/GST validation<br>• 10-digit phone regex and mandatory field checks<br>• Confirmation popup handling & post-creation grid search | **29** | Merged |
| [`create/customer-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/customer-mgmt) | **Create Customer Management** | • 20+ field onboarding with currency/tax/terms matrices<br>• IGST toggle switch & dynamic address parsing<br>• Modal dialog handling (Yes/No dismissal) & route verification | **34** | Merged |
| [`create/invoice-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/invoice-mgmt) | **Create Invoice Management** | • Complete invoice creation workflow with customer binding<br>• Line items calculation, tax breakdown & total tallying<br>• Form mount wait guards & cached authentication state | **27** | Merged |
| [`update/purchase-order`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/purchase-order) | **Update Purchase Orders** | • Purchase Order search, edit & status modification<br>• Line item adjustments, audit tracking & remarks<br>• Defect tracking with `wasxfail` integration and 1-to-1 screenshot audit | **31** | Merged |

---

### 👤 Mrugank's Modules & Branch Responsibilities

Mrugank owns HR & Admin authentication, consultant onboarding, purchase order creation, and update workflows for Employees, Customers, and Invoices.

| Branch | Module Scope | Key Automated Scenarios & Highlights | Test Count | Status |
| :--- | :--- | :--- | :---: | :---: |
| [`login/hr_admin`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/hr_admin) | **HR & Admin Authentication** | • HR & Super-Admin login credentials & 2FA<br>• Password recovery, invalid credentials & boundary test cases<br>• Dynamic wait optimizations & role-specific dashboard routing | **39** | Merged |
| [`create/consultant_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/consultant_mgmt) | **Create Consultant Management** | • Complete consultant profile creation & contract period assignment<br>• Hourly/monthly rate validations & bank account binding<br>• Modal confirmation handling & grid search verification | **47** | merged |
| [`create/purchase_order`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/purchase_order) | **Create Purchase Order** | • End-to-end PO creation linked to customer profiles<br>• Base, tax, and total amount calculation checks<br>• `sample_po.pdf` document upload automation & submission verification | **33** | Merged |
| [`update/emp_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/emp_mgmt) | **Update Employee Management** | • Existing employee record search & profile field modification<br>• Role, department, and salary update assertions<br>• Confirmation popup verification and audit logging | **31** | Merged |
| [`update/customer_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/customer_mgmt) | **Update Customer Management** | • Customer detail updates (billing address, contact, GST)<br>• Active/Inactive state toggling & credit limit revisions<br>• Offline network simulation & negative validation handling | **51** | Merged |
| [`update/invoice_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/invoice_mgmt) | **Update Invoice Management** | • Invoice editing, item additions/removals, and recalculations<br>• Status transitions (Draft → Approved → Sent → Paid)<br>• Data-driven automation mirroring invoice management standards | **32** | Merged |

---

## 🏛️ Comprehensive Framework Architecture

The framework is architected according to strict **Layered Separation of Concerns**, ensuring high modularity, maximum code reusability, and clean separation between test definitions, business page logic, and data infrastructure.

```
swarajya-stg-automation/
│
├── .github/                                 # 🤖 CI/CD Orchestration Layer
│   └── workflows/
│       └── ci.yml                          # Multi-stage GitHub Actions CI/CD matrix pipeline
│
├── shared/                                 # 🌐 Centralized Core Framework & Infrastructure
│   ├── config/                             # Global configuration, timeouts & constant definitions
│   │   ├── constants.py                    # Universal timeouts, URLs, standard roles, and regex patterns
│   │   └── __init__.py
│   │
│   ├── pages/                              # Core Page Object Model (POM) foundation
│   │   ├── base_page.py                    # Base Playwright actions, dynamic waits, dropdown selectors, screenshot hooks
│   │   ├── login_page.py                   # Centralized authentication page object with credential injection
│   │   ├── auth_setup_page.py              # Authenticated session generator and storage state exporter
│   │   ├── tfa_page.py                     # Two-Factor Authentication (2FA) verification page object
│   │   └── __init__.py
│   │
│   ├── reporter/                           # Custom reporting engine & visualization
│   │   ├── html_reporter.py                # Standalone HTML report generator with embedded analytics
│   │   ├── template.py                     # Modern responsive HTML5/CSS3 template definitions
│   │   ├── models.py                       # Data models for test case execution, timings, and status
│   │   ├── hooks.py                        # Pytest execution hooks (`pytest_runtest_makereport`)
│   │   ├── assets/
│   │   │   └── coreco_logo.png             # Corporate logo embedded in HTML reports
│   │   └── __init__.py
│   │
│   ├── test_data/                          # Universal Single Source of Truth (Zero Duplication)
│   │   ├── Swarajya-test-cases.xlsx        # Master test cases workbook (12 sheets, statuses, run history)
│   │   ├── Swarajya-test-data.xlsx         # Master test data repository (12 sheets, input payloads, credentials)
│   │   ├── sample_po.pdf                   # Standard PDF artifact for Purchase Order file upload tests
│   │   └── auth_state_swarajya-stg_corecotechnologies_com.json # Cached browser session state
│   │
│   └── utils/                              # Universal helper utilities & common services
│       ├── excel_base.py                   # Base workbook loader & bi-directional execution result writer
│       ├── excel_loader.py                 # High-performance OpenPyXL dynamic loader & cell parser
│       ├── logger.py                       # Unified console and rotating file logger with timestamps
│       ├── paths.py                        # Cross-platform path resolver for root, data, reports, and screenshots
│       ├── popup.py                        # Desktop execution summary popup modal (Tkinter)
│       └── __init__.py
│
├── swarajya-create/                        # 📋 Master Create Operations Suite
│   ├── customer-management/                # 👥 Customer Onboarding Module (Himanshu)
│   │   ├── customer_pages/                 # BasePage, LoginPage, CustomerPage, FormExecutor
│   │   ├── customer_utils/                 # Excel Reader, Logger, Popup integrations
│   │   ├── tests/                          # Positive, Negative & Login customer creation suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   └── README.md                       # Customer module documentation
│   │
│   ├── employee-management/                # 👤 Employee Onboarding Module (Himanshu)
│   │   ├── emp_pages/                      # BasePage, LoginPage, EmployeePage, FormExecutor
│   │   ├── emp_utils/                      # Excel Reader, Logger, Popup integrations
│   │   ├── tests/                          # Positive, Negative & Login employee creation suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   └── README.md                       # Employee module documentation
│   │
│   ├── invoice-management/                 # 🧾 Invoice Creation Module (Himanshu)
│   │   ├── invoice_pages/                  # BasePage, LoginPage, InvoicePage, FormExecutor
│   │   ├── invoice_utils/                  # Excel Reader, Logger, Calculation helpers
│   │   ├── tests/                          # Positive, Negative & Login invoice creation suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   └── README.md                       # Invoice module documentation
│   │
│   ├── vendor-management/                  # 🏢 Vendor Onboarding Module (Himanshu)
│   │   ├── vendor_pages/                   # BasePage, LoginPage, VendorPage, FormExecutor
│   │   ├── vendor_utils/                   # Excel Reader, Logger, Popup integrations
│   │   ├── tests/                          # Positive, Negative & Login vendor creation suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   └── README.md                       # Vendor module documentation
│   │
│   ├── consultant-management/              # 💼 Consultant Profile Creation Module (Mrugank)
│   │   ├── consultant_pages/               # BasePage, LoginPage, ConsultantPage, FormExecutor
│   │   ├── consultant_utils/               # Excel Reader, Logger, Popup integrations
│   │   ├── tests/                          # Positive & Negative consultant creation suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   └── README.md                       # Consultant module documentation
│   │
│   ├── purchase-order/                     # 📦 Purchase Order Creation Module (Mrugank)
│   │   ├── po_pages/                       # BasePage, LoginPage, POPage, FormExecutor
│   │   ├── po_utils/                       # Excel Reader, PDF file upload helper
│   │   ├── tests/                          # Positive & Negative PO creation suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   └── README.md                       # PO creation module documentation
│   │
│   ├── pytest.ini                          # Root Create operations pytest configuration
│   └── README.md                           # Create operations overview & guidelines
│
├── swarajya-update/                        # 🔄 Master Update Operations Suite
│   ├── purchase-orders/                    # 📑 Purchase Order Modification Module (Himanshu)
│   │   ├── po_update_pages/                # BasePage, LoginPage, POUpdatePage, FormExecutor
│   │   ├── po_update_utils/                # Centralized Excel Parsers, Logger, Status Updater
│   │   ├── tests/                          # Positive, Negative & Navigation PO update suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   ├── requirements.txt                # Sub-module specific dependencies
│   │   └── README.md                       # PO update operations manual
│   │
│   ├── customer-management/                # 👥 Customer Record Updates Module (Mrugank)
│   │   ├── customer_update_pages/          # CustomerUpdatePage, FormExecutor, LoginPage
│   │   ├── customer_update_utils/          # Excel Loader, Logger, Popup integrations
│   │   ├── tests/                          # Positive, Negative & Navigation customer update suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   └── README.md                       # Customer update operations manual
│   │
│   ├── employee-management/                # 👤 Employee Record Updates Module (Mrugank)
│   │   ├── emp_update_pages/               # EmployeeUpdatePage, FormExecutor, LoginPage
│   │   ├── emp_update_utils/               # Excel Loader, Logger, Popup integrations
│   │   ├── tests/                          # Positive, Negative & Navigation employee update suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   └── README.md                       # Employee update operations manual
│   │
│   ├── invoice-management/                 # 🧾 Invoice Editing & Recalculation Module (Mrugank)
│   │   ├── invoice_update_pages/           # InvoiceUpdatePage, FormExecutor, LoginPage
│   │   ├── invoice_update_utils/           # Excel Loader, Line-Item Recalculation Helpers
│   │   ├── tests/                          # Positive, Negative & Navigation invoice update suites
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   └── README.md                       # Invoice update operations manual
│   │
│   ├── pytest.ini                          # Root Update operations pytest configuration
│   └── README.md                           # Update operations overview & guidelines
│
├── swarajya-login/                         # 🔐 Master Authentication & Access Control Suite
│   ├── emp-manager/                        # 👤 Employee & Manager Authentication (Himanshu)
│   │   ├── tests/                          # Positive & Negative dual-role authentication flows
│   │   ├── conftest.py                     # Employee & Manager lifecycle hooks & fixtures
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   ├── requirements.txt                # Sub-module dependencies
│   │   └── README.md                       # Employee & Manager login documentation
│   │
│   ├── hr_admin/                           # 🛡️ HR & Super-Admin Authentication (Mrugank)
│   │   ├── tests/                          # Positive & Negative admin authentication & 2FA flows
│   │   ├── conftest.py                     # HR & Admin lifecycle hooks & fixtures
│   │   ├── pytest.ini                      # Sub-module test runner configuration
│   │   ├── requirements.txt                # Sub-module dependencies
│   │   └── README.md                       # HR & Admin login documentation
│   │
│   ├── pytest.ini                          # Root Login operations pytest configuration
│   └── README.md                           # Authentication operations overview
│
├── conftest.py                             # Root Pytest fixtures, sys.path resolution & CLI options
├── pytest.ini                              # Master test discovery, markers, and logging config
└── requirements.txt                        # Global pinned production dependencies
```

---

### 🔄 Architectural Data & Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Execution Trigger Layer                               │
│  GitHub Actions CI/CD Pipeline  │  Local CLI (`pytest`)  │  VS Code Runner   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Configuration & Resolution Layer                         │
│  Root `conftest.py`  │  CLI Flags (`--headless`, `--env`)  │  Sys Path Hooks │
│  Dynamic Env Vars (`SWARAJYA_BASE_URL`, `SWARAJYA_EMPLOYEE_ID`, `HEADLESS`)  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Data-Driven Repository Layer                             │
│  `shared/test_data/Swarajya-test-data.xlsx`   ──► Test Payloads & Credentials│
│  `shared/test_data/Swarajya-test-cases.xlsx`  ──► Test Definitions & Step IDs│
│  `shared/test_data/sample_po.pdf`             ──► Binary Upload Fixture     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Page Object Model (POM) Layer                         │
│  `shared.pages.base_page.BasePage` ──► Dynamic Waits, Locators, Dialogs     │
│  `shared.pages.login_page.LoginPage` ──► Storage State Reuse (`auth_state`) │
│  Module Pages: `CustomerPage`, `EmployeePage`, `InvoicePage`, `POPage`, ... │
│  Form Executors: Encapsulated Form Submissions & Input Synchronization      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Target Application Under Test (AUT)                     │
│            Swarajya Staging Portal: `https://swarajya-stg...`               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Telemetry, Reporting & Audit Layer                       │
│  • Bi-Directional Master Excel Writeback (`Swarajya-test-cases.xlsx`)       │
│  • Custom Standalone HTML Report (`reports/latest_report.html`)              │
│  • 1-to-1 Screenshot Audit (`{STATUS}_{TC_ID}__{TIMESTAMP}.png`)            │
│  • Real-Time Desktop Summary Popup (`shared.utils.popup.ExecutionSummary`)   │
│  • GitHub Actions Artifact Archive (`swarajya-test-artifacts-*`)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Core Engineering & Architecture Highlights

1. **Zero Redundant Test Data**:
   - `shared/test_data/Swarajya-test-cases.xlsx` and `shared/test_data/Swarajya-test-data.xlsx` serve as the universal single source of truth across all 12 modules.
   - Feature branches contain zero binary Excel copies, preventing merge conflicts.
2. **Bi-Directional Result Logging**:
   - Real-time execution status (`Passed`, `Failed`, `Skipped`), standardized `AUT_*` IDs, execution durations, and timestamps are written directly back to the master workbook.
3. **Session State Caching (`auth_state_*.json`)**:
   - Authenticated browser storage state is saved to `shared.utils.paths.AUTH_STATE_FILE`, eliminating redundant login handshakes during large test runs.
4. **100% Dynamic Waits (Zero Hardcoded Sleeps)**:
   - Dynamic synchronization via Playwright assertions (`wait_for(state="visible")`, `wait_for_dom_ready()`, `wait_for_url()`).
5. **1-to-1 Screenshot Audit & Auto-Retention**:
   - Exactly 1 screenshot captured per test case (`{STATUS}_{TC_ID}__{TIMESTAMP}.png`) with automatic pruning of runs older than 24 hours.
6. **Execution Feedback & Reporting**:
   - Instant Tkinter desktop popup summary dialog presenting total, passed, failed, and duration metrics upon suite completion.
   - Standalone, self-contained HTML test reports generated per execution.

---

## ⚙️ CI/CD Pipeline & Zero Hardcoded Configuration

The framework enforces a strict **Zero Hardcoded Values** hierarchy:

```
1. CI/CD Environment Variables (Highest Priority)
        ↓ (if not set)
2. Master Test Data Workbook (`shared/test_data/Swarajya-test-data.xlsx`)
        ↓ (if not present)
3. Dynamic In-Memory Generation (Timestamps, Unique UUID Suffixes)
```

### Supported CI/CD Environment Variables

| Variable | Description | Default / Fallback |
| :--- | :--- | :--- |
| `SWARAJYA_BASE_URL` | Staging application target URL | `https://swarajya-stg.corecotechnologies.com` |
| `SWARAJYA_EMPLOYEE_ID` | Master Employee / Admin login ID | Loaded dynamically from Excel banner |
| `SWARAJYA_PASSWORD` | Master login password | Loaded dynamically from Excel banner |
| `SWARAJYA_AUTH_CODE` | 2FA authentication code | Loaded from Excel / environment |
| `HEADLESS` / `CI` | Run browser in headless mode | `1` / `true` in CI workflows |
| `PYTEST_NO_POPUP` | Suppress desktop popup dialogs in CI | `1` in headless environments |

---

## 🏃 Running Tests

### 👤 Execute Himanshu's Modules

```bash
# 1. Employee & Manager Login Suite (22 tests)
pytest swarajya-login/emp-manager/tests -v

# 2. Create Employee Management Suite (25 tests)
pytest swarajya-create/employee-management/tests -v

# 3. Create Vendor Management Suite (29 tests)
pytest swarajya-create/vendor-management/tests -v

# 4. Create Customer Management Suite (34 tests)
pytest swarajya-create/customer-management/tests -v

# 5. Create Invoice Management Suite (27 tests)
pytest swarajya-create/invoice-management/tests -v

# 6. Update Purchase Orders Suite (31 tests)
pytest swarajya-update/purchase-orders/tests -v
```

### 👤 Execute Mrugank's Modules

```bash
# 1. HR & Admin Login Suite (39 tests)
pytest swarajya-login/hr_admin/tests -v

# 2. Create Consultant Management Suite (47 tests)
pytest swarajya-create/consultant-management/tests -v

# 3. Create Purchase Order Suite (33 tests)
pytest swarajya-create/purchase-order/tests -v

# 4. Update Employee Management Suite (31 tests)
pytest swarajya-update/employee-management/tests -v

# 5. Update Customer Management Suite (51 tests)
pytest swarajya-update/customer-management/tests -v

# 6. Update Invoice Management Suite (32 tests)
pytest swarajya-update/invoice-management/tests -v
```

### 🌐 Full Suite Executions

```bash
# Run all Create operations
pytest swarajya-create -v

# Run all Update operations
pytest swarajya-update -v

# Run all Login operations
pytest swarajya-login -v

# Run complete test suite with HTML report
pytest -v --html=reports/full_report.html --self-contained-html

# Run in interactive headed mode
pytest swarajya-login/hr_admin/tests -v --headed
```

---

## 🔀 Branch Management & Conflict-Free PR Strategy

To guarantee zero merge conflicts during team collaboration:
1. **Work Only in Designated Feature Branches**: Every contributor checks out their designated isolated branch.
2. **Shared Framework Updates First**: Any modification to `shared/` core components must be branched off `shared`, tested, and merged into `main` via PR before module branches sync.
3. **Rebase / Sync with `main` Before PR**:
   ```bash
   git fetch origin
   git merge origin/main
   # Resolve any module-specific differences and verify test suite passes
   git push origin <your-branch-name>
   ```
4. **Open Pull Request to `main`**: Ensure the GitHub Actions CI pipeline runs green before merging.
