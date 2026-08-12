# 🏗️ Swarajya Login Automation Framework

Production-style UI automation framework for the **Swarajya Staging Portal** login page.

---

## 📋 Project Overview

| Item | Detail |
|------|--------|
| **Application** | [Swarajya Staging](https://swarajya-stg.corecotechnologies.com/) |
| **Module** | Login Page + 2FA (Google Authenticator) |
| **Tech Stack** | Python 3, Playwright, Pytest, Page Object Model |
| **Roles Tested** | Employee, Manager |
| **Total Test Cases** | 35 automatable, 7 blocked |
| **Reporting** | Desktop popup + console summary |

## ⚠️ Current Role Limitation

The application does **NOT** have role-based access control (RBAC) at present.
- Only **one valid username/password** combination exists.
- Employee and Manager tests use the **same credentials** to validate the **login flow**, not role-specific authorization.
- Role-specific authorization tests (TC_LOGIN_030–032) are marked **BLOCKED** — they are not marked FAIL.

---

## 📁 Framework Architecture

```
swarajya-automation/
├── tests/
│   └── test_login.py          # All login test functions
├── pages/
│   ├── login_page.py           # Login page POM (locators + actions)
│   └── tfa_page.py             # 2FA page POM
├── test_data/
│   ├── credentials.xlsx        # Login credentials (excluded from Git)
│   └── login_test_cases.xlsx   # Excel test case source (updated after run)
├── utils/
│   └── excel_reader.py         # Read credentials + test cases from Excel
├── reports/                    # HTML reports (generated)
├── screenshots/                # Failure screenshots (generated)
├── conftest.py                 # Pytest fixtures (browser, pages, credentials)
├── pytest.ini                  # Markers + test config
├── requirements.txt            # Python dependencies
├── .gitignore                  # Excludes secrets + generated files
└── README.md                   # This file
```

---

## 🚀 Installation

### 1. Clone & navigate

```bash
git clone <repo-url>
cd swarajya-automation
```

### 2. Create virtual environment

```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
playwright install
```

---

## 🔐 Configure Credentials

Credentials are stored in `test_data/credentials.xlsx` (excluded from Git via `.gitignore`).

### Excel Structure

| Role | Employee_ID | Password | Auth_Code | Is_Valid |
|------|-------------|----------|-----------|---------|
| Employee | 332 | test@1234 | 111111 | Yes |
| Manager | 332 | test@1234 | 111111 | Yes |

### To set up credentials:
1. Open `test_data/credentials.xlsx`
2. Enter the valid Employee ID, Password, and Google Authenticator code
3. Save the file

> ⚠️ **Never commit credentials.xlsx to Git.** It is in `.gitignore` by default.

---

## ▶️ Running Tests

### Run all tests
```bash
pytest
```

### Run positive tests only
```bash
pytest -m positive
```

### Run negative tests only
```bash
pytest -m negative
```

### Run smoke tests
```bash
pytest -m smoke
```

### Run security tests
```bash
pytest -m security
```

### Run 2FA tests
```bash
pytest -m tfa
```

### Skip blocked tests (default behavior — they are auto-skipped)
```bash
pytest -m "not blocked"
```

### Run in headless mode (Default)
```bash
pytest
```

### Run in headed mode (Visible browser)
```bash
pytest --headed
```

### Run via environment variable
```bash
# Force headless
HEADLESS=true pytest

# Force headed
HEADLESS=false pytest
```

---

## 📊 Test Reports

After a test run completes, the framework shows a desktop popup with the suite summary.

The popup and console summary show:
- Test Case ID (in test name)
- Role (Employee / Manager)
- PASS / FAIL / SKIPPED status
- Failure screenshots (auto-captured)
- Blocked test reasons

The **Excel test case file** (`test_data/login_test_cases.xlsx`) is also updated after each run with:
- `Automation_Result` column (PASS / FAIL / SKIPPED / BLOCKED)
- `Execution_Timestamp`
- `Remarks`

---

## 🧪 Test Case Mapping

### Positive Tests (Employee + Manager)

| Excel TC ID | Test Function | Status |
|-------------|--------------|--------|
| TC_EMP_001 | `test_valid_login_navigates_to_2fa[Employee]` | ✅ Automatable |
| TC_MGR_001 | `test_valid_login_navigates_to_2fa[Manager]` | ✅ Automatable |
| TC_LOGIN_001 | `test_login_page_elements_visible_TC_LOGIN_001` | ✅ Automatable |
| TC_LOGIN_002 | `test_password_field_is_masked_TC_LOGIN_002` | ✅ Automatable |
| TC_LOGIN_003 | `test_valid_login_navigates_to_2fa[Employee]` | ✅ Automatable |
| TC_LOGIN_004 | `test_valid_2fa_navigates_to_dashboard[*]` | ✅ Automatable |
| TC_LOGIN_005 | `test_2fa_back_to_login_link_TC_LOGIN_005` | ✅ Automatable |
| TC_LOGIN_006 | `test_logout_flow_TC_LOGIN_006` | ✅ Automatable |
| TC_LOGIN_007 | `test_forgot_password_link_TC_LOGIN_007` | ✅ Automatable |

### Negative Tests (Employee + Manager + General)

| Excel TC ID | Test Function | Status |
|-------------|--------------|--------|
| TC_EMP_002 | `test_invalid_employee_id[Employee]` | ✅ Automatable |
| TC_EMP_003 | `test_valid_id_wrong_password[Employee]` | ✅ Automatable |
| TC_MGR_002 | `test_invalid_employee_id[Manager]` | ✅ Automatable |
| TC_MGR_003 | `test_valid_id_wrong_password[Manager]` | ✅ Automatable |
| TC_LOGIN_009–019 | General negative tests | ✅ Automatable |
| TC_LOGIN_021 | `test_case_sensitive_password_TC_LOGIN_021` | ✅ Automatable |
| TC_LOGIN_022–023 | 2FA negative tests | ✅ Automatable |
| TC_LOGIN_026–029 | Security tests | ✅ Automatable |
| TC_LOGIN_033 | `test_repeated_failed_login_attempts_TC_LOGIN_033` | ✅ Automatable |
| TC_LOGIN_035 | `test_back_button_after_logout_TC_LOGIN_035` | ✅ Automatable |

### Blocked Tests

| Excel TC ID | Reason |
|-------------|--------|
| TC_LOGIN_020 | No locked/deactivated account available |
| TC_LOGIN_024 | Cannot control TOTP expiry |
| TC_LOGIN_025 | Cannot control TOTP rotation |
| TC_LOGIN_030 | RBAC not implemented (HR → Admin) |
| TC_LOGIN_031 | RBAC not implemented (Employee → Admin) |
| TC_LOGIN_032 | RBAC not implemented (Manager → Admin) |
| TC_LOGIN_034 | Cannot control session timeout |

### Not Applicable

| Excel TC ID | Reason |
|-------------|--------|
| TC_LOGIN_008 | Cross-browser test — requires CI matrix config |

---

## 🔧 Markers

| Marker | Description |
|--------|-------------|
| `smoke` | Core login tests for quick validation |
| `regression` | Full regression suite |
| `positive` | Happy-path tests |
| `negative` | Error-handling tests |
| `blocked` | Cannot run due to app limitations |
| `security` | SQL injection, XSS, session tests |
| `tfa` | Two-factor authentication tests |

---

## 📌 Known Blockers

1. **No RBAC**: Single login for all roles; role-specific access control tests are blocked.
2. **Static 2FA code**: The Google Authenticator code `111111` is static for staging. If this changes to real TOTP, the `auth_code` in `credentials.xlsx` must be updated per run.
3. **No account lockout**: The application may not enforce lockout after repeated failures.
4. **No session expiry control**: Cannot programmatically trigger session timeout.

---

## 🐙 GitHub Usage

```bash
git init
git add .
git commit -m "feat: Swarajya login automation framework"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

> Remember: `credentials.xlsx` is in `.gitignore` and will NOT be pushed.
> Share it securely with team members separately.
