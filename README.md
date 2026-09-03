# 🚀 Swarajya Staging Automation Master Framework

Production-grade, end-to-end test automation framework powered by **Playwright (Python)** and **Pytest** for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/).

---

## 👥 Team Module Ownership & Division of Responsibilities

| Contributor / Scope | Modules Covered | Branches | Key Areas & Test Artifacts |
| :--- | :--- | :--- | :--- |
| **Himanshu** | • **Login Suite** (Employee & Manager)<br>• **Create Employee** Module<br>• **Create Vendor** Module | `login/emp-manager`<br>`create/employee-mgmt`<br>`create/vendor-mgmt` | • `login_test_cases.xlsx`<br>• `Swarajya-Create-test-cases (6).xlsx`<br>• `Create-Vendor-Management.xlsx`<br>• Dynamic Waits, Modal Handlers, Network Offline Mocks |
| **Partner (Mrugank)** | • **HR / Admin Login** Suite<br>• **Update Employee** Module<br>• **Consultant Management** Module | `update_emp_mgmt`<br>`features/mrugank` | • `test_hr_admin.py`<br>• `Swarajya-Update-Employee-test-cases.xlsx`<br>• `Swarajya-Consultant-test-cases.xlsx`<br>• Update Form Validation, Consultant Flows |

---

## 🏗️ Unified Master Architecture

```
swarajya-stg-automation/
│
├── swarajya-login/                     # 🔐 Authentication & Session Suite
│   ├── swarajya-automation/            # Employee & Manager Authentication
│   │   ├── pages/                      # LoginPage, TFAPage
│   │   ├── utils/                      # Excel I/O, Logger, Desktop Popup
│   │   ├── test_data/                  # login_test_cases.xlsx, credentials.xlsx
│   │   └── tests/test_login.py         # UI, Positive 2FA, Negative Creds, SQLi/XSS
│   │
│   └── hr_admin/                       # 🛡️ HR & Admin Authentication (Partner Module)
│       └── tests/test_hr_admin.py      # HR/Admin RBAC, Role Authorization, 2FA
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
│   └── consultant-management/          # 💼 Create Consultant Module
│       ├── consultant_pages/           # BasePage, ConsultantPage, FormExecutor
│       ├── test_data/                  # Swarajya-Consultant-test-cases.xlsx
│       └── tests/                      # Positive & Negative Consultant Creation Tests
│
├── update/                             # 🔄 Master Update Operations Suite (Partner Module)
│   │
│   ├── emp_mgmt/                       # 📝 Update Employee Module
│       ├── employee_update_page.py     # Page Object for Employee Editing & Patching
│       ├── employee_workbook.py        # Excel Synchronizer for Update Scenarios
│       ├── test_data/                  # Swarajya-Update-Employee-test-cases.xlsx
│       └── tests/                      # test_employee_updates.py
│   
│  
│
├── .gitignore                          # Excludes caches, screenshots & session tokens
├── pytest.ini                          # Root Pytest Configuration & Unified Markers
└── README.md                           # Master Architecture Documentation
```

---

## 📊 Comprehensive Test Coverage Matrix

| Category | Sub-Module | Ownership | Reference Workbook | Execution Mode |
| :--- | :--- | :---: | :--- | :---: |
| **Authentication** | Employee & Manager Login | Himanshu | `login_test_cases.xlsx` | Automated |
| **Authentication** | HR & Admin Login | Mrugank | `login_test_cases_ready.xlsx` | Automated |
| **Create Operations** | Employee Management | Himanshu | `Swarajya-Create-test-cases (6).xlsx` | Automated |
| **Create Operations** | Vendor Management | Himanshu | `Create-Vendor-Management.xlsx` | Automated |
| **Create Operations** | Consultant Management | Mrugank | `Swarajya-Consultant-test-cases.xlsx` | Automated |
| **Update Operations** | Employee Updates | Mrugank | `Swarajya-Update-Employee-test-cases.xlsx` | Automated |

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

### 1. Run Vendor Management
```powershell
cd swarajya-create\vendor-management
pytest
```

### 2. Run Employee Management
```powershell
cd swarajya-create\employee-management
pytest
```

### 3. Run Login Authentication Suite
```powershell
cd swarajya-login\swarajya-automation
pytest
```

### 4. Run Update Employee Suite (Partner Module)
```powershell
cd update\emp_mgmt
pytest
```
