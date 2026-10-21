# 🚀 Swarajya Staging Automation Framework

An enterprise-grade, data-driven test automation framework for the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), built with **Python 3.12+**, **Playwright**, **Pytest**, and **OpenPyXL**.

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
│   ├── invoice-management/             # 📄 Create Invoice Management Module (27 tests)
│   ├── customer-management/            # 👥 Create Customer Management Module (44 tests)
│   ├── employee-management/            # 👤 Create Employee Management Module (34 tests)
│   └── vendor-management/              # 🏢 Create Vendor Management Module (42 tests)
│
├── swarajya-update/
│   └── purchase-orders/                # 📦 Update Purchase Orders Module (31 tests)
│       ├── po_update_pages/            # Page Object Model Layer (POUpdatePage, FormExecutor)
│       ├── po_update_utils/            # Centralized Excel Parsers & Writeback
│       └── tests/                      # Parametrized positive & negative test suites
│
├── swarajya-login/
│   └── emp-manager/                    # 🔐 Employee & Manager Authentication Module (24 tests)
│
├── conftest.py                         # Root Pytest fixtures, sys.path & CLI options
├── pytest.ini                          # Root testpaths, discovery & logging config
└── requirements.txt                    # Project dependencies
```

---

## 🏃 Running Tests

```bash
# Run all Purchase Order update tests (31 tests)
pytest swarajya-update/purchase-orders/tests -v

# Run with HTML report
pytest swarajya-update/purchase-orders/tests -v --html=reports/latest_report.html --self-contained-html

# Run positive flows only
pytest swarajya-update/purchase-orders/tests/test_po_update_positive_flows.py -v

# Run negative flows only
pytest swarajya-update/purchase-orders/tests/test_po_update_negative_flows.py -v

# Run in interactive headed mode
pytest swarajya-update/purchase-orders/tests -v --headed
```
