# 🚀 Swarajya Staging Automation Framework

Production-grade, data-driven test automation framework powered by **Playwright (Python)** and **Pytest** for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/).

---

## 🏗️ Master Architecture Overview

The repository is modularized into distinct test suites with strict Page Object Model (POM) separation and independent namespacing to prevent naming collisions:

```
swarajya-stg-automation/
│
├── swarajya-login/                     # 🔐 Authentication & Session Suite (39 Tests)
│   └── swarajya-automation/
│       ├── pages/                      # LoginPage, TFAPage
│       ├── utils/                      # Excel I/O, Logging, Tkinter Popup
│       ├── test_data/                  # login_test_cases.xlsx, credentials.xlsx
│       ├── tests/                      # test_login.py (UI, Positive, Negative, 2FA, Security)
│       ├── conftest.py                 # Fixtures, 1-to-1 Screenshots & Auto-Cleanup
│       └── pytest.ini
│
├── swarajya-create/                    # 📋 Master Create Operations Suite (52 Tests)
│   │
│   ├── employee-management/            # 👤 Employee Management Module (27 Tests)
│   │   ├── emp_pages/                  # BasePage, LoginPage, EmployeePage, FormExecutor
│   │   ├── emp_utils/                  # Excel Reader, Logger, Popup Dialog
│   │   ├── test_data/                  # Swarajya-Create-test-cases (6).xlsx, credentials.xlsx
│   │   ├── tests/                      # test_emp_login_flow.py, test_emp_positive_flows.py, test_emp_negative_flows.py
│   │   ├── conftest.py                 # Employee Fixtures, 1-to-1 Screenshots & Auto-Cleanup
│   │   └── pytest.ini
│   │
│   └── vendor-management/              # 🏢 Vendor Management Module (25 Tests)
│       ├── vendor_pages/               # BasePage, LoginPage, VendorPage, FormExecutor
│       ├── vendor_utils/               # Excel Reader, Logger, Popup Dialog
│       ├── test_data/                  # Create-Vendor-Management.xlsx, credentials.xlsx
│       ├── tests/                      # test_vendor_login_flow.py, test_vendor_positive_flows.py, test_vendor_negative_flows.py
│       ├── conftest.py                 # Vendor Fixtures, Offline Network Mocks, Screenshots
│       └── pytest.ini
│
├── .gitignore                          # Excludes caches, temp media, screenshots & session tokens
├── pytest.ini                          # Root Pytest Configuration & Unified Markers
└── README.md                           # Master Documentation
```

---

## 📊 Test Suite Coverage Matrix

| Module | Suite Directory | Active Tests | Test Case Reference File | Scope |
| :--- | :--- | :---: | :--- | :--- |
| **Authentication** | `swarajya-login/swarajya-automation` | **39** | `login_test_cases.xlsx` | UI, Positive 2FA, Negative Creds, SQLi/XSS, Session Expiry |
| **Employee Mgmt** | `swarajya-create/employee-management` | **27** | `Swarajya-Create-test-cases (6).xlsx` | Positive Creation, Negative Field Validations, Dropdowns, Grid |
| **Vendor Mgmt** | `swarajya-create/vendor-management` | **25** | `Create-Vendor-Management.xlsx` | Full Form, Inactive Toggle, Boundary/Length, Offline Network Simulation |
| **Total Automated**| **Entire Workspace** | **91 Tests** | *(Excel Driven)* | **100% End-to-End Automated** |

---

## ⚡ Key Framework Capabilities

1. **100% Dynamic Synchronization (Zero Arbitrary Sleeps)**:
   - Uses event-driven Playwright assertions (`wait_for(state="visible")`, `wait_for_dom_ready()`, `wait_for_url()`).
2. **Bi-Directional Excel Reporting**:
   - Reads inputs dynamically from Excel and writes back real-time execution results (`PASS` / `FAIL`), `AUT_*` Script IDs, and detailed timestamps.
3. **1-to-1 Screenshot Audit & Auto-Retention**:
   - Automatically saves 1 screenshot per test case named `{STATUS}_{TC_ID}__{TIMESTAMP}.png`.
   - **Auto-Cleanup**: Automatically purges screenshots older than 24 hours and caps folder size (max 60 files) to save disk space.
4. **Interactive Desktop Summary Popup**:
   - Styled desktop dialog appears at the end of each session showing Total, Passed, Failed, Skipped, and Duration.
5. **Network Simulation & Security Testing**:
   - Simulates offline/server downtime with `context.set_offline(True)` for `TC_VENDOR_NEG_14`.
   - Validates resistance against SQL Injection, XSS payloads, and session cookie hijacking.

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Google Chrome / Chromium

### 2. Clone & Install Dependencies
```powershell
# Navigate to repository root
cd swarajya-stg-automation

# Optional: Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies and Playwright browsers
pip install pytest pytest-html openpyxl playwright
playwright install chromium
```

---

## 🚀 Test Execution Guide

### Run Everything Across All Suites (91 Tests)
```powershell
pytest swarajya-login/swarajya-automation swarajya-create/employee-management swarajya-create/vendor-management
```

### Run by Specific Module

#### 1. Vendor Management Suite
```powershell
cd swarajya-create\vendor-management
pytest                                  # Run all 25 vendor tests (headless)
pytest --headed                         # Run with visible browser
pytest -m positive                      # Positive vendor flows only
pytest -m negative                      # Negative validation flows only
```

#### 2. Employee Management Suite
```powershell
cd swarajya-create\employee-management
pytest                                  # Run all 27 employee tests (headless)
pytest --headed                         # Run with visible browser
pytest -m positive                      # Positive employee flows only
pytest -m negative                      # Negative validation flows only
```

#### 3. Login Suite
```powershell
cd swarajya-login\swarajya-automation
pytest                                  # Run all 39 login tests
pytest -m smoke                         # Core smoke tests
pytest -m security                      # SQLi, XSS, and session tests
```

---

## 🛡️ Git & Contribution Guidelines

1. **Avoid Merge Conflicts**:
   - All runtime caches (`.pytest_cache/`, `__pycache__/`, `auth_state.json`) are gitignored.
2. **Branch Naming**:
   - Use descriptive branch names like `create/employee-mgmt`, `create/vendor-mgmt`, or `features/<feature-name>`.
3. **Always Rebase**:
   - Before merging into `main`, run `git fetch origin` and `git rebase origin/main` for a clean, linear commit history.
