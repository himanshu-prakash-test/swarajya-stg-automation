# 🚀 Swarajya Staging Automation Framework

An enterprise-grade, data-driven test automation framework for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), built with **Python 3.12+**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 📁 Repository Structure & Modules

```
├── shared/                             # 🌐 Centralized Core Framework & Test Data
│   ├── config/                         # Central configuration & selectors
│   ├── pages/                          # Shared BasePage, LoginPage, TfaPage
│   ├── test_data/                      # Centralized Excel workbooks & sample documents
│   └── utils/                          # Logging, Excel readers, popup reporting
│
├── swarajya-create/
│   ├── employee-management/            # 👤 Create Employee Management Module
│   │   ├── emp_pages/                  # Page Object Model Layer (EmployeePage, FormExecutor)
│   │   ├── emp_utils/                  # Excel loaders & test case sync
│   │   ├── tests/                      # Parametrized positive & negative test suites
│   │   └── pytest.ini                  # Module-level configuration
│   │
│   └── vendor-management/              # 🏢 Create Vendor Management Module
│       ├── vendor_pages/               # Page Object Model Layer (VendorPage, FormExecutor)
│       ├── vendor_utils/               # Excel loaders & test case sync
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

### 1. Run Create Vendor Management Tests
```bash
pytest swarajya-create/vendor-management/tests -v
```

### 2. Run Create Employee Management Tests
```bash
pytest swarajya-create/employee-management/tests -v
```

### 3. Run Employee & Manager Login Tests
```bash
pytest swarajya-login/emp-manager/tests -v
```

### 4. Browser Options & HTML Reports
```bash
# Run in headed mode
pytest --headed

# Run with HTML report output
pytest --html=reports/latest_report.html --self-contained-html
```
