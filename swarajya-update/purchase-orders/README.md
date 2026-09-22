# 📦 Purchase Order Update Automation Module

Automated test suite for **Purchase Order Update** operations in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/).

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

## 🧪 Automated Test Suite Matrix (`Update-Purchase-Order.xlsx`)

### Positive Test Scenarios (`Positive_Tests` - 17 Cases)

| Test Case ID | Scenario | Verification Focus | Status |
| :--- | :--- | :--- | :---: |
| **`TC_PO_POS_01`** | Pre-populated Edit Form | Modal opens with existing values across all form controls | **Passed** |
| **`TC_PO_POS_02`** | Immutable Customer Name | Customer Name is disabled/read-only and uneditable | **Passed** |
| **`TC_PO_POS_03`** | Calendar Picker Toggle | PO Date calendar button opens `mat-calendar` popup | **Passed** |
| **`TC_PO_POS_04`** | Currency Dropdown Options | All 7 currency codes (`INR`, `USD`, `SAR`, `EUR`, `GBP`, `NZD`, `JYN`) are selectable | **Passed** |
| **`TC_PO_POS_05`** | Status Dropdown Options | All 4 statuses (`ACTIVE`, `FULLY_USED`, `PARTIALLY_USED`, `CANCELLED`) are selectable | **Passed** |
| **`TC_PO_POS_06`** | File Upload & Document Link | "Choose File" attaches document and provides "View Current Document" link | **Passed** |
| **`TC_PO_POS_07`** | Cancel Button Retraction | Cancel button retracts back to `/purchaseOrder` discarding edits | **Passed** |
| **`TC_PO_POS_08`** | Valid Update & Green Snackbar | Update button shows `Purchase Order Updated Successfully!` (class `snackbar-success`) | **Passed** |
| **`TC_PO_POS_09`** | Search by ID or Name | Grid search filters rows matching PO Ref No or Name | **Passed** |
| **`TC_PO_POS_10`** | Include Fully Used PO Filter | Checkbox toggle dynamically filters/shows `FULLY_USED` records | **Passed** |
| **`TC_PO_POS_11`** | Status Transition: PARTIALLY_USED | Updates status to `PARTIALLY_USED`; verifies table row reflects status | **Passed** |
| **`TC_PO_POS_12`** | Status Transition: CANCELLED | Updates status to `CANCELLED`; verifies table row reflects status | **Passed** |
| **`TC_PO_POS_13`** | Status Transition: FULLY_USED & Filter | Sets status to `FULLY_USED`; verifies visibility interplay with checkbox filter | **Passed** |
| **`TC_PO_POS_14`** | Currency Update Persistence | Changes Currency to `USD`; verifies listing row Currency column update | **Passed** |
| **`TC_PO_POS_15`** | PO Reference Update & Search Sync | Modifies PO Reference No; verifies search retrieves updated record | **Passed** |
| **`TC_PO_POS_16`** | Amount Fields Update Reflection | Updates Base Amount and Total Amount; verifies listing column update | **Passed** |
| **`TC_PO_POS_17`** | Document Replacement Re-upload | Re-attaches replacement document, validates persistence of document link | **Passed** |

### Negative Test Scenarios (`Negative_Tests` - 11 Cases)

| Test Case ID | Scenario | Verification Focus | Status |
| :--- | :--- | :--- | :---: |
| **`TC_PO_NEG_01`** | Empty Mandatory PO Details | Cleared PO Details blocks update and triggers error snackbar `Please Enter PO Details..!` | **Passed** |
| **`TC_PO_NEG_02`** | Rejection of Customer Modification | Direct click/select on disabled Customer Name rejects alterations | **Passed** |
| **`TC_PO_NEG_03`** | Non-existent Record Search | Search for invalid PO Ref yields empty state gracefully without crash | **Passed** |
| **`TC_PO_NEG_04`** | Unauthorized File Extension Block | File input strictly enforces `accept` filter blocking dangerous files (`.exe`, `.sh`) | **Passed** |
| **`TC_PO_NEG_05`** | Unsaved Changes Discard on Cancel | Dirty form cancellation preserves original unmodified table record | **Passed** |
| **`TC_PO_NEG_06`** | Modal Close Icon Dismissal | Top-right 'X' icon button cleanly dismisses modal and discards uncommitted changes | **Passed** |
| **`TC_PO_NEG_07`** | Search Clear Grid Restoration | Clearing search query automatically restores full table records without reload | **Passed** |
| **`TC_PO_NEG_08`** | Mandatory Field Asterisk Indicators | Asserts red asterisk (`*`) indicators are present strictly on required fields | **Passed** |
| **`TC_PO_NEG_09`** | Duplicate PO Reference Number Collision | Asserts application rejects duplicate PO Reference Number assignment matching an existing PO | **Defect / Validation** |
| **`TC_PO_NEG_10`** | Financial Calculation Consistency | Asserts application validates mathematical consistency when Total Amount != Base Amount + Tax Amount | **Defect / Validation** |
| **`TC_PO_NEG_11`** | Cancelled PO Financial Immutability | Asserts lifecycle rules restrict modifying financial terms and amounts on CANCELLED Purchase Orders | **Defect / Validation** |

---

## 🏛️ Directory Structure

```
purchase-order/
├── po_update_pages/        # Page Object Models (POUpdatePage, LoginPage)
│   ├── __init__.py
│   ├── po_update_page.py
│   └── login_page.py
├── po_update_utils/        # Utilities & Excel Parsers
│   ├── __init__.py
│   └── excel_reader.py
├── test_data/              # Test credentials & Master Excel Workbook
│   ├── credentials.xlsx
│   ├── Update-Purchase-Order.xlsx
│   ├── sample_po.pdf
│   └── auth_state.json
├── tests/                  # Pytest test suites
│   ├── __init__.py
│   ├── test_po_login_and_nav_flow.py
│   └── test_po_update_scenarios.py
├── screenshots/            # Failure and audit screenshots
├── conftest.py             # Playwright fixtures & hooks
├── pytest.ini              # Module execution settings
└── README.md               # Complete execution & specification manual
```

---

## 🚀 Execution Guide

```bash
# Run all 28 Purchase Order update tests
pytest swarajya-update/purchase-order/tests -v

# Run only positive test cases
pytest swarajya-update/purchase-order/tests/test_po_update_scenarios.py -m positive -v

# Run only negative test cases
pytest swarajya-update/purchase-order/tests/test_po_update_scenarios.py -m negative -v

# Run in headed mode
pytest swarajya-update/purchase-order/tests -v --headed
```
