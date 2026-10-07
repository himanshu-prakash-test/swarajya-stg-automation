# 🔐 Swarajya Login Automation Framework — HR & Admin Module

An enterprise-grade, data-driven test automation framework for the **Authentication & 2FA** workflows of the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), specifically covering **Admin** and **HR** roles. Built using **Python**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 🏛️ Module Architecture

```
swarajya-login/
│
├── common/                              # Shared Layer for Login Modules
│   ├── pages/                           # Page Object Model (POM) Layer
│   │   ├── __init__.py
│   │   ├── login_page.py                # Login form interactions, error toasts, resilient waits
│   │   └── tfa_page.py                  # Google Authenticator 2FA code submission & validation
│   └── utils/                           # Utilities Layer
│       ├── __init__.py
│       └── excel_reader.py              # Dynamic reader & live Excel result updater for shared test data
│
├── hr_admin/                            # Admin & HR Authentication Sub-module
│   ├── conftest.py                      # Admin & HR fixtures and lifecycle hooks
│   ├── pytest.ini                       # Sub-module test runner settings
│   ├── requirements.txt                 # Dependencies
│   ├── README.md                        # Sub-module documentation
│   ├── screenshots/                     # Test execution screenshots
│   └── tests/
│       ├── __init__.py
│       ├── positive_flows.py            # 10 Data-Driven Positive Tests (loginhr_admin)
│       └── negative_flows.py            # 29 Data-Driven Negative Tests (loginhr_admin)
│
├── pytest.ini                           # Login runner configuration
└── README.md                            # Documentation
```

---

## ⚡ Core Engineering & Design Standards

### 1. Single Source of Truth (`common/`)
- Page Objects (`LoginPage`, `TfaPage`) and Excel Utilities (`excel_reader.py`) exist centrally in `common/`.
- `hr_admin` consumes directly from `common.pages` and `common.utils`.

### 2. Strictly Zero Hardcoded Values
- Credentials, URLs, and test assertions are loaded dynamically from:
  - `shared/test_data/Swarajya-test-data.xlsx` (`loginhr_admin`)
  - `shared/test_data/Swarajya-test-cases.xlsx` (`loginhr_admin`)

### 3. Bi-Directional Master Excel Reporting
- Synchronizes execution status (`PASS` / `FAIL`), `Automation Status` (`Automated`), and remarks back to `Swarajya-test-cases.xlsx` in real-time.

---

## 🚀 Running Tests

### Run all HR & Admin tests:
```bash
pytest swarajya-login/hr_admin/tests -v
```

### Run only Positive Flows:
```bash
pytest swarajya-login/hr_admin/tests/positive_flows.py -v
```

### Run only Negative Flows:
```bash
pytest swarajya-login/hr_admin/tests/negative_flows.py -v
```

### Run in headed mode:
```bash
pytest swarajya-login/hr_admin/tests --headed
```
