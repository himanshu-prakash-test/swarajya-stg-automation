# 📋 Swarajya Create Operations Automation Suite

Master framework containing end-to-end automated test suites for all **Create Operations** in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), covering **Employee Management** and **Vendor Management**.

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
│   ├── consultant_pages/                # POM (base_page, consultant_page, form_executor)
│   ├── test_data/                       # Swarajya-Consultant-test-cases.xlsx
│   └── tests/                           # Positive & Negative Consultant Creation Tests
│
├── pytest.ini                           # Root Create operations pytest configuration
└── README.md                            # Create Operations Overview
```

---

## 📦 Sub-Modules Overview

| Module | Description | Test Coverage | Key Features |
| :--- | :--- | :---: | :--- |
| [**Employee Management**](file:///c:/Users/Himanshu%20Raj%20Prakash/Desktop/swarajya-stg-automation/swarajya-create/employee-management/README.md) | Automates employee onboarding, multi-tab forms, role assignments, and validation checks. | **30 Tests** (10 Pos / 20 Neg) | Datepicker handling, Excel synchronization, storage state caching |
| [**Vendor Management**](file:///c:/Users/Himanshu%20Raj%20Prakash/Desktop/swarajya-stg-automation/swarajya-create/vendor-management/README.md) | Automates vendor creation, mandatory fields, 10-digit phone regex, and confirmation modals. | **24 Tests** (9 Pos / 15 Neg) | Modal confirmation handling, strict positive assertions, search grid validation |
| **Consultant Management** | Automates consultant profile creation, contract period assignment, and rate configuration. | **Automated** | Rate validations, contract dates, consultant profile creation |

---

## 🚀 Execution Guide

### 1. Run Complete Create Operations Suite (Both Modules)
```powershell
# Run from swarajya-create root
cd swarajya-create
pytest employee-management/tests vendor-management/tests
```

### 2. Run Individual Modules
```powershell
# Run Employee Management
cd swarajya-create\employee-management
pytest

# Run Vendor Management
cd swarajya-create\vendor-management
pytest
```
