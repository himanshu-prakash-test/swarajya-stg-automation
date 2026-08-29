# Swarajya Vendor Management Automation Framework

An enterprise-grade, data-driven test automation framework for the **Vendor Management** module of Swarajya staging (`https://swarajya-stg.corecotechnologies.com`), powered by **Python**, **Playwright**, and **Pytest**.

---

## 🏛 Framework Architecture

```
swarajya-create/vendor-management/
│
├── vendor_pages/                   # Page Object Model Layer
│   ├── base_page.py                # Reusable dynamic wait & DOM action helpers
│   ├── login_page.py               # Authentication, 2FA OTP, session caching
│   ├── vendor_page.py              # Vendor Form, modal, search grid & inactive toggle
│   └── form_executor.py            # Data-driven scenario execution & defect assertions
│
├── test_data/                      # Test Management & Credentials
│   ├── Create-Vendor-Management.xlsx # Master Excel test cases & automated status log
│   ├── credentials.xlsx            # Role-based credentials (Admin/Manager/Employee)
│   └── auth_state.json             # Cached browser session storage for rapid runs
│
├── tests/                          # Test Runners
│   ├── test_login_flow.py          # Authentication sanity & access tests
│   ├── test_positive_flows.py      # Parametrized positive creation tests (POS_01 - POS_11, 9 active)
│   └── test_negative_flows.py      # Parametrized negative validation tests (NEG_01 - NEG_18, 15 active)
│
├── vendor_utils/                   # Utilities Layer
│   ├── excel_reader.py             # Openpyxl reader & automated Excel reporting engine
│   ├── popup.py                    # Tkinter desktop summary popup dialog
│   └── logger.py                   # Standard formatted logging
│
├── screenshots/                    # Auto-captured PASS and FAIL screenshots
├── pytest.ini                      # Pytest execution options, paths, and markers
├── requirements.txt                # Python package dependencies
└── README.md                       # Architecture & user manual
```

---

## ⚡ Core Design Principles

1. **100% Dynamic Waits (Zero Static Sleeps)**:
   - Uses event-driven synchronization (`locator.wait_for(state="visible"|"hidden")`, `page.wait_for_url()`, and `wait_for_dom_ready()`) to completely eliminate flaky timing issues.

2. **Automated Master Excel Synchronization**:
   - Reads test scenarios directly from `Create-Vendor-Management.xlsx`.
   - On completion of each test, automatically writes `Test Status` (`PASS`/`FAIL`), `Automation Status` (`Automated`), `Auto Script ID` (`AUT_VENDOR_*`), and timestamped `Remarks` back to the Excel sheet.

3. **Visual Screenshots & Failure Evidence**:
   - Captures full-page screenshots for every test execution under `screenshots/` named with timestamp and test outcome (e.g. `PASS_TC_VENDOR_POS_01_*.png` and `FAIL_TC_VENDOR_NEG_02_*.png`).

4. **Desktop Summary Dialog**:
   - Renders a styled desktop summary popup (Total, Passed, Failed, Duration) immediately after the test run finishes.

5. **Staging Resilience**:
   - Built-in pre-test server health check polls staging and transparently handles transient 503 Gateway errors.

---

## 🚀 Getting Started & Execution

### 1. Installation
```powershell
cd swarajya-create\vendor-management
pip install -r requirements.txt
playwright install chromium
```

### 2. Run All Vendor Management Tests
```powershell
pytest
```

### 3. Run Only Positive Scenarios
```powershell
pytest tests/test_positive_flows.py
```

### 4. Run Only Negative Scenarios
```powershell
pytest tests/test_negative_flows.py
```

### 5. Run a Specific Test Case
```powershell
pytest -k "TC_VENDOR_POS_02"
```

### 6. Run with Visible Browser (Headed Mode)
```powershell
pytest --headed --slowmo 500
```
