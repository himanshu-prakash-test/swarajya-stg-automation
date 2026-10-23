# 🗂️ Core Shared Framework & Centralized Test Data

Universal shared architecture, central Excel test repositories, Base Page Object Models (POM), dynamic waiting utilities, and live test reporting hooks for the **Swarajya ERP Test Automation Suite**.

---

## 🏛️ Directory Architecture

```
shared/
├── config/
│   ├── __init__.py
│   └── constants.py          # Central constants, base URLs, timeouts, retry configurations
├── pages/
│   ├── __init__.py
│   ├── base_page.py          # Abstract base page encapsulating Playwright actions & dynamic waits
│   ├── login_page.py         # Universal Login POM used across login, create, and update suites
│   ├── tfa_page.py           # Two-factor authentication (2FA / OTP) dialog handler
│   └── sidebar_page.py       # Global sidebar navigation router
├── reporter/
│   ├── __init__.py
│   ├── execution_summary.py  # Universal non-blocking desktop summary popup generator
│   └── report_listener.py    # Pytest session reporting listeners and artifact bundlers
├── test_data/
│   ├── Swarajya-test-cases.xlsx  # Central workbook: test cases, step definitions, live test status
│   └── Swarajya-test-data.xlsx   # Central workbook: dynamic test data sets, credentials, environments
└── utils/
    ├── __init__.py
    ├── excel_base.py         # Core Excel parser, credential resolver, atomic cell updates
    ├── excel_loader.py       # Universal test case/data loader with strict type casting
    └── paths.py              # Cross-platform absolute project path resolver
```

---

## ⚙️ Core Architecture Principles

1. **Strictly Zero Hardcoded Values**:
   - Every module (Logins, Creates, Updates) sources its credentials, staging environment URLs, input test data rows, and expected assertions directly from `shared/test_data/Swarajya-test-cases.xlsx` and `Swarajya-test-data.xlsx`.
2. **Dynamic Waiting Standard**:
   - Zero static sleeps (`time.sleep`) across the entire repository. Playwright auto-waiting, DOM visibility checks, state synchronization, and networkidle handlers are standardized in `shared/pages/base_page.py`.
3. **Universal Live Writeback**:
   - Test execution results (`PASS`, `FAIL`, `SKIP`) and execution timestamps are automatically written back to the respective module sheets in `Swarajya-test-cases.xlsx`.
4. **CI/CD Integration**:
   - Automated GitHub Actions execution with isolated test runners, sanitized artifact names, and targeted change-detection for rapid feedback (~5 min runtime).
5. **Continuous Verification Status**:
   - Monitored and validated under GitHub Actions CI/CD Pipeline. Runs core verification suite (`swarajya-update/employee-management/tests`) on shared updates with automated artifact capture.
