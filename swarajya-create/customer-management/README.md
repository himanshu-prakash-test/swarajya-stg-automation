# 👥 Swarajya Customer Management Automation Suite

End-to-end automated test suite for **Customer Management** in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), covering customer onboarding, form field validations, tax/GSTIN handling, and grid searches.

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
│   ├── base_page.py                     # Inherited from shared.pages.base_page
│   ├── customer_page.py                 # Customer listing, forms, modals, dropdowns, switches, search
│   ├── form_executor.py                 # Data-driven test dispatcher & strict assertion engine
│   └── login_page.py                    # 2FA-compliant authentication
│
├── customer_utils/                      # Utilities & Data Parsers
│   ├── __init__.py                      # Package exports
│   └── excel_reader.py                  # Excel parser & live result reporter
│
├── test_data/                           # Test Data Workbooks
│   ├── credentials.xlsx                 # Role-based credentials (Admin, Manager)
│   ├── Create-Customer-Management.xlsx  # Master Positive (26) & Negative (8) test scenarios
│   └── auth_state.json                  # Cached browser session state (auto-generated)
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

## 🚀 Key Functional Capabilities Automated

1. **Confirmation Snackbar / Modal Dialog Handling**:
   - **Clicking 'Yes'**: Submits the customer record, automatically navigates to Customer Details (`/customerDetails`), executes a grid search for the customer name, and verifies that the new customer is visible in the table.
   - **Clicking 'No'**: Cancels the confirmation prompt without submitting; asserts that the form state remains intact and verifies that the customer was not created in the database or table listing.
2. **Dropdown Selection Validation**:
   - **Country Dropdown (`TC_CUSTOMER_POS_24`)**: Verifies that the Country dropdown opens cleanly, lists available countries, and permits selection.
   - **Currency Dropdown (`TC_CUSTOMER_POS_25`)**: Verifies that operational currencies (`INR`, `USD`, `EUR`) open cleanly and are selectable.
3. **GST / IGST Toggle Switch Validation (`TC_CUSTOMER_POS_26`)**:
   - Verifies that the "Is IGST Applicable?" slide toggle switch responds cleanly to toggle events (switches between enabled and disabled states).
4. **Session Timeout & Security Negative Testing (`TC_CUSTOMER_NEG_08`)**:
   - Simulates session expiration during customer creation and verifies that the application intercepts unauthorized submissions with redirection to authentication.

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

---

## 📊 Reporting & Evidence

- **HTML Reporter**: Integrated with `shared.reporter`, automatically generates standalone HTML reports in `reports/`.
- **Summary Popup**: Automatically displays a desktop notification summarizing test counts, pass/fail metrics, duration, and direct report links.
- **Excel Synchronization**: Updates `Create-Customer-Management.xlsx` with test status, timestamp, and detailed remarks.
- **1-to-1 Evidence Screenshots**: Automatically captures full-page (`full_page=True`) screenshot evidence into `screenshots/` **strictly immediately after the test case has executed** (on both PASS and FAIL events, never before). File format: `{STATUS}_{TC_ID}__{TIMESTAMP}.png`.
