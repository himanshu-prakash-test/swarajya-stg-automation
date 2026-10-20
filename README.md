# 🚀 Swarajya Staging Automation Framework

An enterprise-grade, data-driven test automation framework for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), built with **Python 3.12+**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 📁 Repository Structure & Modules

```
swarajya-stg-automation/
│
├── shared/                             # 🌐 Centralized Core Framework & Test Data
│   ├── config/                         # Central configuration & selectors
│   ├── pages/                          # Shared BasePage, LoginPage, TfaPage
│   ├── test_data/                      # Centralized Excel workbooks & sample documents
│   └── utils/                          # Logging, Excel readers, popup reporting
│
├── swarajya-create/
│   └── employee-management/            # 👤 Create Employee Management Module
│       ├── emp_pages/                  # Page Object Model Layer (EmployeePage, FormExecutor)
│       ├── emp_utils/                  # Excel loaders & test case sync
│       ├── tests/                      # Parametrized positive & negative test suites
│       └── pytest.ini                  # Module-level configuration
│
├── swarajya-login/
│   └── emp-manager/                    # 🔐 Employee & Manager Authentication Module
│       ├── tests/                      # Role-based positive & negative authentication flows
│       └── pytest.ini                  # Module-level configuration
│
├── conftest.py                         # Root Pytest fixtures, sys.path & CLI options
├── pytest.ini                          # Root testpaths, discovery & logging config
└── requirements.txt                    # Project dependencies
```

---

## 🏃 Test Execution Guide

### 1. Run All Tests Across Modules
```bash
pytest -v
```

### 2. Run Create Employee Management Tests
```bash
# Run all Employee Management create tests
pytest swarajya-create/employee-management/tests -v

# Run positive flows only
pytest swarajya-create/employee-management/tests/test_emp_positive_flows.py -v

# Run negative flows only
pytest swarajya-create/employee-management/tests/test_emp_negative_flows.py -v
```

### 3. Run Employee & Manager Login Tests
```bash
# Run all Login tests
pytest swarajya-login/emp-manager/tests -v

# Run positive flows only
pytest swarajya-login/emp-manager/tests/positive_flows.py -v

# Run negative flows only
pytest swarajya-login/emp-manager/tests/negative_flows.py -v
```

### 4. Browser Options & HTML Reports
```bash
# Run in headed mode
pytest --headed

# Run with HTML report output
pytest --html=reports/latest_report.html --self-contained-html
```
