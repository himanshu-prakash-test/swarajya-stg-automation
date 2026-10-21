# 📄 Create Invoice Management Automation Module

Automated test suite for Create Invoice workflows on the Swarajya platform.

## 📁 Module Structure
```
invoice-management/
├── conftest.py                      # Browser fixtures, makereport hooks, Excel updates, guarded popups
├── pytest.ini                       # Testpaths, options, and marker configurations
├── requirements.txt                 # Module dependencies
├── invoice_pages/                   # Page Object Models
│   ├── __init__.py
│   ├── invoice_page.py              # Dashboard & creation form actions
│   └── form_executor.py             # Form filling from dynamic Excel dataset
├── invoice_utils/                   # Data utilities
│   ├── __init__.py
│   └── excel_reader.py              # Wrapper for shared.utils.excel_base
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── test_invoice_positive_flows.py  # 20 Data-driven positive test cases
│   └── test_invoice_negative_flows.py  # 7 Data-driven negative test cases
└── screenshots/                     # 1-to-1 automated run evidence
```

> **Strict Zero-Hardcoding Policy**: All credentials, base URLs, form inputs, test descriptions, and expected outcomes are dynamically fetched from `shared/test_data/Swarajya-test-cases.xlsx` and `Swarajya-test-data.xlsx` (Sheet: `createinvoice-mgmt`).

## 🚀 Execution Commands

```bash
# Run entire Invoice test suite in headless mode (CI/CD compatible)
pytest swarajya-create/invoice-management/tests -v --headless

# Run only positive flows
pytest swarajya-create/invoice-management/tests/test_invoice_positive_flows.py -v --headless

# Run only negative flows
pytest swarajya-create/invoice-management/tests/test_invoice_negative_flows.py -v --headless

# Run in interactive headed mode
pytest swarajya-create/invoice-management/tests -v --headed
```
