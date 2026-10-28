# 🚀 Swarajya Staging Automation Framework

An enterprise-grade, data-driven end-to-end test automation framework for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), engineered with **Python 3.12+**, **Playwright**, **Requests**, **Pytest**, and **OpenPyXL**.

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
| **Himanshu** | 🔍 Read & Report Operations | Invoice Reports (API Automation) | [`read/invoice-report`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/read/invoice-report) | `swarajya-read/invoice-report` | `readinvoice-reports` | `readinvoice-report` | **13** | ✅ Merged |
| **Mrugank** | 🔐 Authentication | HR & Admin Login | [`login/hr_admin`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/hr_admin) | `swarajya-login/hr_admin` | `loginhr_admin` | `loginhr_admin` | **39** | ✅ Merged |
| **Mrugank** | 📋 Create Operations | Consultant Management | [`create/consultant_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/consultant_mgmt) | `swarajya-create/consultant-management` | `createconsultant_mgmt` | `createconsultant_mgmt` | **47** | ✅ Merged |
| **Mrugank** | 📋 Create Operations | Purchase Order Creation | [`create/purchase_order`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/purchase_order) | `swarajya-create/purchase-order` | `createpurchase_order` | `createpurchase_order` | **33** | ✅ Merged |
| **Mrugank** | 🔄 Update Operations | Employee Updates | [`update/emp_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/emp_mgmt) | `swarajya-update/employee-management` | `updateemp_mgmt` | `updateemp_mgmt` | **31** | ✅ Merged |
| **Mrugank** | 🔄 Update Operations | Customer Updates | [`update/customer_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/customer_mgmt) | `swarajya-update/customer-management` | `updatecustomer_mgmt` | `updatecustomer_mgmt` | **51** | ✅ Merged |
| **Mrugank** | 🔄 Update Operations | Invoice Updates | [`update/invoice_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/invoice_mgmt) | `swarajya-update/invoice-management` | `updateinvoice_mgmt` | `updateinvoice_mgmt` | **32** | ✅ Merged |
| **Mrugank** | 🔍 Read & Report Operations | Customer Insights (API Automation) | [`read/customer_insights`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/read/customer_insights) | `swarajya-read/customer_insights` | `readcustomer_insights` | `readcustomer_insights` | **16** | ✅ Merged |
| **Collaborative** | 🌐 Core Framework | Shared Infrastructure | [`shared`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/shared) | `shared/` | *Universal Base* | *Universal Base* | **Core** | ✅ Integrated |
| **Collaborative** | 🚀 Production / Master | Integrated Suite | [`main`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/main) | *Root* | *All Sheets (14)* | *All Sheets (14)* | **436** | 🚀 Production |

---

### 👤 Himanshu's Modules & Branch Responsibilities

Himanshu owns the core framework architecture, employee/manager authentication, full creation lifecycle for Employees, Vendors, Customers, and Invoices, the Purchase Order update suite, and the Invoice Report API automated test suite.

| Branch | Module Scope | Key Automated Scenarios & Highlights | Test Count | Status |
| :--- | :--- | :--- | :---: | :---: |
| [`login/emp-manager`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/emp-manager) | **Employee & Manager Authentication** | • Dual-role login flows (Employee, Manager)<br>• 2FA verification & session persistence<br>• Negative error states, locked accounts & role RBAC checks | **22** | Merged |
| [`create/emp-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/emp-mgmt) | **Create Employee Management** | • Multi-tab onboarding form automation<br>• Datepicker selection & department dropdowns<br>• Validation assertions, duplicate email/ID handling & Excel writeback | **25** | Merged |
| [`create/vendor-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/vendor-mgmt) | **Create Vendor Management** | • Full vendor profile creation & PAN/GST validation<br>• 10-digit phone regex and mandatory field checks<br>• Confirmation popup handling & post-creation grid search | **29** | Merged |
| [`create/customer-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/customer-mgmt) | **Create Customer Management** | • 20+ field onboarding with currency/tax/terms matrices<br>• IGST toggle switch & dynamic address parsing<br>• Modal dialog handling (Yes/No dismissal) & route verification | **34** | Merged |
| [`create/invoice-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/invoice-mgmt) | **Create Invoice Management** | • Complete invoice creation workflow with customer binding<br>• Line items calculation, tax breakdown & total tallying<br>• Form mount wait guards & cached authentication state | **27** | Merged |
| [`update/purchase-order`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/purchase-order) | **Update Purchase Orders** | • Purchase Order search, edit & status modification<br>• Line item adjustments, audit tracking & remarks<br>• Defect tracking with `wasxfail` integration and 1-to-1 screenshot audit | **31** | Merged |
| [`read/invoice-report`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/read/invoice-report) | **Invoice Report API Automation** | • 13 automated REST API test scenarios (7 positive, 6 negative)<br>• Zero hardcoding with dynamic financial year parsing & live JWT token generation<br>• Bi-directional Excel synchronization with cell styling & dark-theme Coreco HTML reporting with scenario specifications | **13** | Merged |

---

### 👤 Mrugank's Modules & Branch Responsibilities

Mrugank owns HR & Admin authentication, consultant onboarding, purchase order creation, and update workflows for Employees, Customers, and Invoices.

| Branch | Module Scope | Key Automated Scenarios & Highlights | Test Count | Status |
| :--- | :--- | :--- | :---: | :---: |
| [`login/hr_admin`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/hr_admin) | **HR & Admin Authentication** | • HR & Super-Admin login credentials & 2FA<br>• Password recovery, invalid credentials & boundary test cases<br>• Dynamic wait optimizations & role-specific dashboard routing | **39** | Merged |
| [`create/consultant_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/consultant_mgmt) | **Create Consultant Management** | • Complete consultant profile creation & contract period assignment<br>• Hourly/monthly rate validations & bank account binding<br>• Modal confirmation handling & grid search verification | **47** | Merged |
| [`create/purchase_order`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/purchase_order) | **Create Purchase Order** | • End-to-end PO creation linked to customer profiles<br>• Base, tax, and total amount calculation checks<br>• `sample_po.pdf` document upload automation & submission verification | **33** | Merged |
| [`update/emp_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/emp_mgmt) | **Update Employee Management** | • Existing employee record search & profile field modification<br>• Role, department, and salary update assertions<br>• Confirmation popup verification and audit logging | **31** | Merged |
| [`update/customer_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/customer_mgmt) | **Update Customer Management** | • Customer detail updates (billing address, contact, GST)<br>• Active/Inactive state toggling & credit limit revisions<br>• Offline network simulation & negative validation handling | **51** | Merged |
| [`update/invoice_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/invoice_mgmt) | **Update Invoice Management** | • Invoice editing, item additions/removals, and recalculations<br>• Status transitions (Draft → Approved → Sent → Paid)<br>• Data-driven automation mirroring invoice management standards | **32** | Merged |
| [`read/customer_insights`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/read/customer_insights) | **Customer Insights API Automation** | • 16 automated REST API test scenarios (6 positive, 2 negative, 8 data-driven)<br>• Fiscal period filtering (CFY, 2FY, 3FY, 5FY) & descending revenue sorting<br>• Zero-data handling, error schema assertions & Excel sync | **16** | Merged |

---

## 🏛️ Comprehensive Framework Architecture & Directory Hierarchy

The framework is architected according to strict **Layered Separation of Concerns**, ensuring high modularity, maximum code reusability, zero hardcoding, and clean separation between test definitions, business page logic, and data infrastructure.

### 📂 Exhaustive Repository Directory Tree

Below is the complete, comprehensive directory and file breakdown of the entire repository:

```
swarajya-stg-automation/
│
├── .github/                                                # 🤖 Continuous Integration & Continuous Deployment
│   └── workflows/
│       └── ci.yml                                         # Multi-stage GitHub Actions CI/CD matrix pipeline
│
├── shared/                                                # 🌐 Centralized Universal Core Infrastructure
│   ├── README.md                                          # Shared framework documentation & usage guide
│   ├── __init__.py                                        # Shared namespace initializer
│   │
│   ├── config/                                            # Global configurations & system constants
│   │   ├── README.md                                      # Configuration guidelines
│   │   ├── __init__.py                                    # Config namespace package
│   │   └── constants.py                                   # Universal timeouts, URLs, standard roles, and regex patterns
│   │
│   ├── pages/                                             # Core Page Object Model (POM) foundation
│   │   ├── README.md                                      # POM design patterns and locator guidelines
│   │   ├── __init__.py                                    # Pages package initializer
│   │   ├── auth_setup_page.py                             # Authenticated session generator and storage state exporter
│   │   ├── base_page.py                                   # Base Playwright actions, dynamic waits, dropdown selectors, screenshot hooks
│   │   ├── login_page.py                                  # Centralized authentication page object with credential injection
│   │   └── tfa_page.py                                    # Two-Factor Authentication (2FA) verification page object
│   │
│   ├── reporter/                                          # Custom dark-theme Coreco HTML reporting engine & analytics
│   │   ├── README.md                                      # Reporter integration & hook documentation
│   │   ├── __init__.py                                    # Reporter package initializer
│   │   ├── hooks.py                                       # Pytest execution hooks (`pytest_runtest_makereport`, status tracking)
│   │   ├── html_reporter.py                               # Standalone HTML report generator with embedded analytics
│   │   ├── models.py                                      # Data models for test case execution, timings, and status
│   │   ├── template.py                                    # Modern responsive HTML5/CSS3 template definitions with scenario details
│   │   └── assets/
│   │       └── coreco_logo.png                            # Corporate Coreco logo embedded in generated HTML reports
│   │
│   ├── test_data/                                         # Universal Single Source of Truth (Zero Duplication)
│   │   ├── README.md                                      # Excel structure & test case specification guidelines
│   │   ├── Swarajya-test-cases.xlsx                       # Master test cases workbook (13 sheets, statuses, run history)
│   │   ├── Swarajya-test-data.xlsx                        # Master test data repository (13 sheets, input payloads, credentials)
│   │   ├── auth_state_session.json                        # Cached authenticated browser session state (session token)
│   │   ├── auth_state_swarajya-stg_corecotechnologies_com.json # Master cached Playwright browser storage state
│   │   └── sample_po.pdf                                  # Standard PDF artifact for Purchase Order file upload tests
│   │
│   └── utils/                                             # Universal helper utilities & common services
│       ├── README.md                                      # Utilities documentation
│       ├── __init__.py                                    # Utils package initializer
│       ├── excel_base.py                                  # Base workbook loader & bi-directional execution result writer
│       ├── excel_loader.py                                # High-performance OpenPyXL dynamic loader & cell parser
│       ├── logger.py                                      # Unified console and rotating file logger with timestamps
│       ├── paths.py                                       # Cross-platform path resolver for root, data, reports, and screenshots
│       └── popup.py                                       # Desktop execution summary popup modal (Tkinter)
│
├── swarajya-create/                                       # 📋 Master Create Operations Domain
│   ├── README.md                                          # Create operations overview & guidelines
│   │
│   ├── consultant-management/                             # 💼 Consultant Profile Creation Module (Mrugank)
│   │   ├── README.md                                      # Consultant onboarding guide
│   │   ├── conftest.py                                    # Consultant lifecycle hooks, fixtures & CLI flags
│   │   ├── pytest.ini                                     # Sub-module test runner configuration
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   ├── consultant_pages/                              # Consultant Page Object Model
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   ├── consultant_page.py                         # Consultant Page actions & locators
│   │   │   └── form_executor.py                           # Form submission & verification flow executor
│   │   ├── consultant_utils/                              # Consultant-specific utilities
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   └── excel_reader.py                            # Centralized Excel reader for consultant sheets
│   │   └── tests/                                         # Consultant automated test suites
│   │       ├── __init__.py                                # Package initializer
│   │       ├── test_consultant_negative_flows.py          # 26 negative validation scenarios
│   │       └── test_consultant_positive_flows.py          # 21 positive end-to-end creation scenarios
│   │
│   ├── customer-management/                               # 👥 Customer Onboarding Module (Himanshu)
│   │   ├── README.md                                      # Customer onboarding manual
│   │   ├── conftest.py                                    # Customer lifecycle hooks & fixtures
│   │   ├── pytest.ini                                     # Sub-module test runner configuration
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   ├── customer_pages/                                # Customer Page Object Model
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   ├── customer_page.py                           # Customer creation page object
│   │   │   ├── form_executor.py                           # Comprehensive 20+ field form submission engine
│   │   │   └── login_page.py                              # Module-specific login bridge
│   │   ├── customer_utils/                                # Customer utilities
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   └── excel_reader.py                            # Customer test data & case parser
│   │   └── tests/                                         # Customer test suites
│   │       ├── __init__.py                                # Package initializer
│   │       ├── test_customer_login_flow.py                # Pre-condition authentication validation
│   │       ├── test_customer_negative_flows.py            # Validation errors, boundary values & mandatory checks
│   │       └── test_customer_positive_flows.py            # Happy-path onboarding with currency & tax matrix
│   │
│   ├── employee-management/                               # 👤 Employee Onboarding Module (Himanshu)
│   │   ├── README.md                                      # Employee onboarding manual
│   │   ├── conftest.py                                    # Employee lifecycle hooks & fixtures
│   │   ├── pytest.ini                                     # Sub-module test runner configuration
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   ├── emp_pages/                                     # Employee Page Object Model
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   ├── employee_page.py                           # Multi-tab employee onboarding page object
│   │   │   ├── form_executor.py                           # Dynamic tab executor & datepicker synchronizer
│   │   │   └── project_page.py                            # Project allocation page object
│   │   ├── emp_utils/                                     # Employee utilities
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   └── excel_reader.py                            # Employee Excel loader
│   │   └── tests/                                         # Employee test suites
│   │       ├── test_emp_login_flow.py                     # Login state assertion
│   │       ├── test_emp_negative_flows.py                 # Duplicate email, invalid PAN/Aadhaar & format errors
│   │       └── test_emp_positive_flows.py                 # Full lifecycle onboarding with bank/address binding
│   │
│   ├── invoice-management/                                # 🧾 Invoice Creation Module (Himanshu)
│   │   ├── README.md                                      # Invoice creation operations guide
│   │   ├── conftest.py                                    # Invoice fixtures & browser setup
│   │   ├── pytest.ini                                     # Sub-module test runner configuration
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   ├── invoice_pages/                                 # Invoice Page Object Model
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   ├── form_executor.py                           # Item addition, calculation & submission engine
│   │   │   └── invoice_page.py                            # Invoice form locators & interaction logic
│   │   ├── invoice_utils/                                 # Invoice utilities
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   └── excel_reader.py                            # Invoice Excel reader
│   │   └── tests/                                         # Invoice test suites
│   │       ├── __init__.py                                # Package initializer
│   │       ├── test_invoice_negative_flows.py             # Empty items, negative amounts & tax mismatch checks
│   │       └── test_invoice_positive_flows.py             # End-to-end invoice creation with auto-calculated totals
│   │
│   ├── purchase-order/                                    # 📦 Purchase Order Creation Module (Mrugank)
│   │   ├── README.md                                      # PO creation documentation
│   │   ├── conftest.py                                    # PO fixtures & browser context
│   │   ├── pytest.ini                                     # Sub-module test runner configuration
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   ├── po_pages/                                      # Purchase Order Page Object Model
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   ├── form_executor.py                           # PO form submission engine
│   │   │   └── po_page.py                                 # PO creation locators & PDF upload hook
│   │   ├── po_utils/                                      # PO utilities
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   └── excel_reader.py                            # PO Excel reader
│   │   └── tests/                                         # Purchase Order test suites
│   │       ├── __init__.py                                # Package initializer
│   │       ├── test_po_negative_flows.py                  # Missing documents, invalid dates & field validations
│   │       └── test_po_positive_flows.py                  # End-to-end PO creation with PDF attachment
│   │
│   └── vendor-management/                                 # 🏢 Vendor Onboarding Module (Himanshu)
│       ├── README.md                                      # Vendor onboarding documentation
│       ├── conftest.py                                    # Vendor fixtures & hooks
│       ├── pytest.ini                                     # Sub-module test runner configuration
│       ├── requirements.txt                               # Sub-module dependencies
│       ├── tests/                                         # Vendor test suites
│       │   ├── test_vendor_login_flow.py                  # Pre-test login verification
│       │   ├── test_vendor_negative_flows.py              # Invalid GSTIN, PAN regex & missing phone numbers
│       │   └── test_vendor_positive_flows.py              # Successful vendor registration & post-create search
│       ├── vendor_pages/                                  # Vendor Page Object Model
│       │   ├── __init__.py                                # Package initializer
│       │   ├── form_executor.py                           # Vendor form fill and submit engine
│       │   └── vendor_page.py                             # Vendor form locators & confirmation handling
│       └── vendor_utils/                                  # Vendor utilities
│           ├── __init__.py                                # Package initializer
│           └── excel_reader.py                            # Vendor test data & case parser
│
├── swarajya-login/                                        # 🔐 Master Authentication & Access Control Domain
│   ├── README.md                                          # Authentication domain architecture overview
│   │
│   ├── emp-manager/                                       # 👤 Employee & Manager Authentication (Himanshu)
│   │   ├── README.md                                      # Employee & Manager login manual
│   │   ├── __init__.py                                    # Package initializer
│   │   ├── conftest.py                                    # Employee & Manager fixtures & login assertions
│   │   ├── pytest.ini                                     # Sub-module test runner configuration
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   └── tests/                                         # Login test suites
│   │       ├── __init__.py                                # Package initializer
│   │       ├── negative_flows.py                          # Invalid credentials, locked accounts & boundary checks
│   │       └── positive_flows.py                          # Dual-role login flows & 2FA verification
│   │
│   └── hr_admin/                                          # 🛡️ HR & Super-Admin Authentication (Mrugank)
│       ├── README.md                                      # HR & Admin login manual
│       ├── __init__.py                                    # Package initializer
│       ├── conftest.py                                    # HR & Admin fixtures & 2FA hooks
│       ├── pytest.ini                                     # Sub-module test runner configuration
│       ├── requirements.txt                               # Sub-module dependencies
│       └── tests/                                         # Admin test suites
│           ├── negative_flows.py                          # Super-Admin security boundary & invalid input tests
│           └── positive_flows.py                          # HR/Admin credentials, 2FA validation & dashboard routing
│
├── swarajya-read/                                         # 🔍 Master Read & Reporting Operations Domain
│   ├── customer_insights/                                 # 📊 Customer Analytics & Intelligence Module (Mrugank)
│   │   ├── README.md                                      # Customer Insights API technical manual
│   │   ├── __init__.py                                    # Module package initializer
│   │   ├── conftest.py                                    # Session fixtures, auth hooks & Excel reporter
│   │   ├── pytest.ini                                     # Test runner configuration & markers
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   │
│   │   ├── customer_insights_api/                         # Core API Client & Verification Layer
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   ├── api_client.py                              # REST Client with dynamic wait & retry
│   │   │   ├── assertions.py                              # Domain assertions (revenue metrics, periods, sorting)
│   │   │   └── auth.py                                    # Dynamic JWT Bearer token resolver
│   │   │
│   │   ├── customer_insights_utils/                       # Data Extraction & Central Excel Synchronization
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   └── excel_reader.py                            # Central Excel reader & results updater
│   │   │
│   │   └── tests/                                         # Automated Test Suites (16 tests)
│   │       ├── __init__.py                                # Test package initializer
│   │       ├── test_customer_insights_data_driven.py      # Parameterized Excel row runner (8 tests)
│   │       ├── test_customer_insights_negative.py         # Negative flows & error schema validation (2 tests)
│   │       └── test_customer_insights_positive.py         # Positive flows, sorting & period filters (6 tests)
│   │
│   └── invoice-report/                                    # 🧾 Invoice Report REST API Automation Module (Himanshu)
│       ├── README.md                                      # Comprehensive Invoice Report API technical manual
│       ├── __init__.py                                    # Module package initializer
│       ├── conftest.py                                    # Session fixtures, dynamic JWT token & base URL resolvers
│       ├── pytest.ini                                     # Test discovery, markers (`api`), logging
│       ├── requirements.txt                               # Sub-module dependencies (`requests`, `openpyxl`, `pytest`)
│       │
│       ├── invoice_report_api/                            # REST API Client & Verification Layer
│       │   ├── __init__.py                                # API package initializer
│       │   ├── api_client.py                              # Resilient HTTP Client (`GET /api/reports/invoice-report`)
│       │   ├── assertions.py                              # Strict status, schema, metric & financial reconciliation assertions
│       │   └── auth.py                                    # Dynamic login & JWT Bearer token generation
│       │
│       ├── invoice_report_utils/                          # Data Extraction & Central Excel Synchronization
│       │   ├── __init__.py                                # Utils package initializer
│       │   └── excel_reader.py                            # Dynamic test case & test data loader + result writer
│       │
│       └── tests/                                         # Complete Invoice Report API Automated Test Suite (13 tests)
│           ├── test_invoice_reports_negative.py           # 6 negative validation, 401/403 security & boundary tests
│           └── test_invoice_reports_positive.py           # 7 positive functional, drilldown & status filter tests
├── swarajya-update/                                       # 🔄 Master Update Operations Domain
│   ├── README.md                                          # Update operations overview & guidelines
│   │
│   ├── customer-management/                               # 👥 Customer Record Updates Module (Mrugank)
│   │   ├── README.md                                      # Customer update manual
│   │   ├── conftest.py                                    # Customer update fixtures & browser setup
│   │   ├── pytest.ini                                     # Sub-module test runner configuration
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   ├── customer_update_pages/                         # Customer Update Page Object Model
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   ├── customer_update_page.py                    # Search, edit & modification locators
│   │   │   └── form_executor.py                           # Update execution engine
│   │   ├── customer_update_utils/                         # Customer update utilities
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   └── excel_reader.py                            # Customer update Excel parser
│   │   └── tests/                                         # Customer update test suites
│   │       ├── __init__.py                                # Package initializer
│   │       ├── test_customer_update_login_flow.py         # Login assertion
│   │       ├── test_customer_update_negative_flows.py     # Inactive toggle errors & validation handling
│   │       └── test_customer_update_positive_flows.py     # Billing address, contact & GST update checks
│   │
│   ├── employee-management/                               # 👤 Employee Record Updates Module (Mrugank)
│   │   ├── README.md                                      # Employee update manual
│   │   ├── conftest.py                                    # Employee update fixtures
│   │   ├── pytest.ini                                     # Sub-module test runner configuration
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   ├── emp_update_pages/                              # Employee Update Page Object Model
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   ├── employee_update_page.py                    # Employee search & edit locators
│   │   │   └── form_executor.py                           # Update submission engine
│   │   ├── emp_update_utils/                              # Employee update utilities
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   └── excel_reader.py                            # Employee update Excel reader
│   │   └── tests/                                         # Employee update test suites
│   │       ├── __init__.py                                # Package initializer
│   │       ├── test_emp_update_login_flow.py              # Login state validation
│   │       ├── test_emp_update_negative_flows.py          # Boundary, invalid role & mismatch validations
│   │       └── test_emp_update_positive_flows.py          # Department, salary & profile update assertions
│   │
│   ├── invoice-management/                                # 🧾 Invoice Editing & Recalculation Module (Mrugank)
│   │   ├── README.md                                      # Invoice update operations manual
│   │   ├── conftest.py                                    # Invoice update fixtures
│   │   ├── pytest.ini                                     # Sub-module test runner configuration
│   │   ├── requirements.txt                               # Sub-module dependencies
│   │   ├── invoice_update_pages/                          # Invoice Update Page Object Model
│   │   │   ├── __init__.py                                # Package initializer
│   │   │   ├── form_executor.py                           # Line item adjustment & status transition engine
│   │   │   └── invoice_update_page.py                     # Invoice update locators & controls
│   │   ├── invoice_update_utils/                          # Invoice update utilities
│   │   │   ├── __init__.py                                # Package initializer
│   │   └── excel_reader.py                                # Invoice update Excel loader
│   │   └── tests/                                         # Invoice update test suites
│   │       ├── test_invoice_update_login_flow.py          # Login verification
│   │       ├── test_invoice_update_negative_flows.py      # Invalid status transitions & calculation errors
│   │       └── test_invoice_update_positive_flows.py      # Status shifts (Draft → Approved → Sent → Paid)
│   │
│   └── purchase-orders/                                   # 📑 Purchase Order Modification Module (Himanshu)
│       ├── README.md                                      # PO update operations manual
│       ├── conftest.py                                    # PO update fixtures & options
│       ├── pytest.ini                                     # Sub-module test runner configuration
│       ├── requirements.txt                               # Sub-module dependencies
│       ├── po_update_pages/                               # PO Update Page Object Model
│       │   ├── __init__.py                                # Package initializer
│       │   ├── form_executor.py                           # PO modification & remarks executor
│       │   └── po_update_page.py                          # PO search, edit & status modification locators
│       ├── po_update_utils/                               # PO update utilities
│       │   ├── __init__.py                                # Package initializer
│       │   └── excel_reader.py                            # Centralized Excel reader for update_po sheets
│       └── tests/                                         # PO update test suites
│           ├── __init__.py                                # Package initializer
│           ├── test_po_update_login_flow.py               # Login validation
│           ├── test_po_update_negative_flows.py           # Closed PO edits, negative quantities & remarks checks
│           └── test_po_update_positive_flows.py           # Status transitions & item recalculation checks
│
├── conftest.py                                            # Root Pytest fixtures, sys.path resolution & CLI options
├── pytest.ini                                             # Master test discovery, markers, and logging config
└── requirements.txt                                       # Global pinned production dependencies
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
│  Root `conftest.py`  │  CLI Flags (`--headless`, `--api-url`, `--popup`)    │
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
┌──────────────────────────────────────┴──────────────────────────────────────┐
│                                                                             │
▼                                                                             ▼
┌─────────────────────────────────────────┐   ┌───────────────────────────────┐
│       UI Layer: Page Object Model       │   │  API Layer: REST Client &     │
│  `shared.pages.base_page.BasePage`      │   │  Dynamic Assertion Engine     │
│  • Dynamic Waits, Locators, Dialogs     │   │  `InvoiceReportApiClient`     │
│  • Playwright Browser Automation        │   │  • Request Retries & Headers  │
│  • Storage State Reuse (`auth_state`)   │   │  • Dynamic Token Resolution   │
│  • Multi-Tab Form Executors             │   │  • Strict Schema Validation   │
└────────────────────┬────────────────────┘   └───────────────┬───────────────┘
                     │                                        │
                     ▼                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Target Application Under Test (AUT)                     │
│            Swarajya Staging Portal: `https://swarajya-stg...`               │
│               [UI Web Frontend  &  REST HTTP API Endpoints]                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Telemetry, Reporting & Audit Layer                       │
│  • Bi-Directional Master Excel Writeback (`Swarajya-test-cases.xlsx`)       │
│  • Custom Standalone Coreco HTML Report (`reports/read_invoice_report.html`)│
│  • 1-to-1 Screenshot Audit (`{STATUS}_{TC_ID}__{TIMESTAMP}.png`)            │
│  • Real-Time Desktop Summary Popup (`shared.utils.popup.show_summary_popup`)│
│  • GitHub Actions Artifact Archive (`swarajya-test-artifacts-*`)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Core Engineering & Architecture Highlights

1. **Zero Redundant Test Data**:
   - `shared/test_data/Swarajya-test-cases.xlsx` and `shared/test_data/Swarajya-test-data.xlsx` serve as the universal single source of truth across all 13 modules.
   - Individual branches contain zero binary copies or hardcoded values, preventing merge conflicts.
2. **Bi-Directional Result Logging**:
   - Real-time execution status (`PASS`, `FAIL`, `SKIPPED`), standardized `AUT_*` IDs, execution durations, and timestamps are written directly back to the master workbook with green/red cell formatting.
3. **Session State Caching (`auth_state_*.json`)**:
   - Authenticated browser storage state is saved to `shared.utils.paths.AUTH_STATE_FILE`, eliminating redundant login handshakes during large test runs.
4. **100% Dynamic Synchronization (Zero Hardcoded Sleeps)**:
   - Dynamic synchronization via Playwright assertions (`wait_for(state="visible")`, `wait_for_dom_ready()`, `wait_for_url()`) and robust HTTP timeout backoffs for API automation.
5. **Standardized Dark-Theme Coreco HTML Reporter**:
   - Custom standalone HTML test reports enriched with **Scenario Specification & Verification Details**, **Execution Parameters & Endpoint Specs**, and **Live Console Output/Logs** with a copy-to-clipboard button.
6. **1-to-1 Screenshot Audit & Auto-Retention**:
   - Exactly 1 screenshot captured per UI test case (`{STATUS}_{TC_ID}__{TIMESTAMP}.png`) with automatic pruning of runs older than 24 hours.
7. **Execution Feedback & Reporting**:
   - Instant Tkinter desktop popup summary dialog presenting total, passed, failed, and duration metrics upon suite completion (suppressed gracefully in CI via `PYTEST_NO_POPUP=1` and `CI=true`).

---

## ⚙️ CI/CD Pipeline & Zero Hardcoded Configuration

The framework enforces a strict **Zero Hardcoded Values** hierarchy:

```
1. CI/CD Environment Variables (Highest Priority)
        ↓ (if not set)
2. Master Test Data Workbook (`shared/test_data/Swarajya-test-data.xlsx`)
        ↓ (if not present)
3. Dynamic In-Memory Generation (Timestamps, Unique UUID Suffixes, Ephemeral JWTs)
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

# 7. Invoice Report API Automation Suite (13 tests: 7 Positive, 6 Negative)
pytest swarajya-read/invoice-report/tests -v
pytest swarajya-read/customer_insights/tests -v

# Run specific Invoice Report API test suites
pytest swarajya-read/invoice-report/tests/test_invoice_reports_positive.py -v
pytest swarajya-read/invoice-report/tests/test_invoice_reports_negative.py -v
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

# 7. Customer Insights API Automation Suite (16 tests)
pytest swarajya-read/customer_insights/tests -v
```

### 🌐 Full Suite Executions

```bash
# Run all Create operations
pytest swarajya-create -v

# Run all Update operations
pytest swarajya-update -v

# Run all Read & Report operations
pytest swarajya-read/invoice-report/tests -v
pytest swarajya-read/customer_insights/tests -v

# Run all Login operations
pytest swarajya-login -v

# Run complete test suite across all modules with HTML report
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
