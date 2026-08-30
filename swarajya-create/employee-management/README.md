# 👤 Swarajya Employee Management Automation Framework

An enterprise-grade, data-driven test automation framework for the **Employee Management (Create)** module of the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), built with **Python 3.13**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 🏛️ Module Architecture

```
swarajya-create/employee-management/
│
├── emp_pages/                           # Page Object Model (POM) Layer
│   ├── __init__.py
│   ├── base_page.py                     # Base browser wrapper, dynamic waits & toast listeners
│   ├── login_page.py                    # Multi-role authentication & session state persistence
│   ├── employee_page.py                 # Employee creation form, mat-selects, datepickers, search
│   ├── project_page.py                  # Project assignment & verification helpers
│   └── form_executor.py                 # Data-driven workflow executor & validation assertions
│
├── emp_utils/                           # Utilities Layer
│   ├── excel_reader.py                  # OpenPyXL scenario loader & real-time Excel result writer
│   ├── logger.py                        # Standard colored logging engine
│   └── popup.py                         # Native Tkinter desktop execution summary popup
│
├── test_data/                           # Test Assets & Caches
│   ├── Swarajya-Create-test-cases (6).xlsx # Master Excel test cases workbook
│   ├── credentials.xlsx                 # Role-based credentials (Manager / Employee / Admin)
│   └── auth_state.json                  # Reusable Playwright session storage state
│
├── tests/                               # Test Execution Runners
│   ├── __init__.py
│   ├── test_emp_login_flow.py           # Authentication & employee page navigation sanity
│   ├── test_emp_positive_flows.py       # Parametrized positive employee creation tests (10 cases)
│   └── test_emp_negative_flows.py       # Parametrized negative form validation tests (20 cases)
│
├── screenshots/                         # 1-to-1 Test Evidence Screenshots
├── pytest.ini                           # Pytest configuration & markers
├── requirements.txt                     # Python dependencies
└── README.md                            # Comprehensive Module Manual
```

---

## ⚡ Core Engineering & Design Standards

### 1. Page Object Model (POM) & Dynamic Synchronization
- Encapsulates UI locators and low-level Playwright actions in `emp_pages/`.
- Uses dynamic event-driven waits (`wait_for(state="visible")`, `wait_for_dom_ready()`) ensuring zero flakiness without static sleep calls.

### 2. Session Authentication Caching
- Authenticates once per test session and caches the authenticated browser state in `test_data/auth_state.json`.
- Each test function runs in an isolated browser context pre-loaded with `storage_state`, executing tests with rapid startup.

### 3. Angular Material Form Handlers
- Custom handlers for Angular Material components:
  - `mat-select` search and option selectors.
  - Datepicker calendar pickers and raw input formatting.
  - Multi-tab form traversal (Personal Details, Professional Details, Bank & Salary Details).

### 4. Bi-Directional Master Excel Synchronization
- Directly loads test scenarios from `Swarajya-Create-test-cases (6).xlsx`.
- Synchronizes real-time execution results back to the Excel sheets:
  - **`Test Status`**: `PASS` / `FAIL` / `SKIP`
  - **`Automation Status`**: `Automated` / `Not automated - API`
  - **`Auto Script ID`**: `AUT_POS_EMP_xxx` / `AUT_NEG_EMP_xxx`
  - **`Execution Remark`**: Human-readable test outcome explanation.

### 5. 1-to-1 Screenshot Audit & Auto-Retention
- Captures full-page screenshots for test outcomes labeled `{STATUS}_{TC_ID}__{TIMESTAMP}.png`.
- Automatically retains recent evidence and purges screenshots older than 24 hours.

---

## 📊 Test Coverage Matrix

### Positive Scenarios (`Positive_Flows` — 10 Tests)
| Test ID | Test Scenario | Expected Outcome |
| :--- | :--- | :--- |
| `TC_POS_EMP_001` | Verify navigation to Employee Management page | Successfully loads Employee list grid |
| `TC_POS_EMP_002` | Create employee with all mandatory fields | Employee created successfully |
| `TC_POS_EMP_003` | Create employee with mandatory + optional fields | Full profile created successfully |
| `TC_POS_EMP_004` | Search existing employee by Name / ID | Filtered employee appears in grid |
| `TC_POS_EMP_005` | Create employee with different role permissions | Role-based profile created |
| `TC_POS_EMP_006` | Verify Cancel button on creation form | Form cancelled, returns to list |
| `TC_POS_EMP_007` | Create inactive employee | Inactive employee created |
| `TC_POS_EMP_008` | Filter employee list by department/status | Grid filtered accordingly |
| `TC_POS_EMP_009` | Create employee with max length inputs | Inputs accepted within limits |
| `TC_POS_EMP_010` | Verify whitespace trimming on text inputs | Saved data is trimmed |

### Negative Scenarios (`Negative_Flows` — 20 Tests)
| Test Range | Focus Area | Validation Enforced |
| :--- | :--- | :--- |
| `TC_NEG_EMP_001` - `005` | Blank Mandatory Fields | Required field error messages |
| `TC_NEG_EMP_006` - `008` | Duplicate Data Checks | Duplicate Email / Employee Code rejection |
| `TC_NEG_EMP_009` - `012` | Format & Regex Checks | Invalid Email, Phone format, non-numeric fields |
| `TC_NEG_EMP_013` - `016` | Date & Range Logic | Invalid DOB / Joining Date chronological constraints |
| `TC_NEG_EMP_017` - `020` | Security & Outage Tests | SQL Injection, XSS payloads & network offline mocks |

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites & Installation
```powershell
cd swarajya-create\employee-management
pip install -r requirements.txt
playwright install chromium
```

### 2. Run All Employee Management Tests
```powershell
pytest
```

### 3. Run Positive Tests Only
```powershell
pytest tests/test_emp_positive_flows.py
```

### 4. Run Negative Tests Only
```powershell
pytest tests/test_emp_negative_flows.py
```

### 5. Run a Specific Test Case
```powershell
pytest -k "TC_POS_EMP_002"
```

### 6. Run with Visible Browser (Headed Mode)
```powershell
pytest --headed --slowmo 400
```
