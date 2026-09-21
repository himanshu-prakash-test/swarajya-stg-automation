# 📦 Swarajya Purchase Order Create Automation Suite

End-to-end automated test suite for **Purchase Order Creation & Management** in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), covering purchase order creation, form field validations, customer mapping, currency & tax calculations, document uploads, and grid searches.

---

## 🧭 Navigation Workflow

The Purchase Order Create operation follows the portal path:
1. **Authentication**: User logs in with valid credentials & OTP -> lands on [`/default`](https://swarajya-stg.corecotechnologies.com/default).
2. **Invoice Reports**: Navigates from landing screen -> [`/invoiceReports`](https://swarajya-stg.corecotechnologies.com/invoiceReports).
3. **Invoice Home**: Selects Invoice Home -> [`/invoicedashboard`](https://swarajya-stg.corecotechnologies.com/invoicedashboard).
4. **Purchase Orders**: Opens Purchase Order listing directly -> [`/purchaseOrder`](https://swarajya-stg.corecotechnologies.com/purchaseOrder). *(Bypasses `/customerDetails`)*.
5. **Add Purchase Order**: Clicks "Add Purchase Order" / "+ Purchase Order" button -> opens creation modal/form.

---

## 📋 Form Fields Specification (Purchase Order)

| Field Label | Control Name / Selector | Field Type | Requirement | Notes & Validations |
| :--- | :--- | :--- | :---: | :--- |
| **PO Date** | `date` | Date Picker / Text | **Mandatory** | Valid date in `YYYY-MM-DD` or `DD-MM-YYYY` format |
| **PO Reference No** | `refNo` | Text Input | **Mandatory** | Unique PO reference / identifier number |
| **Customer Name** | `poCustomer` | Mat-Select / Dropdown | **Mandatory** | Customer entity mapped from active customers |
| **Authorized By** | `authorizedBy` | Text Input | **Mandatory** | Name of authorizing manager / executive |
| **PO Details** | `poDetails` | Textarea | Optional | Scope, notes, or descriptions of the PO |
| **Base Amount** | `poBaseAmount` | Numeric Input | **Mandatory** | Base amount before taxes |
| **Tax Amount** | `poTaxAmount` | Numeric Input | Optional | Calculated or entered tax amount |
| **Total Amount** | `poTotalAmount` | Numeric Input | **Mandatory** | Final total value of PO |
| **Currency** | `poCurrency` | Mat-Select / Dropdown | **Mandatory** | Operational currency (INR, USD, EUR, etc.) |
| **Status** | `poStatus` | Mat-Select / Dropdown | **Mandatory** | Status (Draft, Pending, Approved, etc.) |
| **PO Document** | `po_document_url` | File Input (PDF) | Optional | Supporting PO document upload |

---

## 🏛️ Directory Structure

```
swarajya-create/purchase-order/
│
├── po_pages/                            # Page Object Model & Execution Layer
│   ├── __init__.py                      # Package exports (POPage, FormExecutor, LoginPage)
│   ├── po_page.py                       # Purchase order listing, navigation, form controls, modals
│   ├── form_executor.py                 # Data-driven test dispatcher & assertion engine
│   └── login_page.py                    # 2FA-compliant authentication
│
├── po_utils/                            # Utilities & Data Parsers
│   ├── __init__.py                      # Package exports
│   └── excel_reader.py                  # Dynamic Excel parser for test cases & credentials
│
├── test_data/                           # Test Assets & Credentials
│   ├── credentials.xlsx                 # Multi-role credentials (Admin, Manager, Employee)
│   ├── sample_po.pdf                    # Sample PDF file for document upload tests
│   └── (Your PO test cases .xlsx)       # Place your test cases Excel file here
│
├── tests/                               # Test Suites
│   ├── __init__.py
│   ├── test_po_login_flow.py            # Authentication and navigation traversal tests
│   ├── test_po_positive_flows.py        # Data-driven positive test scenarios
│   └── test_po_negative_flows.py        # Data-driven negative / validation test scenarios
│
├── screenshots/                         # Timestamped visual evidence (PASS/FAIL/SKIP)
├── reports/                             # Custom HTML test reports generated per run
├── conftest.py                          # Session fixtures, hooks, evidence capture, reporter
├── pytest.ini                           # Pytest configuration and markers
├── requirements.txt                     # Dependencies
└── README.md                            # Documentation
```

---

## 🚀 Running Tests

Run from within `swarajya-create/purchase-order`:

```bash
# Run all tests headlessly
pytest

# Run in headed mode (visible browser)
pytest --headed

# Run specific suite
pytest tests/test_po_login_flow.py
pytest tests/test_po_positive_flows.py
pytest tests/test_po_negative_flows.py

# Run by marker
pytest -m login
pytest -m positive
pytest -m negative
```

Run from the workspace root:

```bash
pytest swarajya-create/purchase-order/tests -v
```

---

## 📝 Test Data Configuration

Place your test cases Excel file into `test_data/` (e.g., `Create-Purchase-Order.xlsx` or `Purchase-Order.xlsx`).
The reader automatically searches for sheets:
- `Positive_Tests`
- `Negative_Tests`

Expected columns:
- `Test Case ID` (e.g. `TC_PO_POS_01`, `TC_PO_NEG_01`)
- `Scenario`
- `Test Steps` or `Steps`
- `Test Data` (Key-value formatted or bulleted list)
- `Expected Result`
- `Execution Type` (`UI`)
- `Test Status` (Updated automatically upon execution)
- `Remarks` (Updated automatically with timestamps and pass/fail reason)
