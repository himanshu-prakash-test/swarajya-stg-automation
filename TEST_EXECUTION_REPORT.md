# 🏗️ Swarajya HR/Admin Automation - Test Execution Report

## ✅ Setup Complete

The following setup has been completed:

### 1. **Credentials Configured** ✓
- File: `test_data/credentials.xlsx`
- Credentials added for:
  - **Admin**: Employee ID 332, Password: test@1234, Auth Code: 111111
  - **HR**: Employee ID 332, Password: test@1234, Auth Code: 111111

### 2. **Test Framework Running** ✓
- **Framework**: Python 3.14 + Playwright + Pytest
- **Pattern**: Page Object Model (POM)
- **Test Cases**: 6 implemented (TC_ADMIN_001-003, TC_HR_001-003)

### 3. **Test Execution Results**

| Status | Count | Test Cases |
|--------|-------|-----------|
| ❌ FAILED | 2 | TC_ADMIN_001, TC_HR_001 |
| ⭕ NOT RUN | 10 | TC_MGR_001, TC_EMP_001, TC_LOGIN_001-008 |
| **TOTAL** | **12** | |

---

## 📊 Test Results Details

### Failed Tests (Reason: Network Timeout)

**TC_ADMIN_001** - Valid Admin Login + 2FA
- Role: Admin
- Status: ❌ FAILED
- Timestamp: 2026-08-13 10:55:17
- Issue: Page.goto timeout (30000ms exceeded) - Application server may be unreachable or slow to respond

**TC_HR_001** - Valid HR Login + 2FA
- Role: HR
- Status: ❌ FAILED
- Timestamp: 2026-08-13 10:55:57
- Issue: Page.goto timeout (30000ms exceeded) - Application server may be unreachable or slow to respond

### Excel Report Location
- **File**: `test_data/login_test_cases.xlsx`
- **Updated Columns**:
  - `Automation_Result`: FAIL
  - `Execution_Timestamp`: Timestamp of run
  - `Remarks`: Error details with stack trace
  - `Automation Status`: Automated

---

## 🚀 How to Run Tests

### Run All Tests (Headless)
```bash
python3 -m pytest tests/test_hr_admin.py -v --headless
```

### Run All Tests (Headed - With Browser Visible)
```bash
python3 -m pytest tests/test_hr_admin.py -v --headed
```

### Run Specific Test Markers
```bash
# Smoke tests only
pytest -m smoke

# Regression tests only
pytest -m regression

# Positive tests only
pytest -m positive

# Negative tests only
pytest -m negative

# 2FA tests only
pytest -m tfa
```

### Run Via Shell Script
```bash
bash run_hr_admin.sh
```

---

## 📁 Project Structure

```
swarajya-stg-hr-admin/
├── tests/
│   └── test_hr_admin.py              # Test cases (6 implemented)
├── pages/
│   ├── login_page.py                 # Login page POM
│   └── tfa_page.py                   # 2FA page POM
├── test_data/
│   ├── credentials.xlsx              # Login credentials (CONFIGURED ✓)
│   └── login_test_cases.xlsx         # Test case source + results (UPDATED ✓)
├── utils/
│   ├── __init__.py
│   └── excel_reader.py               # Excel utilities
├── screenshots/                      # Failure screenshots (auto-generated)
├── conftest.py                       # Pytest fixtures & hooks
├── pytest.ini                        # Test markers & config
├── requirements.txt                  # Python dependencies
├── run_hr_admin.sh                   # Test runner script
└── README.md                         # Documentation
```

---

## 📋 Test Cases Implemented

### Positive Tests (Happy Path)

| TC ID | Role | Scenario | Status |
|-------|------|----------|--------|
| TC_ADMIN_001 | Admin | Valid Admin ID + password + 2FA | ❌ FAILED |
| TC_HR_001 | HR | Valid HR ID + password + 2FA | ❌ FAILED |

### Negative Tests (Error Handling)

| TC ID | Role | Scenario | Status |
|-------|------|----------|--------|
| TC_ADMIN_002 | Admin | Invalid Admin ID + valid password | ⭕ NOT RUN |
| TC_ADMIN_003 | Admin | Valid Admin ID + wrong password | ⭕ NOT RUN |
| TC_HR_002 | HR | Invalid HR ID + valid password | ⭕ NOT RUN |
| TC_HR_003 | HR | Valid HR ID + wrong password | ⭕ NOT RUN |

### Legacy Tests (Not Implemented for HR/Admin Only)

| TC ID | Role | Status |
|-------|------|--------|
| TC_MGR_001 | Manager | ⭕ NOT IMPLEMENTED |
| TC_EMP_001 | Employee | ⭕ NOT IMPLEMENTED |
| TC_LOGIN_001-008 | General | ⭕ NOT IMPLEMENTED |

---

## ⚙️ Framework Configuration

### pytest.ini Markers
```ini
smoke       - Core HR/Admin login tests
regression  - HR/Admin regression tests
positive    - Positive flow tests
negative    - Negative flow tests
security    - Security-related tests
tfa         - Two-factor authentication tests
```

### Logging Configuration
- Log Level: INFO
- Format: `%(asctime)s | %(levelname)-7s | %(name)s | %(message)s`
- Time Format: HH:MM:SS

---

## 📊 Output Format

### 1. **Console Output**
Each test run shows:
- Test case ID
- Role (Admin/HR/Manager/Employee)
- PASS/FAIL/SKIPPED status
- Execution timestamp
- Error details (if failed)

### 2. **Excel Workbook**
`test_data/login_test_cases.xlsx` updated with:
- **Automation_Result**: PASS | FAIL | SKIPPED
- **Execution_Timestamp**: When test was run
- **Remarks**: Detailed error message or success note
- **Automation Status**: Automated

### 3. **Screenshots**
Failed tests auto-capture to `screenshots/` directory:
- File format: `{test_name}_{timestamp}.png`
- Full page screenshots

---

## 🔧 Troubleshooting

### Issue: Network Timeout (Current)
```
Error: playwright._impl._errors.TimeoutError: Page.goto: Timeout 30000ms exceeded
```

**Solutions:**
1. Check if `https://swarajya-stg.corecotechnologies.com/` is accessible
2. Increase timeout in [conftest.py](conftest.py#L44)
3. Check network connectivity
4. Verify VPN connection (if required)

### Issue: Missing Credentials
```
Error: FileNotFoundError: Missing test_data/credentials.xlsx
```

**Solution:** Ensure `test_data/credentials.xlsx` exists with ROLE, EMPLOYEE_ID, PASSWORD, AUTH_CODE columns

### Issue: Playwright Not Installed
```
Error: ModuleNotFoundError: No module named 'playwright'
```

**Solution:**
```bash
pip install -r requirements.txt
playwright install
```

---

## 📦 Dependencies

| Package | Version |
|---------|---------|
| playwright | 1.52.0 |
| pytest | 8.3.5 |
| openpyxl | 3.1.5 |
| python-dotenv | 1.1.0 |

---

## 🌐 Environment Variables

Optional environment variables:

```bash
# Base URL (default: https://swarajya-stg.corecotechnologies.com)
export SWARAJYA_BASE_URL="https://your-url"

# Headless mode (default: true)
export HEADLESS=false
```

Or use command-line options:
```bash
pytest --headed         # Run with browser visible
pytest --headless       # Run in headless mode
```

---

## 📝 Notes

- **Credentials File**: `test_data/credentials.xlsx` is ignored by Git (`.gitignore`)
- **Test Data Source**: `test_data/login_test_cases.xlsx` is the source of truth for test cases
- **Screenshots**: Stored in `screenshots/` directory, cleared before each run
- **HR/Admin Only**: This framework tests only HR and Admin roles (not Employee/Manager)
- **2FA Testing**: Google Authenticator code is static (`111111`) for staging

---

## ✨ Next Steps

1. **Verify Application Availability**: Ensure the Swarajya staging server is accessible
2. **Increase Timeout** (if needed):
   ```python
   # In conftest.py, change:
   self.page.goto(url, wait_until="networkidle", timeout=60_000)  # 60 seconds
   ```
3. **Run Negative Tests**: Once positive tests pass, run negative test cases
4. **CI/CD Integration**: Configure GitHub Actions or Jenkins for automated runs

---

**Framework Version**: 1.0  
**Last Updated**: 2026-08-13  
**Status**: ✅ Setup Complete, Ready for Testing
