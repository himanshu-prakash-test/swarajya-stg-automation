# 📝 Swarajya Customer Update Automation Suite

Production-grade automated test suite for **Customer Update Operations** in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), powered by **Playwright (Python)** and **Pytest**.

---

## 🏛️ Module Architecture

```
swarajya-update/customer-management/
├── customer_update_pages/                 # Page Object Model (POM) Layer
│   ├── __init__.py
│   ├── login_page.py                      # Session authentication, 2FA OTP, role-based login (Admin)
│   ├── customer_update_page.py            # Customer grid, search, row edit modal/form, field mappings & actions
│   └── form_executor.py                   # Data-driven workflow engine for positive & negative updates
│
├── customer_update_utils/                 # Framework Utilities
│   ├── __init__.py
│   └── excel_reader.py                    # Test case loader from test_data/, credential reader, and Excel reporter
│
├── test_data/                             # Test Data & Session Cache
│   ├── credentials.xlsx                   # Role-based credentials (Admin)
│   ├── auth_state.json                    # Cached Playwright browser authentication state (auto-generated)
│   └── [Your-Test-Cases].xlsx             # User-added master Excel test suite
│
├── tests/                                 # Test Execution Suites
│   ├── __init__.py
│   ├── test_customer_update_login_flow.py     # Authentication & multi-step navigation sanity
│   ├── test_customer_update_positive_flows.py  # Parametrized positive customer update scenarios
│   └── test_customer_update_negative_flows.py  # Parametrized negative validation scenarios
│
├── screenshots/                           # 1-to-1 Test Evidence Screenshots (PASS / FAIL)
├── conftest.py                            # Session fixtures, storage caching, reporting hooks & popup
├── pytest.ini                             # Pytest execution configuration & test markers
├── requirements.txt                       # Python dependencies
└── README.md                              # Comprehensive Module Manual
```

---

## 🗺️ Navigation Workflow

The Customer Update operation follows the 4-step path from the portal dashboard:
1. **Default Dashboard**: Authenticates and lands on [`/default`](https://swarajya-stg.corecotechnologies.com/default).
2. **Invoicing Reports**: Clicks `Invoicing` -> opens [`/invoiceReports`](https://swarajya-stg.corecotechnologies.com/invoiceReports).
3. **Invoice Home**: Clicks `Invoice Home` -> opens [`/invoicedashboard`](https://swarajya-stg.corecotechnologies.com/invoicedashboard).
4. **Customer Details**: Clicks `Customers` card -> lands on [`/customerDetails`](https://swarajya-stg.corecotechnologies.com/customerDetails).
5. **Row Selection & Edit**: Searches for the customer in the table and clicks the edit pencil icon on the target row to open the update form/modal.

---

## 📋 Adding Test Cases in `test_data/`

Place your Excel test case workbook (e.g. `Update-Customer-Management.xlsx` or any `.xlsx` file) inside `swarajya-update/customer-management/test_data/`.

### Expected Sheet Names:
- `Update_Positive_Flows` or `Positive_Flows` (for positive update scenarios)
- `Update_Negative_Flows` or `Negative_Flows` (for negative validation scenarios)

### Expected Columns:
| Column | Description |
| :--- | :--- |
| `Test Case ID` | Unique identifier (e.g., `TC_CUST_UPD_001`) |
| `Scenario` | High-level summary of test case |
| `Test Data` | Key-value pairs separated by newline (e.g., `Customer Name: Acme Corp\nCity: Pune`) |
| `Expected Result` | Expected system response or validation |
| `Test Status` | Updated automatically (`PASS` / `FAIL` / `SKIPPED`) |
| `Auto Script ID` | Generated automation ID (`AUT_TC_CUST_UPD_001`) |
| `Execution_Timestamp` | Timestamp when test finished |
| `Remarks` | Failure message or pass duration |

---

## 🚀 Execution Commands

Run from the `swarajya-update/customer-management` directory:

### 1. Run Complete Customer Update Suite
```bash
pytest
```

### 2. Run Headed (Visible Browser) Mode
```bash
pytest --headed --slowmo=500
```

### 3. Run Specific Test Groups by Marker
```bash
# Smoke / Login & Navigation sanity
pytest -m sanity

# Positive flows
pytest -m positive

# Negative validation flows
pytest -m negative
```

### 4. Custom Excel File Path (Optional)
You can point to a specific test case workbook using an environment variable:
```bash
CUSTOMER_UPDATE_WORKBOOK="/path/to/my_cases.xlsx" pytest
```

---

## 📊 Reporting & Evidence
- **Screenshots**: Automatically saved in `screenshots/` on PASS and FAIL with test case ID and timestamp.
- **HTML Report**: Generated automatically in `reports/` with step timings and embedded screenshots.
- **Excel Report**: Live result status and execution timestamp updated in the test case workbook.
- **Summary Dialog**: Desktop summary popup with execution counts and duration.
