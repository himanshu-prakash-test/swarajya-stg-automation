# Create Consultant Management Test Automation

This module automates the end-to-end testing of the **Create Consultant Management** workflow in the Swarajya ERP application.

## Architecture

Aligned with `swarajya-create/invoice-management` and framework standards:
- **Zero Hardcoding**: All base URLs, credentials, form inputs, scenarios, and expected outcomes are dynamically read from central Excel workbooks (`shared/test_data/Swarajya-test-cases.xlsx` and `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `createconsultant_mgmt`]).
- **Dynamic Waits**: Playwright auto-waits, visibility checks, networkidle synchronization, and dialog state handlers (no static sleeps).
- **Form Executor**: Dynamic field mapping and population via `ConsultantFormExecutor`.
- **Live Excel Reporting**: Automatically updates the `Test Status` and `Remarks / Defect Observed` columns in `Swarajya-test-cases.xlsx`.
- **Artifacts**: 1-to-1 screenshots saved in `screenshots/` and HTML reports with execution summaries.
- **CI/CD Integration**: Fully integrated into GitHub Actions with automated headless testing, dynamic artifact sanitization, and full positive/negative suite regression coverage.

## Directory Structure

```
swarajya-create/consultant-management/
├── conftest.py                       # Fixtures, browser session caching, reporting hooks
├── pytest.ini                        # Module-level pytest configuration
├── requirements.txt                  # Dependencies
├── consultant_pages/
│   ├── __init__.py
│   ├── consultant_page.py            # Page Object Model for Consultant Dashboard & Create form
│   └── form_executor.py              # Dynamic data-driven form executor
├── consultant_utils/
│   ├── __init__.py
│   └── excel_reader.py               # Excel reader delegating to shared/utils/excel_base.py
├── screenshots/                      # 1-to-1 execution screenshots
└── tests/
    ├── test_consultant_positive_flows.py  # 22 Positive test scenarios (TC_CONSULTANT_POS_01 - POS_22)
    └── test_consultant_negative_flows.py  # 25 Negative & validation scenarios (TC_CONSULTANT_NEG_01 - NEG_25)
```

## Running Tests

From module directory:
```bash
pytest -v
```

Run positive flows only:
```bash
pytest tests/test_consultant_positive_flows.py -v
```

Run negative flows only:
```bash
pytest tests/test_consultant_negative_flows.py -v
```

---

## 🔄 CI/CD Pipeline Status
- **Status**: Integrated & Verified ✅
- **Automation Pipeline**: [Swarajya Automation CI/CD Pipeline](https://github.com/himanshu-prakash-test/swarajya-stg-automation/actions)
- **Supported Execution**: Headless and Headed modes via GitHub Actions `workflow_dispatch`.

