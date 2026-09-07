# 🏢 Swarajya Consultant Management Automation Framework

An enterprise-grade, data-driven test automation framework for the **Consultant Management (Create)** module of the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), built using **Python 3.13 / 3.14**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 🏛️ Module Architecture

```
swarajya-create/consultant-management/
│
├── consultant_pages/                       # Page Object Model (POM) Layer
│   ├── __init__.py
│   ├── base_page.py                        # Base wrapper with dynamic waits, retry loops & toast detection
│   ├── login_page.py                       # Session authentication, 2FA OTP, role-based login
│   ├── consultant_page.py                  # Consultant form, confirmation modal, search grid, inactive toggle
│   └── form_executor.py                    # Data-driven workflow engine & strict assertion logic
│
├── consultant_utils/                       # Framework Utilities
│   ├── __init__.py
│   ├── excel_reader.py                     # OpenPyXL test loader & real-time Excel reporting engine
│   ├── logger.py                           # Standardized colored console & file logging
│   └── popup.py                            # Desktop Tkinter execution summary popup
│
├── test_data/                              # Test Data & Session Cache
│   ├── Create-Consultant-Management.xlsx   # Master Excel test suite (Positive & Negative sheets)
│   ├── credentials.xlsx                    # Role-based credentials (Manager / Employee / Admin)
│   └── auth_state.json                     # Cached Playwright browser authentication state
│
├── tests/                                  # Test Execution Suites
│   ├── __init__.py
│   ├── test_consultant_login_flow.py       # Authentication & consultant page navigation sanity
│   ├── test_consultant_positive_flows.py   # Parametrized positive creation tests (22 active)
│   └── test_consultant_negative_flows.py   # Parametrized negative validation tests (25 active)
│
├── screenshots/                            # 1-to-1 Test Evidence Screenshots
├── conftest.py                             # Pytest session setup, browser fixtures & result writeback
├── pytest.ini                              # Pytest execution configuration & test markers
├── requirements.txt                        # Python dependencies
└── README.md                               # Comprehensive Module Manual
```

---

## ⚡ Core Engineering & Design Standards

### 1. 100% Dynamic Synchronization (Zero Flakiness)
- Eliminates hardcoded sleeps (`time.sleep()`) through event-driven assertions: `wait_for(state="visible")`, `wait_for_dom_ready()`, and Angular Material dialog listeners.

### 2. Angular Material Confirmation Modal Handling
- Submitting a valid consultant form triggers the Angular Material confirmation dialog:
  `"Confirm Details: Do you want to add new Consultant? [No] [Yes]"`
- The framework automatically detects and clicks **Yes** for creation flows or **No** for popup dismissal tests (`TC_CONSULTANT_POS_10` / `TC_CONSULTANT_NEG_07`).

### 3. Strict Positive Assertions & Staging Compliance
- **Validation Toast Check**: Asserts validation error messages do not appear during valid submissions.
- **Form Error Check**: Asserts zero inline `.mat-form-field-invalid` or `mat-error` tags.
- **Success Verification**: Verifies genuine backend success confirmation and dashboard visibility.

### 4. Bi-Directional Master Excel Synchronization
- Reads test scenarios dynamically from `Create-Consultant-Management.xlsx`.
- Real-time writeback per test execution:
  - **`Test Status`**: `PASS` / `FAIL` / `SKIP`
  - **`Automation Status`**: `Automated`
  - **`Auto Script ID`**: `AUT_CONSULTANT_POS_xx` / `AUT_CONSULTANT_NEG_xx`
  - **`Remarks`**: Detailed validation errors or creation confirmation.

### 5. 1-to-1 Screenshot Audit
- Captures full-page screenshots per test case named `{STATUS}_{TC_ID}__{TIMESTAMP}.png` inside `screenshots/`.

### 6. Desktop Summary Dialog
- Displays a native desktop popup upon test completion summarizing Total, Passed, Failed, and Total Duration.

---

## 📊 Test Coverage Matrix

### Positive Scenarios (`Positive_Tests` — 22 Tests)
| Test ID | Test Scenario | Expected Outcome | Status |
| :--- | :--- | :--- | :---: |
| `TC_CONSULTANT_POS_01` | Verify navigation to Consultant Dashboard | Redirects to `/consultantdetails` | **PASS** |
| `TC_CONSULTANT_POS_02` | Verify existing consultant records displayed on dashboard | Table rows and data loaded | **PASS** |
| `TC_CONSULTANT_POS_03` | Verify 'Add Consultant' form opens with all fields | Form fields rendered | **PASS** |
| `TC_CONSULTANT_POS_04` | Create new consultant with mandatory fields | Consultant created | **PASS** |
| `TC_CONSULTANT_POS_05` | Verify consultant creation save & confirmation popup | Popup confirmed & saved | **PASS** |
| `TC_CONSULTANT_POS_06` | Validate new consultant is listed via search | Displayed in search grid | **PASS** |
| `TC_CONSULTANT_POS_07` | Create consultant with optional Middle Name, Address, Branch | Optional fields persisted | **PASS** |
| `TC_CONSULTANT_POS_08` | Verify Cancel button functionality during creation | Returns to dashboard | **PASS** |
| `TC_CONSULTANT_POS_09` | Create consultant with 'Active' unticked (Inactive) | Inactive consultant saved | **PASS** |
| `TC_CONSULTANT_POS_10` | Verify selecting 'No' on confirmation popup stays on form | Form remains open | **PASS** |
| `TC_CONSULTANT_POS_11` | Search inactive consultant with 'Include Inactive' filter | Inactive record listed | **PASS** |
| `TC_CONSULTANT_POS_12` | Creation with maximum allowed characters in text fields | Boundary length accepted | **PASS** |
| `TC_CONSULTANT_POS_13` | Verify leading and trailing whitespace trimming | Whitespace trimmed | **PASS** |
| `TC_CONSULTANT_POS_14` | Verify consultant details edited via Actions edit icon | Edit form opens | **PASS** |
| `TC_CONSULTANT_POS_15` | Verify Account Number is masked on dashboard | Account masked with `****` | **PASS** |
| `TC_CONSULTANT_POS_16` | Verify Status toggle switches Active / Inactive | Status toggled | **PASS** |
| `TC_CONSULTANT_POS_17` | Verify pagination works correctly on dashboard | Pagination controls active | **PASS** |
| `TC_CONSULTANT_POS_18` | Verify TDS Percentage saved as valid numeric value | TDS numeric validated | **PASS** |
| `TC_CONSULTANT_POS_19` | Verify Account Number masking format consistency | Masking format consistent | **PASS** |
| `TC_CONSULTANT_POS_20` | Verify Bank Name field stores bank name properly | Bank name saved | **PASS** |
| `TC_CONSULTANT_POS_21` | Verify Consultant Name fields reject numeric characters | Name validated | **PASS** |
| `TC_CONSULTANT_POS_22` | Verify Monthly Fees enforces valid minimum value | Min fees enforced | **PASS** |

### Negative Scenarios (`Negative_Tests` — 25 Tests)
| Test ID | Test Scenario | Validation Enforced | Status |
| :--- | :--- | :--- | :---: |
| `TC_CONSULTANT_NEG_01` | Blank mandatory fields | Required validation errors | **PASS** |
| `TC_CONSULTANT_NEG_02` | Duplicate Personal Email | Duplicate email error | **PASS** |
| `TC_CONSULTANT_NEG_03` | SQL injection payload in First Name | Input sanitized / rejected | **PASS** |
| `TC_CONSULTANT_NEG_04` | First Name exceeding max length | Length restriction error | **PASS** |
| `TC_CONSULTANT_NEG_05` | Invalid Personal Email format | `"Enter valid Email ID."` | **PASS** |
| `TC_CONSULTANT_NEG_06` | Non-numeric characters in Phone | Phone format validation error | **PASS** |
| `TC_CONSULTANT_NEG_07` | Verify creation aborted clicking 'No' in popup | Cancelled cleanly | **PASS** |
| `TC_CONSULTANT_NEG_08` | Non-admin role access restriction | Authorization verified | **PASS** |
| `TC_CONSULTANT_NEG_09` | Invalid IFSC Code format | IFSC format validation | **FAIL** *(Staging Bug)* |
| `TC_CONSULTANT_NEG_10` | Non-alphabetic in Names and Bank Name | Name format validation error | **PASS** |
| `TC_CONSULTANT_NEG_11` | Non-numeric in Fees, TDS, Account Number | Numeric type validation error | **PASS** |
| `TC_CONSULTANT_NEG_12` | TDS Percentage > 100% or < 0% | Range validation error | **PASS** |
| `TC_CONSULTANT_NEG_13` | Negative Monthly Fees (`-5000`) | Rejection of negative fees | **PASS** |
| `TC_CONSULTANT_NEG_14` | XSS payload in First Name | XSS sanitized / rejected | **PASS** |
| `TC_CONSULTANT_NEG_15` | Account Number shorter than min length | Length validation error | **PASS** |
| `TC_CONSULTANT_NEG_16` | Session timeout during creation | Skipped (requires server kill) | **SKIP** |
| `TC_CONSULTANT_NEG_17` | Network idle / server unreachable | Skipped (requires mock proxy) | **SKIP** |
| `TC_CONSULTANT_NEG_18` | Failed creation not listed on dashboard | Absence verified in table | **PASS** |
| `TC_CONSULTANT_NEG_19` | Unselected Account Type dropdown | Account type required error | **PASS** |
| `TC_CONSULTANT_NEG_20` | Duplicate Account Number | Duplicate account error | **PASS** |
| `TC_CONSULTANT_NEG_21` | Digits in Name (`Ravindra1`) | Rejection of digits in name | **PASS** |
| `TC_CONSULTANT_NEG_22` | Blank TDS Percentage | Blank TDS rejected | **PASS** |
| `TC_CONSULTANT_NEG_23` | Code string in Bank Name | Format validation error | **PASS** |
| `TC_CONSULTANT_NEG_24` | Near-duplicate consultant (inserted digits) | Duplicate check warning | **PASS** |
| `TC_CONSULTANT_NEG_25` | Account number masking length normalization | Masking pattern verified | **PASS** |

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites & Installation
```bash
cd swarajya-create/consultant-management
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Complete Consultant Suite
```bash
pytest
```

### 3. Run Positive Tests Only
```bash
pytest tests/test_consultant_positive_flows.py
# or directly:
python3 tests/test_consultant_positive_flows.py --headless
```

### 4. Run Negative Tests Only
```bash
pytest tests/test_consultant_negative_flows.py
# or directly:
python3 tests/test_consultant_negative_flows.py --headless
```

### 5. Run Authentication Sanity Test
```bash
pytest tests/test_consultant_login_flow.py
```

### 6. Run a Specific Test Case
```bash
pytest -k "TC_CONSULTANT_POS_04"
```

### 7. Run in Headed Browser Mode (Visible UI)
```bash
pytest --headed --slowmo 400
```
