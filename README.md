# 🚀 Swarajya Staging Automation Master Framework

Production-grade, end-to-end test automation framework powered by **Playwright (Python)** and **Pytest** for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/).

---

## 👥 Team Module Ownership & Division of Responsibilities

| Contributor / Scope | Modules Covered | Branches | Key Areas & Test Artifacts |
| :--- | :--- | :--- | :--- |
| **Himanshu** | • **Login Suite** (Employee & Manager)<br>• **Create Employee** Module<br>• **Create Vendor** Module | `create/employee-mgmt`<br>`features/himanshu` | • `login_test_cases.xlsx`<br>• `Swarajya-Create-test-cases (6).xlsx`<br>• `Create-Vendor-Management.xlsx`<br>• Dynamic Waits, Network Offline Mocks |
| **Partner (Mrugank)** | • **HR / Admin Login** Suite<br>• **Update Employee** Module<br>• **Consultant Management** Module | `update_emp_mgmt`<br>`features/mrugank` | • `test_hr_admin.py`<br>• `Swarajya-Update-Employee-test-cases.xlsx`<br>• Update Form Validation, Consultant Flows |

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
│   ├── employee-management/            # 👤 Create Employee Module (27 Tests)
│   │   ├── emp_pages/                  # BasePage, LoginPage, EmployeePage, FormExecutor
│   │   ├── emp_utils/                  # Excel Reader, Logger, Popup
│   │   ├── test_data/                  # Swarajya-Create-test-cases (6).xlsx
│   │   └── tests/                      # test_emp_positive_flows.py, test_emp_negative_flows.py
│   │
│   └── vendor-management/              # 🏢 Create Vendor Module (25 Tests)
│       ├── vendor_pages/               # BasePage, LoginPage, VendorPage, FormExecutor
│       ├── vendor_utils/               # Excel Reader, Logger, Popup
│       ├── test_data/                  # Create-Vendor-Management.xlsx
│       └── tests/                      # test_vendor_positive_flows.py, test_vendor_negative_flows.py
│
├── update/                             # 🔄 Master Update Operations Suite (Partner Module)
│   │
│   ├── emp_mgmt/                       # 📝 Update Employee Module
│   │   ├── employee_update_page.py     # Page Object for Employee Editing & Patching
│   │   ├── employee_workbook.py        # Excel Synchronizer for Update Scenarios
│   │   ├── test_data/                  # Swarajya-Update-Employee-test-cases.xlsx
│   │   └── tests/                      # test_employee_updates.py
│   │
│   └── consultant-management/          # 💼 Consultant Management Module
│       ├── consultant_pages/           # Consultant Profile & Contract Updaters
│       ├── test_data/                  # Swarajya-Consultant-test-cases.xlsx
│       └── tests/                      # test_consultant_management.py
│
├── .gitignore                          # Excludes caches, temp media, screenshots & session tokens
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
| **Update Operations** | Employee Updates | Mrugank | `Swarajya-Update-Employee-test-cases.xlsx` | Automated |
| **Consultant Mgmt** | Consultant Management | Mrugank | `Swarajya-Consultant-test-cases.xlsx` | Automated |

---

## ⚡ Core Engineering & Quality Standards

1. **100% Dynamic Synchronization (Zero Arbitrary Sleeps)**:
   - Event-driven Playwright assertions (`wait_for(state="visible")`, `wait_for_dom_ready()`, `wait_for_url()`).
2. **Bi-Directional Excel Reporting**:
   - Reads inputs dynamically from Excel and writes back real-time execution results (`PASS` / `FAIL`), `AUT_*` IDs, and timestamps.
3. **1-to-1 Screenshot Audit & Auto-Retention**:
   - Captures exactly 1 screenshot per test case (`{STATUS}_{TC_ID}__{TIMESTAMP}.png`).
   - Automatically purges screenshots older than 24 hours and caps folder size (max 60 files).
4. **Desktop Summary Dialogs**:
   - Instant Tkinter popup summary displaying execution metrics (Total, Passed, Failed, Duration) at the end of each session.
5. **Network Mocking & Security Payloads**:
   - Simulates offline/server outages (`context.set_offline(True)`).
   - Validates boundary checks, SQL Injection, and XSS sanitization.

---

## 🚀 Execution Commands

### 1. Create Operations (Employee & Vendor)
```powershell
# Run Vendor Management
cd swarajya-create\vendor-management
pytest

# Run Employee Management
cd swarajya-create\employee-management
pytest
```

### 2. Update Operations (Employee & Consultant)
```powershell
# Run Employee Update Suite
cd update\emp_mgmt
pytest tests/test_employee_updates.py

# Run Consultant Management Suite
cd update\consultant-management
pytest
```

### 3. Login Suites (Role-Based)
```powershell
# General & Employee/Manager Login
cd swarajya-login\swarajya-automation
pytest

# HR & Admin Login
pytest tests/test_hr_admin.py
```

---

## 🛡️ Git & Merge Conflict Prevention
* **Ignored Runtime Artifacts**: `.pytest_cache/`, `__pycache__/`, `screenshots/*.png`, and `auth_state.json` are strictly excluded in `.gitignore`.
* **Namespaced Packages**: `emp_pages/`, `vendor_pages/`, and `pages/` ensure zero module name collisions across branches.
* **Rebase Strategy**: Always run `git fetch origin` and `git rebase origin/main` before merging pull requests to guarantee a clean, linear commit graph.
