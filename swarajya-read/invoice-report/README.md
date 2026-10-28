# Swarajya Invoice Report API Automation

Automated REST API test suite for the **Read / Invoice Report** module of Swarajya ERP.

Driven strictly by the shared Excel workbooks with **ZERO hardcoding**:
- **Test Definitions & Cases**: `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `readinvoice-reports`]
- **Test Inputs & Credentials**: `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `readinvoice-report`]

---

## 📁 Architecture & Directory Structure

```
swarajya-read/invoice-report/
├── conftest.py                       # Fixtures, CLI options, bi-directional Excel reporter hook
├── pytest.ini                        # Pytest configuration and marker declarations
├── requirements.txt                  # Python dependencies
├── README.md                         # Documentation and run instructions
├── invoice_report_api/               # Core API testing layer
│   ├── __init__.py
│   ├── api_client.py                 # REST client with timing, logging, and error handling
│   ├── auth.py                       # Dynamic JWT Bearer token resolver and login manager
│   └── assertions.py                 # Deep assertions (metrics, zero-data, reconciliation, precision)
├── invoice_report_utils/             # Data providers and Excel sync
│   ├── __init__.py
│   └── excel_reader.py               # Bi-directional Excel loader & results updater
└── tests/                            # Automated test suites (Split into Separate Folders)
    ├── __init__.py
    ├── positive/                     # Positive flows folder
    │   ├── __init__.py
    │   └── test_invoice_reports_positive.py
    ├── negative/                     # Negative flows folder
    │   ├── __init__.py
    │   └── test_invoice_reports_negative.py
    └── data_driven/                  # Parameterized runner folder
        ├── __init__.py
        └── test_invoice_reports_data_driven.py
```

---

## 🎯 Test Scenarios Covered

| Test Case ID | Category | Scenario / Assertion Focus | Endpoint |
|---|---|---|---|
| `TC-REP-POS-01` | Positive | Fetch Annual Invoice Summary Metrics for Current FY (2026-2027) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-POS-02` | Positive | Status Filter Constraint for Finalized Invoices & Total Reconciliation | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-POS-03` | Positive | Monthly Breakdown with Zero-Data Future Period Validation (0.00) | `GET /api/v1/invoice-reports/monthly-breakdown` |
| `TC-REP-POS-04` | Positive | Dynamic Historical Financial Year Filtering (FY 2025-2026) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-POS-05` | Positive | Retrieval of Active Financial Years Dropdown / Customer Filter | `GET /api/v1/invoice-reports/financial-years` |
| `TC-REP-POS-06` | Positive | Drill-Down Line-Item Reconciliation / Paid vs Outstanding | `GET /api/v1/invoices/outstanding` |
| `TC-REP-POS-07` | Positive | Floating-Point Decimal Precision (2-decimal) / Line-Item Details | `GET /api/v1/invoice-reports/details` |
| `TC-REP-NEG-01` | Negative | Malformed Financial Year Parameter Format (HTTP 400) | `GET /api/v1/invoice-reports/summary?financial_year=...` |
| `TC-REP-NEG-02` | Negative | Missing Mandatory Financial Year Query Parameter (HTTP 400) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-NEG-03` | Negative | Unauthorized Access via Missing Authentication Token (HTTP 401) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-NEG-04` | Negative | Forbidden Access via Low-Privilege Role Restriction (HTTP 403) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-NEG-05` | Negative | SQL Injection Query Parameter Sanitization / Metadata Failure | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-NEG-06` | Negative | Boundary Handling for Zero Overdue Items / Service Unavailable (503) | `GET /api/v1/invoices/outstanding` |

---

## 🚀 Running the Tests

From the workspace root or the `swarajya-read/invoice-report` folder:

### 1. Run All Tests
```powershell
pytest swarajya-read/invoice-report/tests -v
```

### 2. Run Only Positive Flows
```powershell
pytest swarajya-read/invoice-report/tests/test_invoice_reports_positive.py -v
```

### 2. Run Only Positive Flows
```powershell
pytest swarajya-read/invoice-report/tests/positive -v
```

### 3. Run Only Negative Flows
```powershell
pytest swarajya-read/invoice-report/tests/negative -v
```

### 4. Run Data-Driven Parameterized Suite
```powershell
pytest swarajya-read/invoice-report/tests/data_driven -v
```

### 5. Generate Standalone HTML Report
```powershell
pytest swarajya-read/invoice-report/tests --html=reports/read_invoice_report.html --self-contained-html
```

---

## 📊 Bi-Directional Excel Synchronization

When the tests run, the `conftest.py` hook automatically writes execution results directly back to:
- `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `readinvoice-reports`]
- `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `readinvoice-report`]

Updates include:
- Status: **`PASS`** (Green cell), **`FAIL`** (Red cell), or **`SKIPPED`** (Yellow cell)
- Remarks / Defect Observed: Detailed failure traceback or assertion confirmation
- Auto Script ID: Formatted ID (e.g. `AUT_REP_POS_01`, `AUT_REP_NEG_03`)

