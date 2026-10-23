# Create Purchase Order Automation Suite

Automated end-to-end regression and smoke test suites for Swarajya **Create Purchase Order** module, powered by Playwright and Pytest.

## Overview
- **Architecture**: Modular Page Object Model (`POPage`, `POFormExecutor`) mirroring `invoice-management`.
- **Data Source**: Strictly data-driven from central shared Excel workbooks (`shared/test_data/Swarajya-test-cases.xlsx` & `shared/test_data/Swarajya-test-data.xlsx` [Sheet: `createpurchase_order`]).
- **Zero Hardcoding**: Credentials, Base URL, input test data, descriptions, and validations are dynamically resolved.
- **Dynamic Waits**: Playwright dynamic state waiting without static sleeps.
- **Live Reporting**: Test results write directly to `Swarajya-test-cases.xlsx`, HTML reports generated under `reports/`, and 1-to-1 screenshots saved under `screenshots/`.
- **CI/CD Integration**: Fully integrated into GitHub Actions with automated headless testing, dynamic artifact sanitization, and regression test validation.

## Directory Structure
```
swarajya-create/purchase-order/
├── conftest.py               # Shared session fixtures, auth caching, reporting hooks
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Python dependencies
├── README.md                 # Module documentation
├── po_pages/
│   ├── __init__.py
│   ├── po_page.py            # Page Object Model for Purchase Order
│   └── form_executor.py      # Dynamic form filling executor
├── po_utils/
│   ├── __init__.py
│   └── excel_reader.py       # Excel delegation to shared.utils.excel_base
├── screenshots/              # 1-to-1 captured execution screenshots
└── tests/
    ├── test_po_positive_flows.py  # 18 Positive test cases (TC_CPO_POS_01 - 18)
    └── test_po_negative_flows.py  # 15 Negative test cases (TC_CPO_NEG_01 - 15)
```

## Running Tests Locally
```bash
# Run all Create Purchase Order tests
pytest swarajya-create/purchase-order/tests -v

# Run positive tests only
pytest swarajya-create/purchase-order/tests -m positive -v

# Run negative tests only
pytest swarajya-create/purchase-order/tests -m negative -v

# Run headed
pytest swarajya-create/purchase-order/tests --headed
```
