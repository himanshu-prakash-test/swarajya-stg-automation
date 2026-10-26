# 🔐 Swarajya Login Automation Framework

An enterprise-grade, data-driven test automation framework for the **Authentication & 2FA** workflows of the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), covering **Admin & HR** and **Employee & Manager** roles. Built using **Python**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 🏛️ Module Architecture

```
swarajya-login/
│
├── hr_admin/                            # Admin & HR Authentication Sub-module
│   ├── conftest.py                      # Admin & HR fixtures and lifecycle hooks
│   ├── pytest.ini                       # Sub-module test runner settings
│   ├── requirements.txt                 # Dependencies
│   ├── README.md                        # Sub-module documentation
│   ├── screenshots/                     # Test execution screenshots
│   └── tests/
│       ├── __init__.py
│       ├── positive_flows.py            # 10 Data-Driven Positive Tests (Sheet: loginhr_admin)
│       └── negative_flows.py            # 29 Data-Driven Negative Tests (Sheet: loginhr_admin)
│
├── emp-manager/                         # Employee & Manager Authentication Sub-module
│   ├── conftest.py                      # Employee & Manager fixtures and lifecycle hooks
│   ├── pytest.ini                       # Sub-module test runner settings
│   ├── requirements.txt                 # Dependencies
│   ├── README.md                        # Sub-module documentation
│   ├── screenshots/                     # Test execution screenshots
│   └── tests/
│       ├── __init__.py
│       ├── positive_flows.py            # 13 Data-Driven Positive Tests (Sheet: loginemp-manager)
│       └── negative_flows.py            # 9 Data-Driven Negative Tests (Sheet: loginemp-manager)
│
├── pytest.ini                           # Login root runner configuration
└── README.md                            # Documentation
```

---

## ⚡ Core Engineering & Design Standards

### 1. Single Source of Truth (`shared/`)
- Page Objects (`LoginPage`, `TfaPage`) and Excel Utilities (`excel_base.py`) exist centrally in root `shared/`.
- Both `hr_admin` and `emp-manager` sub-modules consume directly from `shared.pages` and `shared.utils`.

### 2. Strictly Zero Hardcoded Values
- Credentials, URLs, and test assertions are loaded dynamically from:
  - `shared/test_data/Swarajya-test-data.xlsx` (`loginhr_admin`, `loginemp-manager`)
  - `shared/test_data/Swarajya-test-cases.xlsx` (`loginhr_admin`, `loginemp-manager`)

### 3. Bi-Directional Master Excel Reporting
- Synchronizes execution status (`PASS` / `FAIL`), `Automation Status` (`Automated`), and remarks back to `Swarajya-test-cases.xlsx` in real-time.

---

## 🚀 Running Tests

### Run all Login tests:
```bash
pytest swarajya-login -v
```

### Run HR & Admin tests:
```bash
pytest swarajya-login/hr_admin/tests -v
```

### Run Employee & Manager tests:
```bash
# Run all Employee & Manager tests
pytest swarajya-login/emp-manager/tests -v

# Run only positive flows
pytest swarajya-login/emp-manager/tests/positive_flows.py -v

# Run only negative flows
pytest swarajya-login/emp-manager/tests/negative_flows.py -v

# Run in headed mode
pytest swarajya-login/emp-manager/tests --headed
```

---

## 🔄 CI/CD Pipeline Status
- **Status**: Integrated & Verified ✅
- **Automation Pipeline**: [Swarajya Automation CI/CD Pipeline](https://github.com/himanshu-prakash-test/swarajya-stg-automation/actions)
- **Supported Execution**: Headless and Headed modes via GitHub Actions `workflow_dispatch`.

