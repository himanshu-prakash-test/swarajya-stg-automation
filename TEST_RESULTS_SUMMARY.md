# Test Results Summary - Swarajya HR/Admin Automation

**Execution Date:** 2026-08-13  
**Status:** ✅ ALL TESTS PASSED (6/6)  
**Execution Time:** 21.10 seconds  
**Test Framework:** pytest 8.3.5 + Playwright 1.52.0

---

## Test Execution Results

```
============================= 6 passed in 21.10s ===============================
```

### Detailed Test Results

| Test Case ID | Test Type | Status | Role | Description |
|--------------|-----------|--------|------|-------------|
| TC_ADMIN_001 | Positive | ✅ PASSED | Admin | Valid Admin Login + 2FA |
| TC_HR_001 | Positive | ✅ PASSED | HR | Valid HR Login + 2FA |
| TC_ADMIN_002 | Negative | ✅ PASSED | Admin | Invalid Employee ID |
| TC_HR_002 | Negative | ✅ PASSED | HR | Invalid Employee ID |
| TC_ADMIN_003 | Negative | ✅ PASSED | Admin | Wrong Password |
| TC_HR_003 | Negative | ✅ PASSED | HR | Wrong Password |

---

## Page Object Model (POP) Architecture

### LoginPage - Invalid Login Scenarios

**Location:** [pages/login_page.py](pages/login_page.py)

#### Key Methods for Invalid Login Testing

1. **`enter_employee_id(employee_id: str)`**
   - Enters employee ID into the login form
   - Used for both valid and invalid ID scenarios
   - Example invalid inputs tested:
     - Admin: `INVALID_ADMIN` (13 characters)
     - HR: `INVALID_HR` (10 characters)

2. **`enter_password(password: str)`**
   - Enters password into the login form
   - Used for both valid and wrong password scenarios
   - Wrong password test uses: `Wrong@123`

3. **`click_sign_in()`**
   - Clicks the "Sign In" button
   - Triggers validation on the backend

4. **`get_error_message(timeout=None) -> str`**
   - **Critical for invalid login validation**
   - Waits for error snackbar to appear (default: 5 seconds)
   - Returns error message text
   - Used in negative test cases to assert error is displayed

5. **`is_error_displayed(timeout=None) -> bool`**
   - Returns True if error snackbar is visible
   - Returns False if timeout occurs
   - Used for error state validation

6. **`get_current_url() -> str`**
   - Gets current page URL
   - Used to verify user didn't reach 2FA page on invalid login

#### Locators Used

```python
@property
def employee_id_input(self):
    return self.page.get_by_label("Employee ID")

@property
def password_input(self):
    return self.page.get_by_label("Password")

@property
def sign_in_button(self):
    return self.page.get_by_role("button", name="Sign In")

@property
def error_snackbar(self):
    return self.page.locator("simple-snack-bar")
```

---

## Test Case Implementation

### Invalid Employee ID Test (TC_ADMIN_002, TC_HR_002)

```python
@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize(
    "role",
    ["Admin", "HR"],
    ids=lambda r: ROLE_TC[r]["invalid_id"],
)
def test_invalid_employee_id(role, login_page):
    creds = credentials(role)
    invalid_id = "INVALID_ADMIN" if role == "Admin" else "INVALID_HR"

    # Step 1: Enter invalid employee ID
    login_page.enter_employee_id(invalid_id)
    
    # Step 2: Enter valid password
    login_page.enter_password(creds["password"])
    
    # Step 3: Click Sign In
    login_page.click_sign_in()

    # Step 4: Verify error message appears
    error = login_page.get_error_message(timeout=5_000)
    assert error, f"{role} invalid-ID test did not display an error message"
    
    # Step 5: Verify user didn't reach 2FA
    assert "/tfa-authcode/" not in login_page.get_current_url(), \
        f"{role} invalid ID incorrectly reached 2FA"
```

### Wrong Password Test (TC_ADMIN_003, TC_HR_003)

```python
@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize(
    "role",
    ["Admin", "HR"],
    ids=lambda r: ROLE_TC[r]["wrong_password"],
)
def test_wrong_password(role, login_page):
    creds = credentials(role)

    # Step 1: Enter valid employee ID
    login_page.enter_employee_id(creds["employee_id"])
    
    # Step 2: Enter wrong password
    login_page.enter_password("Wrong@123")
    
    # Step 3: Click Sign In
    login_page.click_sign_in()

    # Step 4: Verify error message appears
    error = login_page.get_error_message(timeout=5_000)
    assert error, f"{role} wrong-password test did not display an error message"
    
    # Step 5: Verify user didn't reach 2FA
    assert "/tfa-authcode/" not in login_page.get_current_url(), \
        f"{role} wrong password incorrectly reached 2FA"
```

---

## Valid Login Test (For Reference)

### Successful Login Flow (TC_ADMIN_001, TC_HR_001)

```python
@pytest.mark.smoke
@pytest.mark.positive
@pytest.mark.tfa
@pytest.mark.parametrize(
    "role",
    ["Admin", "HR"],
    ids=lambda r: ROLE_TC[r]["valid"],
)
def test_valid_login_and_2fa(page, base_url, role):
    creds = credentials(role)

    # Step 1: Navigate and login
    login = LoginPage(page, base_url)
    login.navigate()
    login.login(creds["employee_id"], creds["password"])

    # Step 2: Verify 2FA page loaded
    tfa = TfaPage(page, base_url)
    tfa.wait_for_tfa_page(timeout=15_000)
    
    assert tfa.is_on_tfa_page(), \
        f"{role} valid credentials did not reach 2FA"
    assert tfa.is_auth_code_input_visible(), \
        f"{role} 2FA auth-code field is not visible"

    # Step 3: Submit 2FA code
    tfa.submit_auth_code(creds["auth_code"])

    # Step 4: Verify dashboard loaded
    assert tfa.is_dashboard_loaded(timeout=15_000), \
        f"{role} valid credentials did not reach dashboard"
```

---

## Screenshots

**Status:** No screenshots available (all tests passed ✅)

**Note:** Screenshots are automatically captured on test failures in the `screenshots/` directory.

### How to Generate Screenshots on Failure:
1. Modify test data to trigger failures
2. Run tests: `pytest tests/test_hr_admin.py -v`
3. Failed test screenshots will be in `screenshots/` folder with timestamp

### Screenshot Capture Configuration (conftest.py)

```python
@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(request, page):
    yield
    
    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = request.node.name.replace("[", "_").replace("]", "").replace("/", "_")
        path = os.path.join(SCREENSHOTS_DIR, f"{name}_{timestamp}.png")
        page.screenshot(path=path, full_page=True)
```

---

## Test Markers

Used for organized test execution:

```python
@pytest.mark.smoke        # Quick smoke tests
@pytest.mark.positive     # Positive scenarios (valid login)
@pytest.mark.negative     # Negative scenarios (invalid login)
@pytest.mark.regression   # Regression tests
@pytest.mark.tfa          # 2FA tests
```

### Run Tests by Marker:
```bash
# Only positive tests
pytest -m positive

# Only negative tests
pytest -m negative

# Smoke tests
pytest -m smoke

# Exclude tfa tests
pytest -m "not tfa"
```

---

## Execution Modes

### Headless Mode (Default - CI/CD)
```bash
pytest tests/test_hr_admin.py -v
# or explicitly:
pytest tests/test_hr_admin.py -v --headless
```

### Headed Mode (Visible Browser)
```bash
pytest tests/test_hr_admin.py -v --headed
```

---

## Test Data

**File:** `test_data/login_test_cases.xlsx`

### Admin Credentials
- Employee ID: `332`
- Password: `test@1234`
- Auth Code: `111111`

### HR Credentials
- Employee ID: `332`
- Password: `test@1234`
- Auth Code: `111111`

---

## Conclusion

✅ **All 6 test cases passing**  
✅ **Invalid login scenarios validated**  
✅ **Error handling verified**  
✅ **2FA flow validated**  
✅ **Page Object Model working correctly**  

The automation framework successfully tests both positive (valid login + 2FA) and negative (invalid ID, wrong password) scenarios for Admin and HR roles.
