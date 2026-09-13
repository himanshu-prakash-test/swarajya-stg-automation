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
├── pytest.ini                           # Suite-level pytest configuration
└── README.md                            # Update Operations Overview
```

---

## 📦 Sub-Modules Overview

| Module | Description | Test Coverage | Key Features |
| :--- | :--- | :---: | :--- |
| [**Employee Management (Update)**](employee-management/README.md) | Automates employee profile updating, field modifications, validation handling, and audit confirmation. | **26 Tests** (1 Login / 15 Pos / 10 Neg) | Dynamic field editing, modal confirmation handling, Excel reporting, storage state caching |

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
cd swarajya-update\employee-management
pytest
```
