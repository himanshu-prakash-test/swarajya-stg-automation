# 📋 Swarajya Create Operations Automation Suite

Master framework containing end-to-end automated test suites for all **Create Operations** in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), covering **Employee Management**, **Vendor Management**, and **Consultant Management**.

---

## 🏛️ Directory Structure

```
swarajya-create/
│
├── employee-management/                 # 👤 Employee Management Module
│   ├── emp_pages/                       # POM (base_page, login_page, employee_page, form_executor)
│   ├── emp_utils/                       # Utilities (excel_reader, logger, popup)
│   ├── test_data/                       # Swarajya-Create-test-cases (6).xlsx, credentials.xlsx
│   ├── tests/                           # Positive & Negative Employee Test Suites
│   ├── screenshots/                     # Test evidence screenshots
│   ├── pytest.ini                       # Module execution settings
│   └── README.md                        # Employee Management Manual
│
├── vendor-management/                   # 🏢 Vendor Management Module
│   ├── vendor_pages/                    # POM (base_page, login_page, vendor_page, form_executor)
│   ├── vendor_utils/                    # Utilities (excel_reader, logger, popup)
│   ├── test_data/                       # Create-Vendor-Management.xlsx, credentials.xlsx
│   ├── tests/                           # Positive & Negative Vendor Test Suites
│   ├── screenshots/                     # Test evidence screenshots
│   ├── pytest.ini                       # Module execution settings
│   └── README.md                        # Vendor Management Manual
│
├── consultant-management/               # 💼 Consultant Management Module
│   ├── consultant_pages/                # POM (base_page, login_page, consultant_page, form_executor)
│   ├── consultant_utils/                # Utilities (excel_reader, logger, popup)
│   ├── test_data/                       # Create-Consultant-Management.xlsx, credentials.xlsx
│   ├── tests/                           # Positive & Negative Consultant Creation Suites
│   ├── screenshots/                     # Test evidence screenshots
│   ├── pytest.ini                       # Module execution settings
│   └── README.md                        # Consultant Management Manual
│
├── customer-management/                 # 👥 Customer Management Module
│   ├── customer_pages/                  # POM (base_page, login_page, customer_page, form_executor)
│   ├── customer_utils/                  # Utilities (excel_reader)
│   ├── test_data/                       # Create-Customer-Management.xlsx, credentials.xlsx
│   ├── tests/                           # Positive & Negative Customer Creation Suites
│   ├── screenshots/                     # Test evidence screenshots
│   ├── pytest.ini                       # Module execution settings
│   └── README.md                        # Customer Management Manual
│
├── purchase-order/                      # 📦 Purchase Order Management Module
│   ├── po_pages/                        # POM (base_page, login_page, po_page, form_executor)
│   ├── po_utils/                        # Utilities (excel_reader)
│   ├── test_data/                       # Create-Purchase-Order-Test-Cases.xlsx, credentials.xlsx, sample_po.pdf
│   ├── tests/                           # Positive & Negative PO Creation Suites
│   ├── screenshots/                     # Test evidence screenshots
│   ├── pytest.ini                       # Module execution settings
│   └── README.md                        # Purchase Order Management Manual
│
├── pytest.ini                           # Root Create operations pytest configuration
└── README.md                            # Create Operations Overview
```

---

## 📦 Sub-Modules Overview

| Module | Description | Test Coverage | Key Features |
| :--- | :--- | :---: | :--- |
| [**Employee Management**](employee-management/README.md) | Automates employee onboarding, multi-tab forms, role assignments, and validation checks. | **30 Tests** (10 Pos / 20 Neg) | Datepicker handling, Excel synchronization, storage state caching |
| [**Vendor Management**](vendor-management/README.md) | Automates vendor creation, mandatory fields, 10-digit phone regex, and confirmation modals. | **24 Tests** (9 Pos / 15 Neg) | Modal confirmation handling, strict positive assertions, search grid validation |
| [**Consultant Management**](consultant-management/README.md) | Automates consultant profile creation, contract period assignment, rates, and bank details. | **47 Tests** (22 Pos / 25 Neg) | Modal confirmation handling, dynamic grid search, rate validations, Excel reporting |
| [**Customer Management**](customer-management/README.md) | Automates customer onboarding, 20 fields, currency/tax/terms variants, dropdown options, IGST switch, confirmation dialogs (Yes/No), and grid search. | **36 Tests** (2 Login / 26 Pos / 8 Neg) | Full profile creation, confirmation popup (Yes/No), search verification, dropdown & switch testing, session timeout, Excel reporting |
| [**Purchase Order**](purchase-order/README.md) | Automates PO creation, customer mapping, base/tax/total amounts, PDF document upload, and status validation. | **20 Tests** (2 Login / 10 Pos / 8 Neg) | Direct PO navigation, modal form automation, file upload, calculation validations, Excel synchronization |

---

## 🚀 Execution Guide

### 1. Run Complete Create Operations Suite
```powershell
# Run from swarajya-create root
cd swarajya-create
pytest
```

### 2. Run Individual Modules
```powershell
# Run Employee Management
cd swarajya-create\employee-management
pytest

# Run Vendor Management
cd swarajya-create\vendor-management
pytest

# Run Consultant Management
cd swarajya-create\consultant-management
pytest

# Run Customer Management
cd swarajya-create\customer-management
pytest
```
