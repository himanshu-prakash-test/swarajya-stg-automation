# 🚀 Swarajya Staging Automation - Update Invoice Management Module

> **Branch:** `update/invoice_mgmt`  
> **Master Repository:** [Switch to main branch](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/main)

This branch contains strictly the **Update Invoice Management Module** along with the shared framework dependencies.

## 🏃 Running Tests on this Branch
```bash
# Run tests for this module
pytest swarajya-update/invoice-management/tests -v

# Run with HTML report
pytest swarajya-update/invoice-management/tests --html=report.html --self-contained-html
```

---

# 🧾 Invoice Update Management Automation Module

Automated test suite for **Invoice Update** operations in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), integrated with centralized Excel test workbooks with **strictly zero hardcoded values** and **dynamic wait times**.

---

## 🧭 Navigation Workflow

The Invoice Update operation follows a standard lifecycle path from the portal dashboard:

1. **Authentication / Default Landing**: User logs in with valid credentials & OTP -> lands on [`/default`](https://swarajya-stg.corecotechnologies.com/default).
2. **Invoice Reports**: Navigates from landing screen -> [`/invoiceReports`](https://swarajya-stg.corecotechnologies.com/invoiceReports) via Invoicing navigation.
3. **Invoice Home / Dashboard**: Selects Invoice Home -> [`/invoicedashboard`](https://swarajya-stg.corecotechnologies.com/invoicedashboard).
4. **Invoice Listing**: Opens Invoice listing directly at [`/invoice`](https://swarajya-stg.corecotechnologies.com/invoice).
5. **Update Invoice**: On the listing, clicks the update button with the **edit icon** (`button:has(mat-icon:has-text('edit'))`) under the Action column for the target row -> opens the Edit Invoice view at [`/editInvoice/<id>`](https://swarajya-stg.corecotechnologies.com/editInvoice).

---

## 📋 Update Form Specification & Lifecycle Features

| Field / Action Label | Form Control | Type | Constraints & Behaviors |
| :--- | :--- | :--- | :--- |
| **Customer Name \*** | `customerName` | Dropdown | **Strictly Disabled / Read-only** (Immutable during edit) |
| **PO Reference** | `poReference` | Dropdown | Associated Purchase Order identifier |
| **Payment Terms** | `paymentTerms` | Text Input | Net payment term days (e.g. 30, 45) |
| **Invoice Date \*** | `invoiceDate` | Date Input | Mandatory. Date picker popup toggle |
| **Due Date \*** | `dueDate` | Date Input | Mandatory. Validated against Invoice Date |
| **Invoice For Project \***| `project` | Text / Select | Target client project association |
| **Internal Notes** | `internalNotes` | Textarea | Non-customer visible internal annotations |
| **External Notes** | `externalNotes` | Textarea | Visible customer remarks printed on invoice |
| **Line Items Grid** | `item_*` | Data Grid | Particulars, SAC, QTY, UOM, Rate, Calculated Amount |
| **Taxes** | `cgst`, `sgst`, `igst` | Numeric | Intra-State (9% + 9%) vs Inter-State (18% IGST) |
| **Status Lifecycle** | `status` | Badge / Filter | `Draft` -> `Finalized` -> `Sent` -> `Partially Paid` -> `Paid` / `Cancelled` |

**Form Actions**:
- **Add Line Item** (`button:has-text('Add')`): Adds new service row to data grid with dynamic subtotal recalculation.
- **Save Invoice** (`button:has-text('Save Invoice')`): Persists updates while keeping customer identity intact.
- **Discard Changes** (`button:has-text('Discard Changes')`): Reverts uncommitted edits.
- **Finalize Invoice** (`button:has-text('Finalize')`): Locks draft invoice and assigns official number.
- **Cancel Invoice** (`button:has-text('Cancel Invoice')`): Transitions status to Cancelled with confirmation dialog.
- **Record Payment** (`button:has(mat-icon:has-text('attach_money'))`): Records partial or full payment.

---

## 📊 Centralized Data Source & Excel Synchronization

- **Test Scenarios**: Sourced from `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `update/invoice_mgmt`].
- **Input Test Data**: Sourced from `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `update/invoice_mgmt`].
- **Authentication Credentials & Base URL**: Dynamically loaded from header banner rows in `Swarajya-test-data.xlsx`.
- **Live Excel Writeback**: Automatically syncs test status (`PASS`, `FAIL`, `SKIP`), `Automation Status`, and duration/remarks back to `Swarajya-test-cases.xlsx`.
- **HTML Report Generation**: Finalized into `shared/reports/invoice_update_*.html`.
- **Desktop Execution Summary Popup**: Displays interactive results summary without unsolicited browser popups.
- **1-to-1 Evidence Screenshots**: Automatically captures visual evidence on PASS and FAIL into `screenshots/` using `{STATUS}_{TC_ID}__{TIMESTAMP}.png`.

---

## 🏛️ Directory Structure

```
invoice-management/
├── invoice_update_pages/      # Page Object Models & Form Executor (Zero Hardcoding)
│   ├── __init__.py
│   ├── form_executor.py
│   └── invoice_update_page.py
├── invoice_update_utils/      # Centralized Excel Parsers & Writeback
│   ├── __init__.py
│   └── excel_reader.py
├── tests/                    # Pytest test suites
│   ├── __init__.py
│   ├── test_invoice_update_login_flow.py      # Session & navigation verification (3 tests)
│   ├── test_invoice_update_positive_flows.py  # Parameterized positive scenarios from Excel (18 tests)
│   └── test_invoice_update_negative_flows.py  # Parameterized negative validation scenarios (11 tests)
├── screenshots/              # Automated 1-to-1 test execution evidence
├── conftest.py               # Playwright fixtures & dynamic wait hooks
├── pytest.ini                # Module execution settings
└── README.md                 # Complete execution & specification manual
```

---

## 🚀 Execution Guide

```bash
# Run all Invoice update tests (32 tests)
pytest swarajya-update/invoice-management/tests -v --headless

# Run authentication and navigation path tests
pytest swarajya-update/invoice-management/tests/test_invoice_update_login_flow.py -v --headless

# Run only positive flow test cases (18 tests)
pytest swarajya-update/invoice-management/tests/test_invoice_update_positive_flows.py -v --headless

# Run only negative flow test cases (11 tests)
pytest swarajya-update/invoice-management/tests/test_invoice_update_negative_flows.py -v --headless

# Run in headed mode
pytest swarajya-update/invoice-management/tests -v --headed
```

