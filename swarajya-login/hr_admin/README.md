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

> **Note**: Shared page objects (`LoginPage`, `TfaPage`) and shared test data reader (`excel_reader.py`) reside centrally in `swarajya-login/common/`. All test data and test cases are strictly loaded from `shared/test_data/`.

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
