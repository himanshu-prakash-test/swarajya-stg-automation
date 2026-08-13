# Swarajya STG - HR + Admin Automation

This repository is an HR/Admin-only implementation based on the
`features/himanshu` Playwright/Pytest framework.

## Implemented test cases

- TC_ADMIN_001 - Valid Admin ID + password + 2FA
- TC_ADMIN_002 - Invalid Admin ID + valid password
- TC_ADMIN_003 - Valid Admin ID + incorrect password
- TC_HR_001 - Valid HR ID + password + 2FA
- TC_HR_002 - Invalid HR ID + valid password
- TC_HR_003 - Valid HR ID + incorrect password

Employee and Manager tests are intentionally not included or executed.

## 1. Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

## 2. Credentials

Create:

`test_data/credentials.xlsx`

with columns:

`ROLE | EMPLOYEE_ID | PASSWORD | AUTH_CODE`

Add exactly the HR and Admin credentials you are authorized to use.

The credentials workbook is ignored by Git.

## 3. Test cases

`test_data/login_test_cases.xlsx` is the Excel test-case source.

After each test, the matching row is updated with:

- Automation_Result
- Execution_Timestamp
- Remarks
- Automation Status = Automated

## 4. Run HR + Admin

Visible browser:

```bash
pytest tests/test_hr_admin.py --headed -v -s
```

Headless:

```bash
pytest tests/test_hr_admin.py --headless -v -s
```

HR only:

```bash
pytest tests/test_hr_admin.py -k 'TC_HR' --headed -v -s
```

Admin only:

```bash
pytest tests/test_hr_admin.py -k 'TC_ADMIN' --headed -v -s
```

## 5. Results

- Screenshots of failures: `screenshots/`
- Test-case results: `test_data/login_test_cases.xlsx`

## 6. Portal

Default:

`https://swarajya-stg.corecotechnologies.com`

Override:

```bash
SWARAJYA_BASE_URL="https://swarajya-stg.corecotechnologies.com" pytest tests/test_hr_admin.py --headed
```

## Security

Never commit `test_data/credentials.xlsx`, passwords, or authentication secrets.
