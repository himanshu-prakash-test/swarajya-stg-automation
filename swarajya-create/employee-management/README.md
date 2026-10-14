# 👤 Swarajya Employee Management Automation Framework (Create Module)

An enterprise-grade, data-driven test automation framework for the **Employee Management (Create)** module of the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), built with **Python 3**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 🏛️ Module Architecture & Latest Structure

```
swarajya-create/employee-management/
│
├── emp_pages/                           # Page Object Model (POM) Layer
│   ├── __init__.py
│   ├── employee_page.py                 # Employee creation form, mat-selects, datepickers, search
│   ├── project_page.py                  # Project assignment & verification helpers
│   └── form_executor.py                 # Data-driven workflow executor & validation assertions
│
├── emp_utils/                           # Utilities Layer
│   ├── __init__.py
│   └── excel_reader.py                  # Centralized test cases & data loader (createemp-mgmt)
│
├── tests/                               # Test Execution Runners
│   ├── __init__.py
│   ├── test_emp_login_flow.py           # Authentication & navigation verification (2 tests)
│   ├── test_emp_positive_flows.py       # Parametrized positive employee creation (7 tests)
│   └── test_emp_negative_flows.py       # Parametrized negative form validations (18 tests)
│
├── screenshots/                         # Test evidence screenshots (PASS / FAIL)
├── pytest.ini                           # Pytest configuration & markers
├── requirements.txt                     # Python dependencies
└── README.md                            # Comprehensive Module Documentation
```

### Central Shared Assets (`shared/`):
- **`shared/test_data/Swarajya-test-cases.xlsx`**: Master test case definitions and results sheet `createemp-mgmt`.
- **`shared/test_data/Swarajya-test-data.xlsx`**: Input test data, base URL, and credentials sheet `createemp-mgmt`.
- **`shared/pages/login_page.py`**: Central login POM with 2FA handling and session persistence.
- **`shared/utils/paths.py`**: Central environment and path resolver.
- **`shared/reporter/`**: HTML report generator and test result aggregator.
- **`shared/utils/popup.py`**: Native desktop summary popup (auto-bypassed in CI/CD).

---

## ⚡ Core Engineering Standards & Zero Hardcoding

1. **Zero Hardcoded Values**:
   - Base URL, login credentials, form inputs, scenarios, and validation criteria are fetched dynamically from `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `createemp-mgmt`] and `shared/test_data/Swarajya-test-cases.xlsx` [Sheet: `createemp-mgmt`].
2. **Page Object Model (POM)**:
   - Clean separation of page interactions (`emp_pages/`) from test execution logic (`tests/`).
3. **Session Authentication & Caching**:
   - Authenticates once per test session and caches the browser state partitioned by hostname, eliminating redundant logins.
4. **CI/CD Pipeline Compatibility**:
   - Controlled via environment variables (`HEADLESS=true`, `SWARAJYA_ENV`, `SWARAJYA_BASE_URL`).
   - Standard Pytest exit codes for seamless pipeline failure detection.
   - Generates HTML reports and purges screenshots older than 24 hours.

---

## 📊 Test Coverage Matrix

### 1. Authentication & Navigation Flows (`test_emp_login_flow.py`)
- `TC_EMP_AUTH_01`: Verify Admin login succeeds with credentials from Excel.
- `TC_EMP_NAV_01`: Verify complete navigation path: `/default` -> `/employeeList` -> `/addNewEmployee`.

### 2. Positive Scenarios (`Positive_Flows` — 7 Tests)
| Test ID | Scenario |
| :--- | :--- |
| `TC_POS_EMP_001` | Create a new employee record with all valid mandatory details (Male/Female) |
| `TC_POS_EMP_003` | Create a new employee record verifying alternative dropdown options & Middle Name |
| `TC_POS_EMP_005` | Create a new employee record using maximum allowed characters for Name fields |
| `TC_POS_EMP_006` | Create a new employee record with valid special characters in allowable fields |
| `TC_POS_EMP_008` | Verify that a newly added employee is displayed in the list with a unique Employee ID |
| `TC_POS_EMP_009` | Create a new employee record with leading and trailing spaces in text fields |
| `TC_POS_EMP_010` | Verify the functionality of the Cancel/Reset button while creating a new employee |

### 3. Negative Scenarios (`Negative_Flows` — 18 Tests)
| Test ID | Scenario |
| :--- | :--- |
| `TC_NEG_EMP_001` | Attempt to create an employee record with blank mandatory fields |
| `TC_NEG_EMP_002` | Attempt to create an employee record with numeric/special characters in names |
| `TC_NEG_EMP_003` | Attempt to create an employee record with invalid mobile number format |
| `TC_NEG_EMP_004` | Attempt to create an employee record with improperly formatted email addresses |
| `TC_NEG_EMP_005` | Attempt to create an employee record with underage Date of Birth (<18) |
| `TC_NEG_EMP_006` | Attempt to create an employee record with Joining Date before Date of Birth |
| `TC_NEG_EMP_008` | Attempt to create an employee record with an already existing Personal Email |
| `TC_NEG_EMP_009` | Attempt to create an employee record with an already existing Mobile Number |
| `TC_NEG_EMP_010` | Attempt to create an employee record with First Name exceeding character limit |
| `TC_NEG_EMP_011` | Attempt to create an employee record with SQL injection payload in name |
| `TC_NEG_EMP_012` | Attempt to create an employee record with Date of Birth in the future |
| `TC_NEG_EMP_013` | Attempt to create an employee record with an invalid Department selection |
| `TC_NEG_EMP_014` | Attempt to create an employee record with XSS payload in name |
| `TC_NEG_EMP_015` | Validate dropdown options (Department, Designation, Manager, Role) are text-only |
| `TC_NEG_EMP_016` | Validate newly added employee does not appear in Reporting Manager dropdown |
| `TC_NEG_EMP_017` | Attempt to create an employee record using only whitespaces in mandatory fields |
| `TC_NEG_EMP_018` | Attempt to submit the Create Employee form after user session has timed out |
| `TC_NEG_EMP_019` | Create an employee with an already existing Official Email |

---

## 🚀 Execution Guide

### Local Execution (Headed Mode)
```bash
pytest swarajya-create/employee-management/tests --headed
```

### CI / Headless Mode
```bash
HEADLESS=true pytest swarajya-create/employee-management/tests
```

### Run Positive or Negative Suites Selectively
```bash
pytest swarajya-create/employee-management/tests/test_emp_positive_flows.py
pytest swarajya-create/employee-management/tests/test_emp_negative_flows.py
pytest swarajya-create/employee-management/tests/test_emp_login_flow.py
```
