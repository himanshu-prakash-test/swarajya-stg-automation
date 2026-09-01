# Employee Update Automation

This suite runs the cases in `test_data/Swarajya-Update-Employee-test-cases.xlsx` against the staging portal.

The folder is named `emp_mgmt` rather than `emp-mgmt` because Python package names cannot contain a hyphen.

## Run

From the repository root:

```bash
./update/emp_mgmt/run_headed.sh
./update/emp_mgmt/run_headless.sh
```

The popup appears after the run with total, passed, failed, skipped, duration, and failed test names. Close it to return the shell prompt.

The popup is intentionally shown for normal runs. To run without a popup in CI or for debugging, use `PYTEST_NO_POPUP=1`.

## Configuration

The default workbook is:

`update/emp_mgmt/test_data/Swarajya-Update-Employee-test-cases.xlsx`

Override the workbook or application routing when needed:

```bash
EMPLOYEE_UPDATE_WORKBOOK=/path/to/workbook.xlsx \
EMPLOYEE_LIST_PATH=/employee/list \
EMPLOYEE_TARGET_ID=1 \
./update/emp_mgmt/run_headless.sh
```

Install dependencies from this folder with:

```bash
python3 -m pip install -r update/emp_mgmt/requirements.txt
python3 -m playwright install chromium
```

The existing login credentials remain in `test_data/credentials.xlsx`. The local employee workbook is updated with `PASS`, `FAIL`, or `SKIPPED` in `Test Status` and `Automated` in `Automation Status`.
