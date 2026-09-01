# 🔐 Swarajya Login Automation Framework (Employee & Manager)

An enterprise-grade, data-driven test automation framework for the **Authentication & 2FA** workflows of the [Swarajya Staging Portal](https://swarajya-stg.corecotechnologies.com/), covering **Employee** and **Manager** roles. Built using **Python 3.13**, **Playwright**, **Pytest**, and **OpenPyXL**.

---

## 🏛️ Project Architecture

```
swarajya-login/
│
├── pages/                              # Page Object Model (POM) Layer
│   ├── __init__.py
│   ├── login_page.py                   # Login form actions, 503 resilience, error toasts
│   └── tfa_page.py                     # Google Authenticator 2FA code submission & validation
│
├── utils/                              # Utilities Layer
│   ├── __init__.py
│   └── excel_reader.py                 # OpenPyXL test case loader & real-time result synchronizer
│
├── test_data/                          # Test Data & Credentials
│   ├── login_test_cases.xlsx           # Master Excel test cases sheet (UI, Positive, Negative, Security)
│   └── credentials.xlsx                # Role-based credentials (Employee & Manager)
│
├── tests/                              # Test Execution Suite
│   ├── __init__.py
│   └── test_login.py                   # Complete Employee & Manager test suite
│
├── screenshots/                        # 1-to-1 Evidence Screenshots for test outcomes
├── pytest.ini                          # Pytest configuration, paths, and markers
├── requirements.txt                    # Python package dependencies
└── README.md                           # Framework Documentation
```

---

## ⚡ Core Engineering & Design Standards

### 1. Page Object Model (POM) & Dynamic Synchronization
- UI elements, locators, and interactions are encapsulated within `pages/login_page.py` and `pages/tfa_page.py`.
- Uses dynamic Playwright waits (`wait_for(state="visible")`, `wait_for_url()`) for robust and deterministic test execution.

### 2. Staging 503 Gateway Resilience
- Built-in retry loops with exponential backoff transparently handle transient HTTP 503 Gateway / Service Unavailable responses on Staging.

### 3. Bi-Directional Master Excel Reporting
- Loads test cases dynamically from `test_data/login_test_cases.xlsx`.
- Synchronizes execution status (`PASS` / `FAIL`), `Automation_Result`, timestamps, and detailed execution remarks back to Excel in real-time.

### 4. 1-to-1 Screenshot Audit & Visual Evidence
- Automatically captures full-page high-resolution PNG screenshots upon test completion in `screenshots/`.

### 5. Desktop Summary Dialog
- Renders an interactive desktop GUI summary popup (Tkinter) at the conclusion of every test run displaying overall execution metrics (Total, Passed, Failed, Duration).

---

## 📊 Test Coverage Matrix

| Test Category | Focus Scope | Key Validations |
| :--- | :--- | :--- |
| **Login UI Checks** | Page Layout & Elements | Field visibility, password masking, Forgot Password navigation |
| **Positive Login** | Employee & Manager Flows | Valid Employee ID + Password reaches 2FA; Valid OTP reaches Dashboard |
| **Login Flows** | Navigation & Session | 'Back to Login' from 2FA, session logout redirection |
| **Negative Scenarios** | Invalid & Missing Input | Invalid Employee ID, wrong password, blank fields, invalid OTP |
| **Security Tests** | Boundary & Injection | SQL Injection (`' OR '1'='1`), XSS payloads (`<script>alert()</script>`) |

---

## 🚀 Setup & Execution Guide

### 1. Installation
```powershell
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Complete Login Test Suite
```powershell
pytest
```

### 3. Run Smoke / Positive Tests Only
```powershell
pytest -m smoke
```

### 4. Run Negative Tests Only
```powershell
pytest -m negative
```

### 5. Run Security Tests (SQLi / XSS)
```powershell
pytest -m security
```

### 6. Run with Visible Browser (Headed Mode)
```powershell
pytest --headed --slowmo 400
```
