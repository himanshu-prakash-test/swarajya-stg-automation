# 📝 Swarajya Employee Update Automation Suite

Production-grade automated test suite for the **Employee Profile Update Operations** in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), powered by **Playwright (Python)** and **Pytest**.

---

## 🏛️ Module Architecture

```
update/emp_mgmt/
├── emp_update_pages/                    # Page Object Model (POM) Layer
│   ├── __init__.py
│   ├── base_page.py                     # Base wrapper with dynamic waits & tutorial dismissal
│   ├── login_page.py                    # Session authentication, 2FA OTP, role-based login
│   ├── employee_update_page.py          # Profile field mapping, dropdowns, radios, validations
│   └── form_executor.py                 # Data-driven workflow engine for positive & negative updates
│
├── emp_update_utils/                    # Framework Utilities
│   ├── __init__.py
│   ├── excel_reader.py                  # OpenPyXL test loader & real-time Excel reporting engine
│   ├── logger.py                        # Standardized colored console & file logging
│   └── popup.py                         # Desktop Tkinter execution summary popup
│
├── test_data/                           # Test Data & Session Cache
│   ├── Swarajya-Update-Employee-test-cases.xlsx # Master Excel test suite (Positive & Negative sheets)
│   ├── credentials.xlsx                 # Role-based credentials (HR / Admin)
│   └── auth_state.json                  # Cached Playwright browser authentication state
│
├── tests/                               # Test Execution Suites
│   ├── __init__.py
│   ├── test_emp_update_login_flow.py    # Authentication & employee profile navigation sanity
│   ├── test_emp_update_positive_flows.py # Parametrized positive update tests (15 active)
│   └── test_emp_update_negative_flows.py # Parametrized negative validation tests (13 active)
│
├── screenshots/                         # 1-to-1 Test Evidence Screenshots
├── pytest.ini                           # Pytest execution configuration & test markers
├── requirements.txt                     # Python dependencies
└── README.md                            # Comprehensive Module Manual
```

---

## 📊 Test Coverage Breakdown

| Category | Sheet Name | Total Tests | Description |
| :--- | :--- | :---: | :--- |
| **Authentication & Nav** | — | **1** | HR login and landing on employee profile |
| **Positive Update Flows** | `Update_Positive_Flows` | **15** | Mandatory fields, gender switch, marital status, DOB picker, personal email, switches, emergency contacts, addresses, partial updates, read-only verification, multi-section updates |
| **Negative Validation Flows** | `Update_Negative_Flows` | **13** | Cleared mandatory fields, invalid mobile, bad email format, special characters, bad PIN, invalid DOJ/DOB sequence, duplicate mobile, leading/trailing space names, underage DOB, invalid emergency numbers |
| **Total Test Suite** | — | **29** | Complete Employee Update Test Suite |

---

## 🚀 Execution Commands

### 1. Run Complete Employee Update Suite
```bash
cd update/emp_mgmt
pytest
```

### 2. Run Only Positive Update Scenarios
```bash
pytest tests/test_emp_update_positive_flows.py
```

### 3. Run Only Negative Validation Scenarios
```bash
pytest tests/test_emp_update_negative_flows.py
```

### 4. Run in Headed Mode
```bash
pytest --headed
```

### 5. Run a Specific Test Case
```bash
pytest -k "TC_POS_UPD_001"
```

---

## ⚡ Core Features

- **Bi-Directional Excel Reporting**: Reads inputs dynamically from `Swarajya-Update-Employee-test-cases.xlsx` and writes back execution results (`PASS` / `FAIL` / `SKIPPED`), `AUT_*` IDs, timestamps, and remarks.
- **Session Caching**: Authenticates once via `LoginPage` and reuses `auth_state.json` across tests for ultra-fast execution.
- **1-to-1 Screenshot Retention**: Automatically captures full-page evidence screenshots per test case.
- **Desktop Summary Popup**: Displays execution statistics (Total, Passed, Failed, Skipped, Duration) upon session completion.
