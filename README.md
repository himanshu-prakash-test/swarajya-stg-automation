# 🚀 Swarajya Staging Automation - HR & Admin Authentication Module

> **Branch:** `login/hr_admin`  
> **Master Repository:** [Switch to main branch](https://github.com/himanshu-prakash-test/swarajya-stg-automation/tree/main)

This branch contains strictly the **HR & Admin Authentication Module** along with the shared framework dependencies.

## 🏃 Running Tests on this Branch
```bash
# Run tests for this module
pytest swarajya-login/hr_admin/tests -v

# Run with HTML report
pytest swarajya-login/hr_admin/tests --html=report.html --self-contained-html
```

---

# 🔐 HR & Admin Login Automation Module

Automated test suite for Admin and HR authentication workflows on the Swarajya platform.

## 📁 Module Structure
```
hr_admin/
├── conftest.py             # Fixtures, browser lifecycle, Excel reporting
├── pytest.ini              # Module pytest configuration
├── requirements.txt        # Sub-module dependencies
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── positive_flows.py   # 10 Data-driven positive test cases (strictly from Excel)
│   └── negative_flows.py   # 29 Data-driven negative test cases (strictly from Excel)
└── screenshots/            # Automated run screenshots
```

> **Note**: Shared page objects (`LoginPage`, `TfaPage`) and shared test data reader (`excel_base.py`) reside centrally in root `shared/`. All test data and test cases are strictly loaded from `shared/test_data/`.

## 🚀 Execution
```bash
# Run all HR & Admin login tests
pytest swarajya-login/hr_admin/tests

# Run only positive flows
pytest swarajya-login/hr_admin/tests/positive_flows.py

# Run only negative flows
pytest swarajya-login/hr_admin/tests/negative_flows.py

# Run in headed mode
pytest swarajya-login/hr_admin/tests --headed
```

