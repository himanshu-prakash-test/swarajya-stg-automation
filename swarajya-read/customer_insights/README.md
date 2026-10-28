# 📊 Swarajya Customer Insights API Automation

Automated REST API test suite for the **Read / Customer Insights** module of Swarajya ERP.

Driven strictly by the shared Excel workbooks with **ZERO hardcoding**:
- **Test Definitions & Cases**: `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `readcustomer_insights`]
- **Test Inputs & Credentials**: `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `readcustomer_insights`]

---

## 📁 Architecture & Directory Structure

```
swarajya-read/customer_insights/
├── conftest.py                       # Fixtures, CLI options, dynamic wait, bi-directional Excel reporter hook
├── pytest.ini                        # Pytest configuration and marker declarations
├── requirements.txt                  # Python dependencies
├── README.md                         # Documentation and run instructions
├── customer_insights_api/            # Core API testing layer
│   ├── __init__.py
│   ├── api_client.py                 # REST client with dynamic wait, timing, retry, and error handling
│   ├── auth.py                       # Dynamic JWT Bearer token resolver and login manager
│   └── assertions.py                 # Deep domain assertions (revenue metrics, periods, sorting, zero-data)
├── customer_insights_utils/          # Data providers and Excel sync
│   ├── __init__.py
│   └── excel_reader.py               # Bi-directional Excel loader, endpoint resolver & results updater
└── tests/                            # Automated test suites
    ├── __init__.py
    ├── test_customer_insights_positive.py     # Positive flows (6 cases)
    ├── test_customer_insights_negative.py     # Negative flows (2 cases)
    └── test_customer_insights_data_driven.py  # Parameterized Excel row runner
```

---

## 🎯 Test Scenarios Covered

| Test Case ID | Category | Scenario / Assertion Focus | Endpoint |
|---|---|---|---|
| `TC_CUST_INS_API_POS_01` | Positive | Retrieve Customer Revenue Insights for Current Fiscal Year (CFY) | `GET {{base_url}}/{{actual_revenue_endpoint}}?period=CFY` |
| `TC_CUST_INS_API_POS_02` | Positive | Filter Revenue Data by Fiscal Period (CFY, 2FY, 3FY, 5FY) | `GET {{base_url}}/{{actual_revenue_endpoint}}?period={{period}}` |
| `TC_CUST_INS_API_POS_03` | Positive | Validate Customer Revenue Against Trusted Data (`TD_CUST_05`, INR) | `GET {{base_url}}/{{actual_revenue_endpoint}}?period=CFY` |
| `TC_CUST_INS_API_POS_04` | Positive | Verify Revenue Sorting (Descending Order `revenue[i] >= revenue[i+1]`) | `GET {{base_url}}/{{actual_revenue_endpoint}}?period=CFY` |
| `TC_CUST_INS_API_POS_05` | Positive | Handle Customer with Zero Revenue (Numeric `0.00` representation) | `GET {{base_url}}/{{actual_revenue_endpoint}}?period=CFY` |
| `TC_CUST_INS_API_POS_06` | Positive | Handle Empty Revenue Results (`[]` collection, total 0.00, count 0) | `GET {{base_url}}/{{actual_revenue_endpoint}}?period={{supported_empty_period}}` |
| `TC_CUST_INS_API_NEG_01` | Negative | Reject Invalid Fiscal Period (HTTP 400 / 422, error schema) | `GET {{base_url}}/{{actual_revenue_endpoint}}?period=INVALID` |
| `TC_CUST_INS_API_NEG_02` | Negative | Reject Malformed or Invalid Query Parameters (HTTP 400, no stack trace) | `GET {{base_url}}/{{actual_revenue_endpoint}}?period=CFY&startDate=...` |

---

## 🚀 Running the Tests Locally

Execute commands from the workspace root or inside the `swarajya-read/customer_insights` directory:

### 1. Run All Customer Insights Tests
```bash
pytest swarajya-read/customer_insights/tests -v
```

### 2. Run Only Positive Flows
```bash
pytest swarajya-read/customer_insights/tests/test_customer_insights_positive.py -v
```

### 3. Run Only Negative Flows
```bash
pytest swarajya-read/customer_insights/tests/test_customer_insights_negative.py -v
```

### 4. Run Data-Driven Parameterized Suite
```bash
pytest swarajya-read/customer_insights/tests/test_customer_insights_data_driven.py -v
```

### 5. Generate Standalone HTML Report
```bash
pytest swarajya-read/customer_insights/tests --html=reports/read_customer_insights.html --self-contained-html
```

---

## 📊 Bi-Directional Excel Synchronization

During execution, `conftest.py` automatically writes execution results directly back to:
- `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `readcustomer_insights`]
- `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `readcustomer_insights`]

Updates include:
- Status: **`PASS`** (Green cell), **`FAIL`** (Red cell), or **`SKIPPED`** (Yellow cell)
- Remarks / Defect Observed: Detailed failure traceback or assertion confirmation
- Auto Script ID: Formatted ID (e.g. `AUT_CUST_INS_POS_01`, `AUT_CUST_INS_NEG_01`)
