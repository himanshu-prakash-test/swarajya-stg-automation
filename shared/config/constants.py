"""
Centralized constants — the SINGLE source of truth for all configurable values.
All modules must import from here instead of hardcoding values.
Environment variables override defaults for CI/CD and production flexibility.
"""

import os
from shared.utils.excel_base import get_base_url

# ── URLs ────────────────────────────────────────────────────────
BASE_URL = (
    os.environ.get("SWARAJYA_BASE_URL")
    or os.environ.get("BASE_URL")
    or get_base_url()
).rstrip("/")

# ── Authentication Defaults ─────────────────────────────────────
# Auth code should come from env vars or credentials file; empty string means
# the test framework will read from credentials.xlsx / env vars at runtime.
DEFAULT_AUTH_CODE = os.environ.get("SWARAJYA_AUTH_CODE", "")
DEFAULT_ROLE = "Admin"

# ── CSS Selectors (login form) ──────────────────────────────────
SELECTORS = {
    "email": (
        "input#mat-input-0, input[name='email'], input[type='text'], "
        "input[placeholder*='Employee ID'], input[placeholder*='Email']"
    ),
    "password": (
        "input#mat-input-1, input[name='password'], input[type='password'], "
        "input[placeholder*='Password']"
    ),
    "submit": "button:has-text('Sign In'), button[type='submit'], button.btn-primary",
    "tfa_input": (
        "input#mat-input-2, input[name='authCode'], input[placeholder*='OTP'], "
        "input[placeholder*='code'], input[type='text']"
    ),
    "tfa_submit": "button:has-text('Submit'), button[type='submit'], button.btn-primary",
}

# ── Timeouts (ms) ───────────────────────────────────────────────
TFA_TIMEOUT = 10000
DASHBOARD_TIMEOUT = 15000
DOM_READY_TIMEOUT = 5000

# ── Dashboard URL Fragments ─────────────────────────────────────
# Used to determine if user has successfully logged in (URL contains any of these)
DASHBOARD_FRAGMENTS = (
    "dashboard", "default", "employeelist", "addnewemployee",
    "vendor", "customer", "consultant", "purchase", "invoice",
    "finance", "empprofile",
)
