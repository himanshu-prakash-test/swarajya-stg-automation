"""
Central path resolver for Swarajya Automation.
Provides single-source-of-truth paths with multi-environment support (Staging / Production).

Directory Structure:
    shared/test_data/
    ├── test_cases/          ← Test case definitions (.xlsx)
    │   ├── Swarajya-test-cases.xlsx
    │   └── login_test_cases.xlsx
    ├── test_data/           ← Test input data and credentials (.xlsx, .pdf)
    │   ├── Swarajya-test-data.xlsx
    │   ├── credentials.xlsx
    │   └── sample_po.pdf
    └── auth_state_*.json    ← Auth state files (gitignored)
"""

import os
from urllib.parse import urlparse

from shared.config.constants import BASE_URL

# Workspace Root: directory containing shared/, swarajya-create/, etc.
_SHARED_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_ROOT = os.path.dirname(_SHARED_DIR)

# Central Test Data Directory (shared/test_data)
SHARED_TEST_DATA_DIR = os.path.join(_SHARED_DIR, "test_data")

# Central Reports Directory (shared/reports)
REPORTS_DIR = os.path.join(_SHARED_DIR, "reports")
SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, "screenshots")

# Subdirectories
TEST_CASES_DIR = os.path.join(SHARED_TEST_DATA_DIR, "test_cases")
TEST_DATA_DIR = os.path.join(SHARED_TEST_DATA_DIR, "test_data")

# Environment Name: 'staging' (default), 'prod', 'production', etc.
ENV_NAME = os.environ.get("SWARAJYA_ENV", os.environ.get("ENV", "staging")).strip().lower()

# ── Test Cases Workbook ──────────────────────────────────────────
# Priority: env var override → direct shared/test_data → env-specific → subfolder fallback
_custom_cases = os.environ.get("SWARAJYA_TEST_CASES_FILE")
if _custom_cases and os.path.exists(_custom_cases):
    TEST_CASES_FILE = _custom_cases
else:
    direct_cases = os.path.join(SHARED_TEST_DATA_DIR, "Swarajya-test-cases.xlsx")
    env_cases = os.path.join(SHARED_TEST_DATA_DIR, f"Swarajya-test-cases-{ENV_NAME}.xlsx")
    if os.path.exists(env_cases):
        TEST_CASES_FILE = env_cases
    elif os.path.exists(direct_cases):
        TEST_CASES_FILE = direct_cases
    else:
        TEST_CASES_FILE = os.path.join(TEST_CASES_DIR, "Swarajya-test-cases.xlsx")

LOGIN_TEST_CASES_FILE = TEST_CASES_FILE

# ── Test Data Workbook ───────────────────────────────────────────
_custom_data = os.environ.get("SWARAJYA_TEST_DATA_FILE")
if _custom_data and os.path.exists(_custom_data):
    TEST_DATA_FILE = _custom_data
else:
    direct_data = os.path.join(SHARED_TEST_DATA_DIR, "Swarajya-test-data.xlsx")
    env_data = os.path.join(SHARED_TEST_DATA_DIR, f"Swarajya-test-data-{ENV_NAME}.xlsx")
    if os.path.exists(env_data):
        TEST_DATA_FILE = env_data
    elif os.path.exists(direct_data):
        TEST_DATA_FILE = direct_data
    else:
        TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, "Swarajya-test-data.xlsx")

# ── Credentials ──────────────────────────────────────────────────
_direct_creds = os.path.join(SHARED_TEST_DATA_DIR, "credentials.xlsx")
CREDENTIALS_FILE = _direct_creds if os.path.exists(_direct_creds) else os.path.join(TEST_DATA_DIR, "credentials.xlsx")

# ── Sample Files ─────────────────────────────────────────────────
_direct_po = os.path.join(SHARED_TEST_DATA_DIR, "sample_po.pdf")
SAMPLE_PO_FILE = _direct_po if os.path.exists(_direct_po) else os.path.join(TEST_DATA_DIR, "sample_po.pdf")

# ── Auth State ───────────────────────────────────────────────────
# Partitioned by hostname to prevent staging/production session collision
_netloc = urlparse(BASE_URL).netloc.replace(":", "_").replace(".", "_")
AUTH_STATE_FILE = os.path.join(SHARED_TEST_DATA_DIR, f"auth_state_{_netloc}.json" if _netloc else "auth_state.json")

# ── Backward compatibility aliases ──────────────────────────────
TEST_CASE_FILE = TEST_CASES_FILE
TEST_CASES_PATH = TEST_CASES_FILE
TEST_DATA_PATH = TEST_DATA_FILE

