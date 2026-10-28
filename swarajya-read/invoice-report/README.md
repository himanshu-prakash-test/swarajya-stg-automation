# Swarajya Invoice Report API Automation

Automated REST API test suite for the **Read / Invoice Report** module of Swarajya ERP.

Driven strictly by the shared Excel workbooks with **ZERO hardcoding**:
- **Test Definitions & Cases**: `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `readinvoice-reports`] (13 Test Cases)
- **Test Inputs & Credentials**: `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `readinvoice-report`] (13 Test Data Rows)

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
└── tests/                            # Automated test suites (13 Total Tests)
    ├── test_invoice_reports_positive.py  # 7 Positive test scenarios (TC-REP-POS-01 to TC-REP-POS-07)
    └── test_invoice_reports_negative.py  # 6 Negative test scenarios (TC-REP-NEG-01 to TC-REP-NEG-06)
```

---

## 🎯 Test Scenarios Covered (13 Tests Total)

| Test Case ID | Category | Scenario / Assertion Focus | Endpoint |
|---|---|---|---|
| `TC-REP-POS-01` | Positive | Fetch Annual Invoice Summary Metrics for Current FY (2026-2027) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-POS-02` | Positive | Status Filter Constraint for Finalized Invoices & Total Reconciliation | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-POS-03` | Positive | Monthly Breakdown with Zero-Data Future Period Validation (0.00) | `GET /api/v1/invoice-reports/monthly-breakdown` |
| `TC-REP-POS-04` | Positive | Dynamic Historical Financial Year Filtering (FY 2025-2026) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-POS-05` | Positive | Customer-Specific Invoice Report Filter & Active FY Validation | `GET /api/v1/invoice-reports/summary?customer_id=...` |
| `TC-REP-POS-06` | Positive | Invoice Status Filter Dropdown (Paid vs Outstanding) | `GET /api/v1/invoice-reports/summary?status=PAID` |
| `TC-REP-POS-07` | Positive | Invoice Drill-Down Line-Item Reconciliation & Precision | `GET /api/v1/invoice-reports/details?invoice_id=...` |
| `TC-REP-NEG-01` | Negative | Malformed Financial Year Parameter Format (HTTP 400) | `GET /api/v1/invoice-reports/summary?financial_year=...` |
| `TC-REP-NEG-02` | Negative | Missing Mandatory Financial Year Query Parameter (HTTP 400) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-NEG-03` | Negative | Unauthorized Access via Missing Authentication Token (HTTP 401) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-NEG-04` | Negative | Forbidden Access via Low-Privilege Role Restriction (HTTP 403) | `GET /api/v1/invoice-reports/summary` |
| `TC-REP-NEG-05` | Negative | SQL Injection Query Parameter Sanitization | `GET /api/v1/invoice-reports/summary?financial_year=...` |
| `TC-REP-NEG-06` | Negative | Backend Database Timeout / Service Unavailable Resilience (HTTP 503) | `GET /api/v1/invoice-reports/summary` |

---

## 🚀 Running the Tests

From the workspace root or the `swarajya-read/invoice-report` folder:

### 1. Run Complete 13-Test Suite
```powershell
pytest swarajya-read/invoice-report/tests -v
```

### 2. Run Only Positive Flows (7 Tests)
```powershell
pytest swarajya-read/invoice-report/tests/test_invoice_reports_positive.py -v
```

### 3. Run Only Negative Flows (6 Tests)
```powershell
pytest swarajya-read/invoice-report/tests/test_invoice_reports_negative.py -v
```

### 4. Generate Standalone HTML Report
```powershell
pytest swarajya-read/invoice-report/tests --html=reports/read_invoice_report.html --self-contained-html
```

---

## 📊 Bi-Directional Excel Synchronization

When the tests run, the `conftest.py` hook automatically writes execution results directly back to:
- `shared/test_data/Swarajya-test-cases.xlsx` -> `readinvoice-reports`
- `shared/test_data/Swarajya-test-data.xlsx` -> `readinvoice-report`

Features:
- Status formatting (`PASS` in green, `FAIL` in red, `SKIPPED` in yellow)
- Standardized execution IDs: `AUT_REC_REP_001` to `AUT_REC_REP_013`
- Full assertion tracking with durations and timestamps
