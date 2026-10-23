# 👥 Employee Update Management Automation Module

Automated test suite for **Employee Update** operations in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), integrated with centralized Excel test workbooks with **strictly zero hardcoded values** and **dynamic wait times**.

---

## 🧭 Navigation Workflow

The Employee Update operation follows a standard lifecycle path from the portal dashboard:

1. **Authentication / Default Landing**: User logs in with valid Admin credentials & OTP -> lands on [`/default`](https://swarajya-stg.corecotechnologies.com/default).
2. **Employee Listing**: Navigates from landing screen -> [`/employeeList`](https://swarajya-stg.corecotechnologies.com/employeeList) via sidebar navigation or direct path.
3. **Open Employee Profile**: On the listing table, clicks the profile action icon (`button[mattooltip='Profile']` / `i.icofont-user`) on the target employee's row -> opens the Employee Profile update view at [`/empProfile/<id>`](https://swarajya-stg.corecotechnologies.com/empProfile).

---

## 📋 Update Form Specification & Lifecycle Features

| Field / Action Label | Form Control | Type | Constraints & Behaviors |
| :--- | :--- | :--- | :--- |
| **Employee ID \*** | `id` | Text Input | **Strictly Disabled / Read-only** (Immutable during edit) |
| **First Name \*** | `emp_first_name` | Text Input | Mandatory. Letters, length limits, whitespace trimmed |
| **Middle Name** | `emp_middle_name` | Text Input | Optional middle name |
| **Last Name \*** | `emp_last_name` | Text Input | Mandatory. Supports valid hyphens and apostrophes |
| **Gender \*** | `emp_gender` | Radio Button | Male (`value=1`) / Female (`value=0`) |
| **Date of Birth \*** | `emp_dob` | Date Input | Mandatory. Date picker toggle, age validation |
| **Official Email \*** | `emp_email` | Text Input | Mandatory. Valid email format, uniqueness check |
| **Personal Email** | `emp_personal_email` | Text Input | Optional. Valid email format validation |
| **Mobile Number \*** | `emp_mobile_number` | Text Input | Mandatory. Exactly 10 digits, numeric validation |
| **Date of Joining \***| `emp_doj` | Date Input | Mandatory. Must be after DOB, future limit check |
| **Marital Status** | `emp_maritalStatus`| Dropdown | `Married`, `Unmarried` options |
| **Emergency Contact** | `emp_emergency_contact_name` | Text Input | Name of emergency contact person |
| **Emergency Number** | `emp_emergency_contact_number` | Text Input | Exactly 10 digits numeric format |
| **Correspondence Addr**| `emp_correspondance_address1` | Text Input | Address Line 1 |
| **Address Line 2** | `emp_correspondance_address2` | Text Input | Address Line 2 |
| **City** | `emp_correspondance_city` | Text Input | City of correspondence |
| **PIN** | `emp_correspondance_pin` | Text Input | 6-digit postal code |
| **Dietary Switches** | `Is Egg?`, `Is Non-Veg?` | Slide Toggle | Toggle ON/OFF state persistence |

**Form Actions**:
- **Save / Update** (`button[type='submit']`): Submits profile updates, validates fields, shows success confirmation.
- **Cancel / Discard** (`button:has-text('Cancel')`): Reverts unsaved changes and retains current profile state.

---

## 📊 Centralized Data Source & Excel Synchronization

- **Test Scenarios**: Sourced from `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `update/emp_mgmt` / `updateemp_mgmt`].
- **Input Test Data**: Sourced from `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `update/emp_mgmt` / `updateemp_mgmt`].
- **Authentication Credentials & Base URL**: Dynamically loaded from header banner rows in `Swarajya-test-data.xlsx`.
- **Live Excel Writeback**: Automatically syncs test status (`PASS`, `FAIL`, `SKIP`), `Automation Status`, and duration/remarks back to `Swarajya-test-cases.xlsx`.
- **HTML Report Generation**: Finalized into `shared/reports/employee_update_*.html`.
- **Desktop Execution Summary Popup**: Displays interactive results summary without unsolicited browser popups.
- **1-to-1 Evidence Screenshots**: Automatically captures visual evidence on PASS and FAIL into `screenshots/` using `{STATUS}_{TC_ID}__{TIMESTAMP}.png`.
- **CI/CD Integration**: Fully integrated into GitHub Actions CI/CD pipeline with dynamic artifact sanitization and full positive/negative regression coverage.

---

## 🏛️ Directory Structure

```
employee-management/
├── emp_update_pages/          # Page Object Models & Form Executor (Zero Hardcoding)
│   ├── __init__.py
│   ├── form_executor.py
│   └── employee_update_page.py
├── emp_update_utils/          # Centralized Excel Parsers & Writeback
│   ├── __init__.py
│   └── excel_reader.py
├── tests/                    # Pytest test suites
│   ├── __init__.py
│   ├── test_emp_update_login_flow.py      # Session & navigation verification (3 tests)
│   ├── test_emp_update_positive_flows.py  # Parameterized positive scenarios from Excel (15 tests)
│   └── test_emp_update_negative_flows.py  # Parameterized negative validation scenarios (13 tests)
├── screenshots/              # Automated 1-to-1 test execution evidence
├── conftest.py               # Playwright fixtures & dynamic wait hooks
├── pytest.ini                # Module execution settings
└── README.md                 # Complete execution & specification manual
```

---

## 🚀 Execution Guide

```bash
# Run all Employee update tests (31 tests)
pytest swarajya-update/employee-management/tests -v --headless

# Run authentication and navigation path tests
pytest swarajya-update/employee-management/tests/test_emp_update_login_flow.py -v --headless

# Run only positive flow test cases (15 tests)
pytest swarajya-update/employee-management/tests/test_emp_update_positive_flows.py -v --headless

# Run only negative flow test cases (13 tests)
pytest swarajya-update/employee-management/tests/test_emp_update_negative_flows.py -v --headless

# Run in headed mode
pytest swarajya-update/employee-management/tests -v --headed
```
