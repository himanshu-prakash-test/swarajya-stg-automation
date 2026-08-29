# Swarajya Login Automation

Playwright + Pytest automation for the [Swarajya Staging](https://swarajya-stg.corecotechnologies.com/) login page, covering Employee and Manager roles.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
playwright install
```

## Credentials

Create `test_data/credentials.xlsx` (excluded from git) with columns:

| Role | Employee_ID | Password | Auth_Code | Is_Valid |
|------|-------------|----------|-----------|---------|
| Employee | 332 | test@1234 | 111111 | Yes |
| Manager  | 332 | test@1234 | 111111 | Yes |

## Running tests

```bash
pytest                  # all tests, headless
pytest --headed         # visible browser
pytest -m smoke         # smoke tests only
pytest -m negative      # negative tests only
pytest -m security      # security tests
pytest -m "not blocked" # skip blocked tests
```

## Project structure

```
├── tests/test_login.py       # test cases
├── pages/
│   ├── login_page.py         # login page object
│   └── tfa_page.py           # 2FA page object
├── utils/excel_reader.py     # Excel I/O
├── test_data/
│   ├── credentials.xlsx      # credentials (gitignored)
│   └── login_test_cases.xlsx # test case mapping
├── conftest.py               # fixtures, popup, Excel hooks
├── pytest.ini                # markers and config
└── requirements.txt
```

## Notes

- The app has no RBAC — Employee and Manager use the same credentials.
- RBAC tests (TC_LOGIN_030–032) are marked `skip`.
- A popup with results appears after each run.
- Screenshots are auto-captured on failure under `screenshots/`.
