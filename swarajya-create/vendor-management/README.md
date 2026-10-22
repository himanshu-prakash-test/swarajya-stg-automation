# 🏢 Swarajya Vendor Management Automation Framework

An enterprise-grade, data-driven test automation framework for the **Vendor Management (Create)** module of the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), built using **Python 3.13**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 🏛️ Module Architecture

```
swarajya-create/vendor-management/
│
├── vendor_pages/                        # Page Object Model (POM) Layer
│   ├── __init__.py
│   ├── base_page.py                     # Base wrapper with dynamic waits, retry loops & toast detection
│   ├── login_page.py                    # Session authentication, 2FA OTP, role-based login
│   ├── vendor_page.py                   # Vendor form, confirmation modal, search grid, inactive toggle
│   └── form_executor.py                 # Data-driven workflow engine & strict assertion logic
│
├── vendor_utils/                        # Framework Utilities
│   ├── excel_reader.py                  # OpenPyXL test loader & real-time Excel reporting engine
│   ├── logger.py                        # Standardized colored console & file logging
│   └── popup.py                         # Desktop Tkinter execution summary popup
│
├── test_data/                           # Test Data & Session Cache
│   ├── Create-Vendor-Management.xlsx    # Master Excel test suite (Positive & Negative sheets)
│   ├── credentials.xlsx                 # Role-based credentials (Manager / Employee / Admin)
│   └── auth_state.json                  # Cached Playwright browser authentication state
│
├── tests/                               # Test Execution Suites
│   ├── __init__.py
│   ├── test_vendor_login_flow.py        # Authentication & vendor page navigation sanity
│   ├── test_vendor_positive_flows.py    # Parametrized positive creation tests (9 active)
│   └── test_vendor_negative_flows.py    # Parametrized negative validation tests (15 active)
│
├── screenshots/                         # 1-to-1 Test Evidence Screenshots
├── pytest.ini                           # Pytest execution configuration & test markers
├── requirements.txt                     # Python dependencies
└── README.md                            # Comprehensive Module Manual
```

---

## ⚡ Core Engineering & Design Standards

### 1. 100% Dynamic Synchronization (Zero Flakiness)
- Eliminates hardcoded sleeps (`time.sleep()`) entirely.
- Uses event-driven assertions: `wait_for(state="visible")`, `wait_for_dom_ready()`, and Angular Material dialog listeners.

### 2. Angular Material Confirmation Modal Handling
- Submitting a valid vendor form triggers the Angular Material confirmation dialog:
  `"Confirm Details: Do you want to add new Vendor? [No] [Yes]"`
- The framework automatically detects and clicks **Yes** for creation flows or **No** for popup dismissal tests (`TC_VENDOR_POS_08`).

### 3. Strict Positive Assertions & Staging Compliance
- **Validation Toast Check**: Asserts `"Please fill all details correctly."` does **not** appear.
- **Form Error Check**: Asserts zero inline `.mat-form-field-invalid` or `mat-error` tags.
- **Success Verification**: Asserts genuine backend success confirmation `"Vendor Added Successfully!"`.
- **Phone Number Format**: Automatically sanitizes positive phone inputs to valid 10-digit Indian mobile numbers (`98xxxxxxxx`, regex `^[6-9]\d{9}$`) required by Staging.

### 4. Bi-Directional Master Excel Synchronization
- Reads test scenarios dynamically from `Create-Vendor-Management.xlsx`.
- Real-time writeback per test execution:
  - **`Test Status`**: `PASS` / `FAIL` / `SKIP`
  - **`Automation Status`**: `Automated`
  - **`Auto Script ID`**: `AUT_VENDOR_POS_xx` / `AUT_VENDOR_NEG_xx`
  - **`Remarks`**: Detailed validation errors or creation confirmation.

### 5. 1-to-1 Screenshot Audit & Auto-Purge
- Captures exactly **1 full-page screenshot** per test case named `{STATUS}_{TC_ID}__{TIMESTAMP}.png`.
- Automated retention policy purges screenshots older than 24 hours and caps directory size at 60 files.

### 6. Desktop Summary Dialog
- Displays a native Tkinter desktop popup upon test completion summarizing Total, Passed, Failed, and Total Duration.

---

## 📊 Test Coverage Matrix

### Positive Scenarios (`Positive_Tests` — 9 Tests)
| Test ID | Test Scenario | Expected Outcome | Status |
| :--- | :--- | :--- | :---: |
| `TC_VENDOR_POS_01` | Verify navigation to Vendor Management page | Redirects to `/vendordetails` | **PASS** |
| `TC_VENDOR_POS_02` | Create new vendor with mandatory fields | Success toast `"Vendor Added Successfully!"` | **PASS** |
| `TC_VENDOR_POS_04` | Validate new vendor is listed via search | Vendor displayed in search grid | **PASS** |
| `TC_VENDOR_POS_06` | Verify cancel button functionality | Cancels form and returns to list | **PASS** |
| `TC_VENDOR_POS_07` | Create vendor with 'Active' unticked & optional fields | Inactive vendor created successfully | **PASS** |
| `TC_VENDOR_POS_08` | Verify clicking 'No' in confirmation popup stays on form | Form remains open with data intact | **PASS** |
| `TC_VENDOR_POS_09` | Search inactive vendor with 'Include Inactive' ticked | Inactive vendor listed in grid | **PASS** |
| `TC_VENDOR_POS_10` | Create vendor with max allowed characters in text fields | Vendor created successfully | **PASS** |
| `TC_VENDOR_POS_11` | Verify leading and trailing whitespace trimming | Whitespace trimmed upon saving | **PASS** |

### Negative Scenarios (`Negative_Tests` — 15 Tests)
| Test ID | Test Scenario | Validation Enforced | Status |
| :--- | :--- | :--- | :---: |
| `TC_VENDOR_NEG_01` | Attempt to create vendor with blank mandatory fields | Mandatory field validation errors | **PASS** |
| `TC_VENDOR_NEG_02` | Attempt to create vendor with duplicate email | Rejection / phone format error | **PASS** |
| `TC_VENDOR_NEG_03` | Attempt to create vendor with SQL injection payload | Sanitization / rejection | **PASS** |
| `TC_VENDOR_NEG_04` | Attempt to create vendor exceeding max characters | Input length validation error | **PASS** |
| `TC_VENDOR_NEG_05` | Attempt to create vendor with invalid email format | `"Enter valid Email ID."` | **PASS** |
| `TC_VENDOR_NEG_06` | Attempt to create vendor with invalid phone characters | `"Enter valid 10 digit mobile number."` | **PASS** |
| `TC_VENDOR_NEG_08` | Verify non-admin access fails | Authorization check verified | **PASS** |
| `TC_VENDOR_NEG_09` | Attempt to create vendor with duplicate vendor name | Rejection / format error | **PASS** |
| `TC_VENDOR_NEG_10` | Non-alphabetic characters in POC, Name, State | `"Enter valid POC Name."` | **PASS** |
| `TC_VENDOR_NEG_11` | Non-numeric characters in Tax, Phone, Days | Non-numeric validation errors | **PASS** |
| `TC_VENDOR_NEG_13` | Attempt to create vendor after session timeout | Session invalidation handled | **PASS** |
| `TC_VENDOR_NEG_14` | Offline / server down simulation | Handled via network mock (`set_offline`) | **PASS** |
| `TC_VENDOR_NEG_16` | Percentage field > 100% or < 0% | `"Valid TDS % (0-100) is required."` | **PASS** |
| `TC_VENDOR_NEG_17` | Negative Payment Terms (Days) | Validation error enforced | **PASS** |
| `TC_VENDOR_NEG_18` | XSS payload in Name field (`<script>alert()</script>`) | Sanitization & rejection | **PASS** |

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites & Installation
```powershell
cd swarajya-create\vendor-management
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Complete Vendor Suite
```powershell
pytest
```

### 3. Run Positive Tests Only
```powershell
pytest tests/test_vendor_positive_flows.py
```

### 4. Run Negative Tests Only
```powershell
pytest tests/test_vendor_negative_flows.py
```

### 5. Run a Specific Test Case
```powershell
pytest -k "TC_VENDOR_POS_02"
```

### 6. Run in Headed Browser Mode (Visible UI)
```powershell
pytest --headed --slowmo 400
```
