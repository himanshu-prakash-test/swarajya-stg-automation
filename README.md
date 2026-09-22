# 🚀 Swarajya Staging Automation Master Framework

Production-grade, end-to-end test automation framework powered by **Playwright (Python)** and **Pytest** for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/).

---

## 👥 Team Module Ownership & Division of Responsibilities

| Contributor / Scope | Modules Covered | Isolated Branches (Click to View) | Key Areas & Test Artifacts |
| :--- | :--- | :--- | :--- |
| **Himanshu** | • **Login Suite** (Employee & Manager)<br>• **Create Employee** Module<br>• **Create Vendor** Module<br>• **Create Customer** Module<br>• **Update Purchase Order** Module | [`login/emp-manager`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/emp-manager)<br>[`create/employee-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/employee-mgmt)<br>[`create/vendor-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/vendor-mgmt)<br>[`create/customer-mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/customer-mgmt)<br>[`update/purchase-orders`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/purchase-orders) | • `login_test_cases.xlsx`<br>• `Swarajya-Create-test-cases (6).xlsx`<br>• `Create-Vendor-Management.xlsx`<br>• `Create-Customer-Management.xlsx`<br>• `Update-Purchase-Order.xlsx`<br>• Dynamic Waits, Modal Handlers, Offline Mocks |
| **Mrugank** | • **HR / Admin Login** Suite<br>• **Create Consultant** Module<br>• **Create Purchase Order** Module<br>• **Update Employee** Module<br>• **Update Customer** Module | [`login/hr-admin`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/login/hr-admin)<br>[`create/consultant_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/consultant_mgmt)<br>[`create/purchase_order`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/create/purchase_order)<br>[`update/emp_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/emp_mgmt)<br>[`update/customer_mgmt`](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/update/customer_mgmt) | • `login_test_cases_ready.xlsx`<br>• `Create-Consultant-Management.xlsx`<br>• `Create-Purchase-Order-Test-Cases.xlsx`<br>• `Swarajya-Update-Employee-test-cases.xlsx`<br>• `Update-Customer-Management.xlsx`<br>• Update Form Validation, Consultant Flows, PO Creation |

---

## 🏗️ Unified Master Architecture

```
swarajya-stg-automation/
│
├── swarajya-login/                     # 🔐 Authentication & Session Suite
│   └── swarajya-automation/            # Employee & Manager Authentication
│       ├── pages/                      # LoginPage, TFAPage
│       ├── utils/                      # Excel I/O, Logger, Desktop Popup
│       ├── test_data/                  # login_test_cases.xlsx, credentials.xlsx
│       └── tests/test_login.py         # UI, Positive 2FA, Negative Creds, SQLi/XSS
│
├── swarajya-create/                    # 📋 Master Create Operations Suite
│   │
│   ├── employee-management/            # 👤 Create Employee Module (30 Tests)
│   │   ├── emp_pages/                  # BasePage, LoginPage, EmployeePage, FormExecutor
│   │   ├── emp_utils/                  # Excel Reader, Logger, Popup
│   │   ├── test_data/                  # Swarajya-Create-test-cases (6).xlsx
│   │   └── tests/                      # Positive & Negative Employee Test Suites
│   │
│   ├── vendor-management/              # 🏢 Create Vendor Module (24 Tests)
│   │   ├── vendor_pages/               # BasePage, LoginPage, VendorPage, FormExecutor
│   │   ├── vendor_utils/               # Excel Reader, Logger, Popup
│   │   ├── test_data/                  # Create-Vendor-Management.xlsx
│   │   └── tests/                      # Positive & Negative Vendor Test Suites
│   │
│   ├── consultant-management/          # 💼 Create Consultant Module (47 Tests)
│   │   ├── consultant_pages/           # BasePage, LoginPage, ConsultantPage, FormExecutor
│   │   ├── consultant_utils/           # Excel Reader, Logger, Popup
│   │   ├── test_data/                  # Create-Consultant-Management.xlsx, credentials.xlsx
│   │   └── tests/                      # Positive & Negative Consultant Creation Suites
│   │
│   ├── customer-management/            # 👥 Create Customer Module (36 Tests)
│   │   ├── customer_pages/             # BasePage, LoginPage, CustomerPage, FormExecutor
│   │   ├── customer_utils/             # Excel Reader
│   │   ├── test_data/                  # Create-Customer-Management.xlsx, credentials.xlsx
│   │   └── tests/                      # Positive & Negative Customer Creation Suites
│   │
│   └── purchase-order/                 # 📦 Create Purchase Order Module (20 Tests)
│       ├── po_pages/                   # BasePage, LoginPage, POPage, FormExecutor
│       ├── po_utils/                   # Excel Reader
│       ├── test_data/                  # Create-Purchase-Order-Test-Cases.xlsx, credentials.xlsx, sample_po.pdf
│       └── tests/                      # Login, Positive & Negative PO Creation Suites
│
├── swarajya-update/                    # 🔄 Master Update Operations Suite
│   ├── common/                         # 🌐 Shared Common Components
│   │   ├── pages/                      # Common Pages (login_page, auth_setup_page)
│   │   └── utils/                      # Common Utilities (excel_base)
│   │
│   ├── employee-management/            # 📝 Update Employee Module (26 Tests)
│   │   ├── emp_update_pages/           # BasePage, LoginPage, EmployeeUpdatePage, FormExecutor
│   │   ├── emp_update_utils/           # Excel Reader, Logger, Popup
│   │   ├── test_data/                  # Swarajya-Update-Employee-test-cases.xlsx, credentials.xlsx
│   │   └── tests/                      # Positive & Negative Employee Update Suites
│   │
│   ├── purchase-orders/                # 📑 Update Purchase Order Module (28 Tests)
│   │   ├── po_update_pages/            # BasePage, LoginPage, POUpdatePage
│   │   ├── po_update_utils/            # Excel Reader, Logger, Popup
│   │   ├── test_data/                  # Update-Purchase-Order.xlsx, credentials.xlsx
│   │   └── tests/                      # Positive, Negative, and Navigation PO Update Suites
│   │
│   ├── customer-management/            # 👥 Update Customer Module (49 Tests)
│   │   ├── customer_update_pages/      # BasePage, LoginPage, CustomerUpdatePage, FormExecutor
│   │   ├── customer_update_utils/      # Excel Reader, Logger
│   │   ├── test_data/                  # Update-Customer-Management.xlsx, credentials.xlsx
│   │   └── tests/                      # Login, Positive, and Negative Customer Update Suites
│   ├── pytest.ini                      # Suite-level Pytest Configuration
│   └── README.md                       # Update Operations Manual
│   
├── .gitignore                          # Excludes caches, screenshots & session tokens
├── pytest.ini                          # Root Pytest Configuration & Unified Markers
└── README.md                           # Master Architecture Documentation
```

---

## 📊 Comprehensive Test Coverage Matrix

| Category | Sub-Module | Ownership | Reference Workbook | Execution Mode |
| :--- | :--- | :---: | :--- | :--- |
| **Authentication** | Employee & Manager Login | **Himanshu** | `login_test_cases.xlsx` | Automated |
| **Authentication** | HR & Admin Login | **Mrugank** | `login_test_cases_ready.xlsx` | Automated |
| **Create Operations** | Employee Management | **Himanshu** | `Swarajya-Create-test-cases (6).xlsx` | Automated |
| **Create Operations** | Vendor Management | **Himanshu** | `Create-Vendor-Management.xlsx` | Automated |
| **Create Operations** | Customer Management | **Himanshu** | `Create-Customer-Management.xlsx` | Automated |
| **Create Operations** | Consultant Management | **Mrugank** | `Create-Consultant-Management.xlsx` | Automated |
| **Create Operations** | Purchase Order Creation | **Mrugank** | `Create-Purchase-Order-Test-Cases.xlsx` | Automated |
| **Update Operations** | Purchase Order Updates | **Himanshu** | `Update-Purchase-Order.xlsx` | Automated |
| **Update Operations** | Employee Updates | **Mrugank** | `Swarajya-Update-Employee-test-cases.xlsx` | Automated |
| **Update Operations** | Customer Updates | **Mrugank** | `Update-Customer-Management.xlsx` | Automated |

---

## ⚡ Core Engineering & Quality Standards

1. **100% Dynamic Synchronization (Zero Arbitrary Sleeps)**:
   - Event-driven Playwright assertions (`wait_for(state="visible")`, `wait_for_dom_ready()`, `wait_for_url()`).
2. **Bi-Directional Excel Reporting**:
   - Reads inputs dynamically from Excel and writes back real-time execution results (`PASS` / `FAIL`), `AUT_*` IDs, and timestamps.
3. **1-to-1 Screenshot Audit & Auto-Retention**:
   - Captures exactly 1 screenshot per test case (`{STATUS}_{TC_ID}__{TIMESTAMP}.png`).
   - Automatically purges screenshots older than 24 hours and caps folder size.
4. **Desktop Summary Dialogs**:
   - Instant Tkinter popup summary displaying execution metrics (Total, Passed, Failed, Duration) at the end of each session.
5. **Network Mocking & Security Payloads**:
   - Simulates offline/server outages (`context.set_offline(True)`).
   - Validates boundary checks, SQL Injection, and XSS sanitization.

---

## 🚀 Quick Execution Commands

### 👤 Himanshu's Modules

#### 1. Login Suite (Employee & Manager)
```powershell
cd swarajya-login\swarajya-automation
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

#### 5. Update Purchase Order Management
```powershell
cd swarajya-update\purchase-orders
pytest
```

---

### 👤 Mrugank's Modules

#### 1. Create Consultant Management
```powershell
cd swarajya-create\consultant-management
pytest
```

#### 2. Create Purchase Order Management
```powershell
cd swarajya-create\purchase-order
pytest
```

#### 3. Update Employee Management
```powershell
cd swarajya-update\employee-management
pytest
```

#### 4. Update Customer Management
```powershell
cd swarajya-update\customer-management
pytest
```

---

### 🌐 Full Suite Runs

```powershell
# Run all Create operations (Employee, Vendor, Consultant, Customer, PO)
pytest swarajya-create

# Run all Update operations (Employee, Purchase Orders, Customer)
pytest swarajya-update

# Run all tests across the entire repository
pytest
```
