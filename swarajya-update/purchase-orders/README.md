# 📦 Purchase Order Update Automation Module

Automated test suite for **Purchase Order Update** operations in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), integrated with centralized Excel test workbooks with **strictly zero hardcoded values**.

---

## 🧭 Navigation Workflow

The Purchase Order Update operation follows a 4-step path from the portal dashboard (omitting the 4th Customer Management step `/customerDetails` and transitioning directly from the Invoice Dashboard to `/purchaseOrder`):

1. **Authentication / Default Landing**: User logs in with valid credentials & OTP -> lands on [`/default`](https://swarajya-stg.corecotechnologies.com/default).
2. **Invoice Reports**: Navigates from landing screen -> [`/invoiceReports`](https://swarajya-stg.corecotechnologies.com/invoiceReports) via Invoicing navigation.
3. **Invoice Home / Dashboard**: Selects Invoice Home -> [`/invoicedashboard`](https://swarajya-stg.corecotechnologies.com/invoicedashboard).
4. **Purchase Orders**: Clicks "Purchase Orders" card on the Invoice Dashboard -> opens the Purchase Order listing directly at [`/purchaseOrder`](https://swarajya-stg.corecotechnologies.com/purchaseOrder). *(Notice: The `/customerDetails` step from Customer Management is omitted).*
5. **Update Purchase Order**: On the listing, clicks the update button with the **pencil icon** (`button:has(mat-icon:has-text('edit'))`) under the Action column for the target row -> opens the Purchase Order Update form modal.

---

## 📋 Update Form Specification

| Field Label | Form Control | Type | Constraints & Behaviors |
| :--- | :--- | :--- | :--- |
| **PO Date** | `date` | Date Input | Read-only input with calendar picker popup toggle (`mat-datepicker-toggle`) |
| **PO Reference No.** | `refNo` | Text Input | Editable PO Reference identification number |
| **Customer Name \*** | `poCustomer` | Dropdown | **Strictly Disabled / Read-only** (Cannot be modified) |
| **Authorized By** | `authorizedBy` | Text Input | Authorizing authority full name |
| **PO Details \*** | `poDetails` | Textarea | **Mandatory**. If empty, blocks update and shows error snackbar |
| **Base Amount** | `poBaseAmount` | Numeric Input | Subtotal before taxes |
| **Tax Amount** | `poTaxAmount` | Numeric Input | Calculated GST / applicable taxes |
| **Total Amount** | `poTotalAmount` | Numeric Input | Gross PO value |
| **Currency** | `poCurrency` | Dropdown | Options: `INR`, `USD`, `SAR`, `EUR`, `GBP`, `NZD`, `JYN` |
| **Status \*** | `poStatus` | Dropdown | Options: `ACTIVE`, `FULLY_USED`, `PARTIALLY_USED`, `CANCELLED` |
| **PO Document** | `po_document_url` | File Input | "Choose File" uploads `.pdf`, `.doc`, `.docx`, etc. Displays "View Current Document" link |

**Form Actions**:
- **Update** (`button:has-text('Update')`): Submits valid updates. Displays green snackbar: `Purchase Order Updated Successfully!`. If mandatory fields are missing, displays red snackbar: `Please Enter PO Details..!`.
- **Cancel** (`button:has-text('Cancel')`): Retracts back to the PO list view without saving uncommitted changes.

---

## 📊 Centralized Data Source & Excel Synchronization

- **Test Scenarios**: Sourced from `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `updatepurchase-order`].
- **Input Test Data**: Sourced from `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `updatepurchase-order`].
- **Authentication Credentials & Base URL**: Dynamically loaded from header banner rows in `Swarajya-test-data.xlsx`.
- **Live Excel Writeback**: Automatically syncs test status (`PASS`, `FAIL`, `SKIP`), `Automation Status`, and error remarks back to `Swarajya-test-cases.xlsx`.
- **HTML Report Generation**: Finalized into `shared/reports/po_update_*.html`.
- **Interactive Popup**: Styled desktop execution popup summarizing total, passed, failed, skipped, and direct report link without auto-opening the browser.
- **1-to-1 Evidence Screenshots**: Automatically captures visual evidence on PASS and FAIL into `screenshots/` using `{STATUS}_{TC_ID}__{TIMESTAMP}.png`.

---

## 🏛️ Directory Structure

```
purchase-orders/
├── po_update_pages/        # Page Object Models & Form Executor (Zero Hardcoding)
│   ├── __init__.py
│   ├── form_executor.py
│   └── po_update_page.py
├── po_update_utils/        # Centralized Excel Parsers & Writeback
│   ├── __init__.py
│   └── excel_reader.py
├── tests/                  # Pytest test suites
│   ├── __init__.py
│   ├── test_po_update_login_flow.py      # Session & navigation verification (3 tests)
│   ├── test_po_update_positive_flows.py  # Parameterized positive scenarios from Excel (17 tests)
│   └── test_po_update_negative_flows.py  # Parameterized negative validation scenarios (11 tests)
├── screenshots/            # Automated 1-to-1 test execution evidence
├── conftest.py             # Playwright fixtures & hooks
├── pytest.ini              # Module execution settings
└── README.md               # Complete execution & specification manual
```

---

## 🚀 Execution Guide

```bash
# Run all Purchase Order update tests (31 tests)
pytest swarajya-update/purchase-orders/tests -v

# Run authentication and navigation path tests
pytest swarajya-update/purchase-orders/tests/test_po_update_login_flow.py -v

# Run only positive flow test cases
pytest swarajya-update/purchase-orders/tests/test_po_update_positive_flows.py -v

# Run only negative flow test cases
pytest swarajya-update/purchase-orders/tests/test_po_update_negative_flows.py -v

# Run in headed mode
pytest swarajya-update/purchase-orders/tests -v --headed
```

---

## 🔄 CI/CD Pipeline Status
- **Status**: Integrated & Verified ✅
- **Automation Pipeline**: [Swarajya Automation CI/CD Pipeline](https://github.com/himanshu-prakash-test/swarajya-stg-automation/actions)
- **Supported Execution**: Headless and Headed modes via GitHub Actions `workflow_dispatch`.

