# 👥 Swarajya Customer Management Automation Suite

End-to-end automated test suite for **Customer Management** in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), covering customer onboarding, form field validations, tax/GSTIN handling, and grid searches.
Integrated with the centralized Excel test data architecture with **strictly zero hardcoded values**.

---

## 🧭 Navigation Workflow

The Customer Create operation follows the portal path:
1. **Authentication**: User logs in with valid credentials & OTP -> lands on [`/default`](https://swarajya-stg.corecotechnologies.com/default).
2. **Invoice Reports**: Navigates from landing screen -> [`/invoiceReports`](https://swarajya-stg.corecotechnologies.com/invoiceReports).
3. **Invoice Home**: Selects Invoice Home -> [`/invoicedashboard`](https://swarajya-stg.corecotechnologies.com/invoicedashboard).
4. **Customer Details**: Opens Customer Details listing -> [`/customerDetails`](https://swarajya-stg.corecotechnologies.com/customerDetails).
5. **Add Customer**: Clicks "Add Customer" button -> opens create form at [`/addNewCustomer`](https://swarajya-stg.corecotechnologies.com/addNewCustomer).

---

## 📋 Form Fields Specification (Customer Details)

The Customer Creation form includes the following 20 core fields:

| Field Label | Field Type | Requirement | Key Notes & Validations |
| :--- | :--- | :---: | :--- |
| **Customer Name** | Text Input | **Mandatory** | Unique business/organization name |
| **Country** | Dropdown/Text | **Mandatory** | Country of customer entity |
| **Place of Supply** | Dropdown/Text | **Mandatory** | State/jurisdiction code for tax supply |
| **Finance Person Email ID** | Email Input | **Mandatory** | Valid finance/accounts notification email |
| **Payment Terms (Days)** | Numeric Input | **Mandatory** | Credit terms in days (e.g., 30, 45, 60) |
| **Currency** | Dropdown/Text | **Mandatory** | Operational currency (INR, USD, EUR) |
| **Address Line 1** | Text/Textarea | Optional | Primary street/unit address |
| **Address Line 2** | Text/Textarea | Optional | Secondary address line / landmark |
| **City** | Text Input | Optional | City of customer location |
| **PIN** | Text/Numeric | Optional | 6-digit PIN code |
| **State** | Dropdown/Text | Optional | State of customer entity |
| **Is IGST Applicable?** | Toggle/Checkbox | Optional | Inter-state tax applicability toggle |
| **PAN/IT NO.** | Text Input | Optional | 10-character alphanumeric PAN format |
| **GST No.** | Text Input | Optional | 15-character GSTIN format |
| **Code** | Text Input | Optional | Unique customer identification code |
| **Primary Person Name** | Text Input | Optional | Primary contact person's full name |
| **Finance Person Name** | Text Input | Optional | Accounts / finance contact person |
| **Primary Person Phone** | Tel/Numeric | Optional | 10-digit primary contact mobile/phone |
| **Finance Person Phone** | Tel/Numeric | Optional | 10-digit finance contact mobile/phone |
| **Primary Person Email ID** | Email Input | Optional | Valid email address format |

---

## 🏛️ Directory Structure

```
customer-management/
│
├── customer_pages/                      # Page Object Model & Execution Layer
│   ├── __init__.py                      # Package exports (CustomerPage, FormExecutor, LoginPage)
│   ├── customer_page.py                 # Customer listing, forms, modals, dropdowns, switches, search
│   └── form_executor.py                 # Data-driven test dispatcher & assertion engine (Zero hardcoding)
│
├── customer_utils/                      # Utilities & Data Parsers
│   ├── __init__.py                      # Package exports
│   └── excel_reader.py                  # Dynamic loader & test case writeback
│
├── tests/                               # Pytest Test Suites
│   ├── __init__.py
│   ├── test_customer_login_flow.py      # Session & authentication verification (2 tests)
│   ├── test_customer_positive_flows.py  # Parameterized positive scenarios from Excel (26 tests)
│   └── test_customer_negative_flows.py  # Parameterized business & system negative scenarios (8 tests)
│
├── screenshots/                         # Automated test execution evidence
├── pytest.ini                           # Module pytest settings and registered markers
├── requirements.txt                     # Dependencies
└── README.md                            # Customer Management Documentation
```

---

## 📊 Centralized Data Source & Excel Synchronization

- **Test Scenarios**: Sourced from `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `createcutomer-mgmt`].
- **Input Test Data**: Sourced from `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `createcustomer-mgmt`].
- **Authentication Credentials & Base URL**: Dynamically loaded from header banner rows in `Swarajya-test-data.xlsx`.
- **Live Excel Writeback**: Automatically syncs test status (`PASS`, `FAIL`, `SKIP`), `Automation Status`, and error remarks back to `Swarajya-test-cases.xlsx`.
- **HTML Report Generation**: Finalized into `shared/reports/customer_mgmt_*.html`.
- **Interactive Popup**: Styled desktop execution popup summarizing total, passed, failed, skipped, and direct report link without auto-opening the browser.
- **1-to-1 Evidence Screenshots**: Automatically captures visual evidence on PASS and FAIL into `screenshots/` using `{STATUS}_{TC_ID}__{TIMESTAMP}.png`.

---

## 🚀 Execution Guide

### 1. Run Complete Customer Management Suite (36 Tests)
```powershell
cd swarajya-create\customer-management
pytest
```

### 2. Run in Headed Browser Mode
```powershell
pytest --headed
```

### 3. Run by Marker
```powershell
# Run only authentication tests (2 tests)
pytest -m login

# Run only positive operational scenarios (26 tests)
pytest -m positive

# Run negative business & system scenarios (8 tests)
pytest -m negative
```

