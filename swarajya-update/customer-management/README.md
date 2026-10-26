# 📝 Swarajya Customer Update Management Automation Suite

Production-grade automated end-to-end test suite for **Customer Update Management** in the Swarajya Staging Portal, powered by **Playwright (Python)** and **Pytest**.

Strictly adheres to the standardized framework architecture established in `swarajya-update/invoice-management`.

---

## 🏛️ Module Architecture

```
swarajya-update/customer-management/
├── customer_update_pages/                 # Page Object Model (POM) Layer
│   ├── __init__.py
│   ├── customer_update_page.py            # Customer grid, search, row edit modal/form, 20+ field locators & actions
│   └── form_executor.py                   # Data-driven workflow engine for positive & negative updates
│
├── customer_update_utils/                 # Framework Utilities
│   ├── __init__.py
│   └── excel_reader.py                    # Test case loader, test data reader, baseline customer loader, and result writer
│
├── tests/                                 # Test Execution Suites
│   ├── __init__.py
│   ├── test_customer_update_login_flow.py     # Authentication, multi-step navigation & form controls sanity
│   ├── test_customer_update_positive_flows.py  # Data-driven positive customer update scenarios (32 cases)
│   └── test_customer_update_negative_flows.py  # Data-driven negative validation scenarios (16 cases)
│
├── screenshots/                           # 1-to-1 Test Evidence Screenshots (PASS / FAIL)
├── conftest.py                            # Session fixtures, storage caching, 503 resilience, reporting hooks & popup
├── pytest.ini                             # Pytest execution configuration & test markers
├── requirements.txt                       # Python dependencies
└── README.md                              # Comprehensive Module Manual
```

---

## 🎯 Core Framework Principles

1. **Strict Zero Hardcoding**:
   - Test cases dynamically loaded from `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `updatecustomer_mgmt`].
   - Test data dynamically loaded from `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `updatecustomer_mgmt`].
   - Staging portal Base URL and Admin credentials dynamically resolved from Excel test data banner headers.
2. **Event-Driven Dynamic Waits**:
   - Zero static sleeps (`time.sleep`).
   - Angular reactive form hydration synchronization, URL transition waits, and dynamic DOM state verifications.
   - Exponential backoff resilience against transient staging 503 Service Unavailable spikes.
3. **Smart Session Reuse**:
   - Authenticates once as Admin dynamically via `LoginPage` and reuses cached session storage across test runs.
4. **Clean Baseline Protection**:
   - Negative validation scenarios cancel/discard changes cleanly to ensure existing staging customer records are preserved.

---

## 🗺️ Navigation Workflow

The Customer Update operation follows the multi-step navigation path:
1. **Default Dashboard**: Authenticates and lands on `/default`.
2. **Invoicing Reports**: Clicks `Invoicing` -> navigates to `/invoiceReports`.
3. **Invoice Home**: Clicks `Invoice Home` -> navigates to `/invoicedashboard`.
4. **Customer Details**: Clicks `Customers` card -> opens `/customerDetails`.
5. **Row Selection & Edit**: Locates target customer row, clicks edit pencil icon, and opens update modal form with all 20+ fields.

---

## 🚀 Execution Commands

Run from the `swarajya-update/customer-management` directory:

### 1. Run Complete Customer Update Suite
```bash
pytest
```

### 2. Run in Headless Mode
```bash
HEADLESS=1 pytest
```

### 3. Run Specific Test Suites
```bash
# Login and navigation workflow sanity
pytest tests/test_customer_update_login_flow.py

# Positive update flows
pytest tests/test_customer_update_positive_flows.py

# Negative validation flows
pytest tests/test_customer_update_negative_flows.py
```

---

## 📊 Reporting & Evidence
- **Screenshots**: Automatically saved in `screenshots/` on PASS and FAIL with test case ID and timestamp.
- **HTML Report**: Generated automatically in `reports/latest_report.html` with step timings and embedded screenshots.
- **Excel Report**: Live test execution status (`PASS` / `FAIL` / `SKIPPED`) and execution duration written back to master `Swarajya-test-cases.xlsx`.
- **Desktop Summary Popup**: Styled desktop execution summary dialog with pass/fail counts and quick report launcher.

---

## 🔄 CI/CD Pipeline Status
- **Status**: Integrated & Verified ✅
- **Automation Pipeline**: [Swarajya Automation CI/CD Pipeline](https://github.com/himanshu-prakash-test/swarajya-stg-automation/actions)
- **Supported Execution**: Headless and Headed modes via GitHub Actions `workflow_dispatch`.

