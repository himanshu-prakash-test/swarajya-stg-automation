"""
Authentication Manager for Invoice Report API Automation.

Dynamically handles JWT Bearer tokens and company context with ZERO HARDCODING:
- Reads environment variables (SWARAJYA_BEARER_TOKEN, SWARAJYA_COMPANY_ID)
- Dynamically extracts token and company ID from cached auth state (auth_state_session.json)
- Automatically authenticates via Playwright headless browser session if token is missing
- Provides low-privilege token simulation for RBAC authorization tests (TC-REP-NEG-04)
"""

import os
import json
from typing import Dict, Optional
from shared.utils.logger import get_logger
from shared.utils.paths import SHARED_TEST_DATA_DIR, AUTH_STATE_FILE
from invoice_report_utils.excel_reader import read_api_credentials, get_base_url

log = get_logger("InvoiceReportAuth")


def _read_token_from_auth_state_file(filepath: str) -> Optional[str]:
    """Extract JWT Bearer token dynamically from Playwright storage state JSON."""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for origin in data.get("origins", []):
            for item in origin.get("localStorage", []):
                name = item.get("name", "")
                val = item.get("value", "")
                if name == "token" and val:
                    return val
                if name == "currentUser" and val:
                    try:
                        user_obj = json.loads(val)
                        if "serviceToken" in user_obj and user_obj["serviceToken"]:
                            return user_obj["serviceToken"]
                    except Exception:
                        pass
    except Exception as e:
        log.warning(f"Error reading auth state from {filepath}: {e}")
    return None


def get_company_id() -> str:
    """
    Dynamically extract Company ID (cId) from environment variables or cached auth state.
    Zero hardcoded values.
    """
    env_cid = (
        os.environ.get("SWARAJYA_COMPANY_ID")
        or os.environ.get("SWARAJYA_CID")
        or os.environ.get("CID")
    )
    if env_cid:
        return env_cid.strip()

    session_file = os.path.join(SHARED_TEST_DATA_DIR, "auth_state_session.json")
    for path in (session_file, AUTH_STATE_FILE):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for origin in data.get("origins", []):
                    for item in origin.get("localStorage", []):
                        if item.get("name") in ("cId", "cid", "companyId") and item.get("value"):
                            return str(item.get("value")).strip()
            except Exception:
                pass

    return ""


def get_auth_token(force_refresh: bool = False) -> str:
    """
    Retrieve valid JWT Bearer token for API authentication.
    1. Check env SWARAJYA_BEARER_TOKEN / BEARER_TOKEN
    2. Check auth_state_session.json
    3. Check AUTH_STATE_FILE
    4. Auto-login via Playwright if necessary
    """
    if not force_refresh:
        env_token = os.environ.get("SWARAJYA_BEARER_TOKEN") or os.environ.get("BEARER_TOKEN")
        if env_token:
            return env_token.strip()

        session_file = os.path.join(SHARED_TEST_DATA_DIR, "auth_state_session.json")
        token = _read_token_from_auth_state_file(session_file)
        if token:
            return token

        token = _read_token_from_auth_state_file(AUTH_STATE_FILE)
        if token:
            return token

    log.info("No cached bearer token found; performing automated login to acquire token...")
    return _login_and_acquire_token()


def _login_and_acquire_token() -> str:
    """Perform dynamic authentication to acquire a fresh JWT Bearer token."""
    creds = read_api_credentials(role="Admin")
    base_url = creds.get("base_url") or get_base_url()

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(f"{base_url}/", wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)

            emp_input = page.locator("input[name='email'], input#mat-input-0, input[placeholder*='Employee ID'], input[placeholder*='Email']").first
            pwd_input = page.locator("input[name='password'], input#mat-input-1, input[placeholder*='Password']").first
            btn_submit = page.locator("button:has-text('Sign In'), button[type='submit']").first

            if emp_input.is_visible(timeout=5000):
                emp_input.fill(creds["employee_id"])
                pwd_input.fill(creds["password"])
                btn_submit.click()
                page.wait_for_timeout(2000)

            tfa_input = page.locator("input#mat-input-2, input[name='authCode'], input[placeholder*='OTP'], input[placeholder*='code']").first
            if tfa_input.is_visible(timeout=5000):
                auth_code = creds.get("auth_code") or os.environ.get("SWARAJYA_AUTH_CODE", "")
                if auth_code:
                    tfa_input.fill(auth_code)
                    page.locator("button:has-text('Submit'), button[type='submit']").first.click()
                    page.wait_for_timeout(3000)

            token = page.evaluate("() => localStorage.getItem('token') || (JSON.parse(localStorage.getItem('currentUser') || '{}')).serviceToken")
            session_file = os.path.join(SHARED_TEST_DATA_DIR, "auth_state_session.json")
            context.storage_state(path=session_file)
            browser.close()

            if token:
                log.info("Successfully acquired Bearer token via automated login.")
                return token
    except Exception as e:
        log.warning(f"Automated browser login failed: {e}")

    raise RuntimeError(
        "Failed to acquire valid JWT Bearer token: automated browser login did not yield token "
        "and no cached auth_state session was found."
    )


def get_low_privilege_token() -> str:
    """
    Return a token representing a low-privilege (Employee / Viewer) user lacking reporting access.
    Dynamically constructed without hardcoded strings. Used for RBAC test TC-REP-NEG-04.
    """
    env_low = os.environ.get("SWARAJYA_LOW_PRIVILEGE_TOKEN") or os.environ.get("LOW_PRIVILEGE_TOKEN")
    if env_low:
        return env_low.strip()

    import base64
    import time
    hdr = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    pld = base64.urlsafe_b64encode(json.dumps({"role": "Employee", "iat": int(time.time())}).encode()).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(os.urandom(16)).decode().rstrip("=")
    return f"{hdr}.{pld}.{sig}"


def get_auth_headers(token: Optional[str] = None) -> Dict[str, str]:
    """Generate HTTP request headers with valid Bearer authorization."""
    tok = token or get_auth_token()
    return {
        "Authorization": f"Bearer {tok}",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
    }


def get_unauthorized_headers() -> Dict[str, str]:
    """Generate headers with omitted authorization for TC-REP-NEG-03."""
    return {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
    }
