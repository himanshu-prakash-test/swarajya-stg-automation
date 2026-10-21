# 🔐 Employee & Manager Login Automation Module

Automated test suite for Employee and Manager authentication workflows on the Swarajya platform.

## 📁 Module Structure
```
emp-manager/
├── conftest.py             # Fixtures, browser lifecycle, Excel reporting
├── pytest.ini              # Module pytest configuration
├── requirements.txt        # Sub-module dependencies
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── positive_flows.py   # 13 Data-driven positive test cases (strictly from Excel)
│   └── negative_flows.py   # 9 Data-driven negative test cases (strictly from Excel)
└── screenshots/            # Automated run screenshots
```

> **Note**: Shared page objects (`LoginPage`, `TfaPage`) and shared test data reader (`excel_base.py`) reside centrally in root `shared/`. All test data and test cases are strictly loaded from `shared/test_data/` (Sheet: `loginemp-manager`).

## 🚀 Execution
```bash
# Run all Employee & Manager login tests
pytest swarajya-login/emp-manager/tests

# Run only positive flows
pytest swarajya-login/emp-manager/tests/positive_flows.py

# Run only negative flows
pytest swarajya-login/emp-manager/tests/negative_flows.py

# Run in headed mode
pytest swarajya-login/emp-manager/tests --headed
```
