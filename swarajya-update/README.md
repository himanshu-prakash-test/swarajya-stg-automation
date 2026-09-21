# 🔄 Swarajya Update Operations Automation Suite

Master framework containing end-to-end automated test suites for all **Update Operations** in the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), covering **Employee Management (Update)**.

---

## 🏛️ Directory Structure

```
swarajya-update/
│
├── common/                              # 🌐 Shared Common Components
│   ├── pages/                           # Common Pages (login_page, auth_setup_page)
│   └── utils/                           # Common Utilities (excel_base)
│
├── employee-management/                 # 👤 Employee Update Management Module
│   ├── emp_update_pages/                # POM (employee_update_page, form_executor, login_page)
│   ├── emp_update_utils/                # Utilities (excel_reader)
│   ├── test_data/                       # Swarajya-Update-Employee-test-cases.xlsx, credentials.xlsx
│   ├── tests/                           # Positive, Negative, and Login Update Test Suites
│   ├── pytest.ini                       # Module execution settings
│   └── README.md                        # Employee Update Manual
│
├── purchase-orders/                     # 📑 Purchase Order Update Module
│   ├── po_update_pages/                 # Page Objects for PO update operations
│   ├── po_update_utils/                 # PO update helpers & Excel readers
│   ├── test_data/                       # credentials.xlsx, Update-Purchase-Order.xlsx
│   ├── tests/                           # Positive, Negative, and Navigation PO Update Test Suites
│   ├── pytest.ini                       # Module execution settings
│   ├── requirements.txt                 # Module dependencies
│   └── README.md                        # Purchase Order Update Manual
│
├── customer-management/                 # 👥 Customer Update Management Module
│   ├── customer_update_pages/           # Page Objects (customer_update_page, form_executor, login_page)
│   ├── customer_update_utils/           # Utilities (excel_reader)
│   ├── test_data/                       # credentials.xlsx, Update-Customer-Management.xlsx
│   ├── tests/                           # Login, Positive, and Negative Customer Update Suites
│   ├── pytest.ini                       # Module execution settings
│   ├── requirements.txt                 # Module dependencies
│   └── README.md                        # Customer Update Manual
│
├── pytest.ini                           # Suite-level pytest configuration
└── README.md                            # Update Operations Overview
```

---

## 📦 Sub-Modules Overview

| Module | Description | Test Coverage | Key Features |
| :--- | :--- | :---: | :--- |
| [**Employee Management (Update)**](employee-management/README.md) | Automates employee profile updating, field modifications, validation handling, and audit confirmation. | **26 Tests** (1 Login / 15 Pos / 10 Neg) | Dynamic field editing, modal confirmation handling, Excel reporting, storage state caching |
| [**Purchase Order (Update)**](purchase-orders/README.md) | Automates Purchase Order modification, line item adjustments, status updates, and audit verification. | **28 Tests** (1 Auth / 2 Nav / 17 Pos / 8 Neg) | Modular POM, bi-directional Excel reporting, 1-to-1 screenshot audit |
| [**Customer Management (Update)**](customer-management/README.md) | Automates Customer profile and tax detail updates, modal handling, validation checks, and audit verification. | **49 Tests** (1 Auth-Nav / 32 Pos / 16 Neg) | Multi-step navigation, dynamic field updating, Excel reporting, offline/error validation |

---

## 🚀 Quick Start

### Run All Update Tests

```bash
# From workspace root
pytest swarajya-update

# Or navigate to swarajya-update directory
cd swarajya-update
pytest
```

### Run Employee Management Update Specifically

```bash
cd swarajya-update/employee-management
pytest
```

### Run Purchase Order Update Specifically

```bash
cd swarajya-update/purchase-orders
pytest
```

### Run Customer Management Update Specifically

```bash
cd swarajya-update/customer-management
pytest
```
