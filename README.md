# 🚀 Swarajya Staging Automation Framework

An enterprise-grade, data-driven test automation framework for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), built with **Python 3.12+**, **Playwright**, **Pytest**, and **OpenPyXL**.

> **Branch:** `create/invoice-mgmt`  
> **Master Repository:** [Switch to main branch](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/main)

---

## 📁 Repository Structure & Modules

```
├── shared/                             # 🌐 Centralized Core Framework & Test Data
│   ├── pages/                          # Shared BasePage, LoginPage, TfaPage
│   ├── reporter/                       # HTML Reporter Plugin & Templates
│   ├── test_data/                      # Centralized Excel workbooks & sample documents
│   └── utils/                          # Logging, Excel readers, popup reporting
│
├── swarajya-create/
│   ├── invoice-management/             # 📄 Create Invoice Management Module
│   │   ├── invoice_pages/              # Page Object Model Layer (InvoicePage, FormExecutor)
│   │   ├── invoice_utils/              # Excel loaders & test case sync
│   │   ├── tests/                      # Parametrized positive & negative test suites
│   │   └── pytest.ini                  # Module-level configuration
│   │
│   ├── customer-management/            # 👥 Create Customer Management Module
│   │   ├── customer_pages/             # Page Object Model Layer (CustomerPage, FormExecutor)
│   │   ├── customer_utils/             # Excel loaders & test case sync
│   │   ├── tests/                      # Parametrized positive & negative test suites
│   │   └── pytest.ini                  # Module-level configuration
│   │
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

## 🏃 Running Tests on this Branch

```bash
# Run all Invoice Management tests in headless mode (default on this branch)
pytest -v

# Run with HTML report
pytest --html=reports/latest_report.html --self-contained-html

# Run positive flows only
pytest swarajya-create/invoice-management/tests/test_invoice_positive_flows.py -v

# Run negative flows only
pytest swarajya-create/invoice-management/tests/test_invoice_negative_flows.py -v

# Run in interactive headed mode
pytest --headed
```
