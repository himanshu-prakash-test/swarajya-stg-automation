# Swarajya Automation — Employee Management Module

An enterprise-grade, data-driven test automation framework for the **Employee Management (Create)** module of Swarajya, built with **Python**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 🏛️ System Architecture

The framework is architected around the **Page Object Model (POM)** and a **Data-Driven Testing (DDT)** design pattern to ensure high modularity, maintainability, fast execution, and detailed defect tracking.

```
                             ┌──────────────────────────────────────┐
                             │       Excel Workbook (OpenPyXL)      │
                             │  - Positive_Flows (10 Test Cases)    │
                             │  - Negative_Flows (20 Test Cases)    │
                             └──────────────────┬───────────────────┘
                                                │
                                                ▼
┌─────────────────────────┐          ┌───────────────────────┐
│     Pytest Runner       │ ───────► │   excel_reader.py     │ (Loads scenarios &
│  (Session & Parametrize)│          │   - read_test_cases() │  auto-maps headers)
└───────────┬─────────────┘          └───────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────┐
│                       conftest.py                          │
│  - Session Authentication -> Saves auth_state.json        │
│  - Isolated Function Contexts via Playwright storage_state │
│  - Automatic Failure Screenshots                           │
│  - Real-Time Excel Results Recorder                        │
│  - Desktop Summary GUI Popup (Tkinter)                     │
└───────────┬────────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────┐
│                    FormExecutor (pages/)                   │
│  - Maps Excel Test Data & Steps to Application Actions     │
│  - Dynamically verifies Positive Creations & Searches      │
│  - Enforces Negative Validation & Defect Reason Assertions │
└───────────┬────────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────┐
│                 EmployeePage & BasePage                    │
│  - Robust element locators, mat-select dropdown handlers   │
│  - Angular Material datepicker & input formatters          │
│  - Form validation error extraction & Toast monitoring     │
└────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Architectural Highlights

### 1. Page Object Model (POM)
- UI element locators and low-level Playwright actions are cleanly abstracted into `pages/base_page.py` and `pages/employee_page.py`.
- Tests never interact with raw DOM selectors directly, ensuring zero test flakiness when UI selectors change.

### 2. Session Authentication & Storage State
- Rather than re-authenticating and navigating 2FA for every single test case, `conftest.py` authenticates once per session and caches the browser authentication state (`test_data/auth_state.json`).
- Each individual test receives a fresh, isolated `BrowserContext` pre-loaded with `storage_state`, running tests instantaneously without session loss or test-to-test side effects.

### 3. Data-Driven Excel Engine
- Tests are directly parameterized from the Excel workbook (`test_data/Swarajya-Create-test-cases (6).xlsx`).
- Auto-discovers test sheets: `Positive_Flows` (10 cases) and `Negative_Flows` (20 cases).
- API-scoped test cases (e.g. SQL injection, invalid backend IDs) are automatically recognized and marked as **SKIPPED** in UI runs with descriptive reasons.

### 4. Real-Time Excel Results Synchronization
- As each test completes (`PASS`, `FAIL`, or `SKIP`), pytest hooks update the Excel workbook in real time:
  - **`Test Status`**: `PASS` / `FAIL` / `SKIP`
  - **`Automation Status`**: `Automated` / `Not automated - API`
  - **`Auto Script ID`**: e.g., `AUT_POS_EMP_001`, `AUT_NEG_EMP_001`
  - **`Execution Remark`**: Human-readable explanation of the test outcome or the exact application defect identified.
  - **`Last Run`**: Timestamp of execution.

### 5. Automated Failure Screenshots & Desktop GUI Reporting
- Captures full-page high-resolution PNG screenshots upon any test failure in `screenshots/`.
- Displays a native desktop GUI popup (Tkinter) upon test session completion showing test metrics, duration, and detailed defect logs.

---

## 📁 Directory Structure & Responsibilities

```
swarajya-create/
├── pages/
│   ├── __init__.py
│   ├── base_page.py          # Core navigation, retry loops, toast alerts, tutorial dismissals
│   ├── login_page.py         # Login form, 2FA code handling, auth state persistence
│   ├── employee_page.py      # Employee creation page object, mat-selects, datepickers, search
│   └── form_executor.py      # Data-driven workflow executor, positive & negative assertion logic
├── test_data/
│   ├── Swarajya-Create-test-cases (6).xlsx  # Primary test cases workbook
│   ├── credentials.xlsx      # Role-based credentials (Employee/Manager)
│   └── auth_state.json       # Cached Playwright session storage state
├── tests/
│   ├── __init__.py
│   ├── test_login_flow.py     # Authentication verification tests
│   ├── test_positive_flows.py # Data-driven positive employee creation tests
│   └── test_negative_flows.py # Data-driven negative validation & defect tests
├── utils/
│   ├── __init__.py
│   ├── excel_reader.py        # Excel parser and live test results updater (openpyxl)
│   ├── logger.py              # Centralized logging utility
│   └── popup.py               # Modern Tkinter summary popup dialog
├── screenshots/               # High-resolution failure screenshots
├── conftest.py                # Global fixtures, storage state, screenshot hooks, Excel reporting
├── pytest.ini                 # Pytest runner configuration, markers, and live log formats
├── requirements.txt           # Python package dependencies
└── README.md                  # Comprehensive framework documentation
```

---

## 🧪 Test Suite Breakdown

### Positive Flows (`Positive_Flows` — 10 Scenarios)
Verifies end-to-end creation of valid employee records:
1. **TC_POS_EMP_001**: Create male employee with all valid mandatory details.
2. **TC_POS_EMP_002**: Create female employee with all valid mandatory details.
3. **TC_POS_EMP_003**: Create employee with Middle Name and alternative dropdown selections.
4. **TC_POS_EMP_004**: Create employee by filling only asterisk-marked (`*`) mandatory fields.
5. **TC_POS_EMP_005**: Create employee using maximum allowed (50) characters for First and Last Name.
6. **TC_POS_EMP_006**: Create employee with valid special characters (e.g. hyphen, apostrophe in names).
7. **TC_POS_EMP_007**: Validate all dropdown fields (Department, Designation, Manager, Role) are selectable.
8. **TC_POS_EMP_008**: Verify newly added employee is displayed in employee directory with unique Employee ID.
9. **TC_POS_EMP_009**: Create employee with leading/trailing whitespaces in text fields (trimmed on save).
10. **TC_POS_EMP_010**: Verify Cancel/Reset button navigates away and discards input without creating a record.

### Negative Flows (`Negative_Flows` — 20 Scenarios)
Validates robust error handling and detects application defects:
- **Blank / Missing Fields**: `TC_NEG_EMP_001` (all blank), `TC_NEG_EMP_007` (single mandatory field blank).
- **Field Limit & Whitespace**: `TC_NEG_EMP_010` (>50 chars), `TC_NEG_EMP_017` (whitespace-only names).
- **Session & Dropdowns**: `TC_NEG_EMP_015` (dropdowns text-only), `TC_NEG_EMP_016` (new employee not manager), `TC_NEG_EMP_018` (session timeout).
- **API Tests (Skipped in UI)**: `TC_NEG_EMP_011` (SQL Injection payload), `TC_NEG_EMP_013` (Invalid Department ID).
- **Application Validation Defects**:
  - `TC_NEG_EMP_002`: Numeric characters in name (`12345`).
  - `TC_NEG_EMP_003`: Invalid mobile format (<10 digits).
  - `TC_NEG_EMP_004`: Improperly formatted email address (`invalid.email`).
  - `TC_NEG_EMP_005`: Underage Date of Birth (`01-01-2025`).
  - `TC_NEG_EMP_006`: Joining Date prior to Date of Birth.
  - `TC_NEG_EMP_008`: Duplicate Personal Email.
  - `TC_NEG_EMP_009`: Duplicate Mobile Number.
  - `TC_NEG_EMP_012`: Future Date of Birth (`2050`).
  - `TC_NEG_EMP_014`: XSS script injection in name.
  - `TC_NEG_EMP_019`: Duplicate Official Email.
  - `TC_NEG_EMP_020`: Extreme future joining date (50 years in future).

---

## 🚀 Setup & Execution

### 1. Prerequisites
- Python 3.10+
- Google Chrome / Chromium

### 2. Installation
```powershell
pip install -r requirements.txt
playwright install chromium
```

### 3. Run Full Test Suite (Headless by Default)
```powershell
pytest
```

### 4. Run Specific Suites
- **Positive Test Cases Only**:
  ```powershell
  pytest tests/test_positive_flows.py
  ```
- **Negative Test Cases Only**:
  ```powershell
  pytest tests/test_negative_flows.py
  ```
- **Authentication Flow Only**:
  ```powershell
  pytest tests/test_login_flow.py
  ```

### 5. Run in Headed Browser Mode (Visual Debugging)
```powershell
pytest --headed
```

---

## 📊 Results & Artifacts

- **Excel Workbook**: Check `test_data/Swarajya-Create-test-cases (6).xlsx` for updated `Test Status`, `Automation Status`, `Auto Script ID`, `Execution Remark`, and `Last Run`.
- **Failure Screenshots**: Check `screenshots/` for full-page screenshots of failed scenarios.
- **Desktop Summary Popup**: A popup dialog automatically appears at the end of the test run showing comprehensive metrics and failure remarks.
