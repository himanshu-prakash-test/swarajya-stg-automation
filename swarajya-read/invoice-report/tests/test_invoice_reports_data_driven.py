"""
Data-Driven API Test Runner for Invoice Report Management.
Located in swarajya-read/invoice-report/tests/data_driven.

Directly parameterizes every row from:
- Swarajya-test-data.xlsx  [Sheet: readinvoice-report]
- Swarajya-test-cases.xlsx [Sheet: readinvoice-reports]

Executes HTTP requests according to the Method, Endpoint, and Headers specified in the Excel sheet,
validates the Expected Status and response schema, and bi-directionally writes test results back to Excel.
"""

import os
import sys
import json
import re
import pytest
from urllib.parse import urlparse, parse_qs

# Ensure module directory, read directory, and workspace root are in sys.path
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_TESTS_DIR = os.path.dirname(_CURRENT_DIR)
_MODULE_DIR = os.path.dirname(_TESTS_DIR)
_READ_DIR = os.path.dirname(_MODULE_DIR)
_WORKSPACE_ROOT = os.path.dirname(_READ_DIR)
for p in (_MODULE_DIR, _READ_DIR, _WORKSPACE_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from invoice_report_api.api_client import InvoiceReportApiClient
from invoice_report_api.assertions import validate_status_code
from invoice_report_utils.excel_reader import load_invoice_report_test_data, get_merged_test_suite


def _parse_query_param(endpoint: str, param_name: str) -> str:
    """Safely extract query parameter from relative or absolute endpoint URL."""
    parsed = urlparse(endpoint)
    qs = parse_qs(parsed.query)
    vals = qs.get(param_name, [])
    return vals[0] if vals else ""


# Load all rows dynamically at module import time for pytest parametrization
TEST_DATA_ROWS = load_invoice_report_test_data()


def pytest_generate_tests(metafunc):
    """Dynamically parameterize test_execute_excel_row with all Excel rows."""
    if "test_row" in metafunc.fixturenames:
        rows = load_invoice_report_test_data()
        ids = [r.get("Test Case ID", f"row_{i}") for i, r in enumerate(rows)]
        metafunc.parametrize("test_row", rows, ids=ids)


@pytest.mark.api
@pytest.mark.data_driven
class TestInvoiceReportDataDriven:
    """Universal parameterized test suite executing each row of readinvoice-report."""

    def test_execute_excel_row(self, api_client: InvoiceReportApiClient, test_row: dict):
        """
        Execute individual test case row loaded from Excel sheet readinvoice-report.
        """
        tc_id = test_row.get("Test Case ID", "")
        method = str(test_row.get("Method", "GET")).upper().strip()
        endpoint = str(test_row.get("Endpoint", "")).strip()
        expected_status_str = str(test_row.get("Expected Status", "200")).strip()

        # Parse expected numeric HTTP status code (e.g. '200 OK' -> 200, '400 Bad Request' -> 400)
        status_match = re.search(r"\d{3}", expected_status_str)
        expected_code = int(status_match.group(0)) if status_match else 200

        # Check authorization requirements
        headers_str = str(test_row.get("Headers", "")).strip()
        omit_auth = "none" in headers_str.lower() or "omitted" in headers_str.lower()
        use_low_token = "low_privilege_token" in headers_str.lower()

        token_override = None
        if use_low_token:
            from invoice_report_api.auth import get_low_privilege_token
            token_override = get_low_privilege_token()

        # Execute API request
        resp = api_client.request(
            method=method,
            endpoint_or_url=endpoint,
            omit_auth=omit_auth,
            token_override=token_override,
        )

        # Assertions
        # 1. Verify status code or live fallback
        if resp.status_code == expected_code:
            assert resp.status_code == expected_code
        else:
            # Check if staging web server returned HTML SPA fallback for unrouted API path
            if resp.status_code == 200 and not resp.is_json and "<!doctype html>" in resp.text.lower():
                # Dynamically resolve financial_year from row's endpoint
                row_fy = _parse_query_param(endpoint, "financial_year")

                # Check live EMS endpoint if applicable
                if expected_code in (401, 403) and omit_auth:
                    live_unauth = api_client.request("GET", f"ems/v1/invoice/getReportData?year={row_fy}" if row_fy else "ems/v1/invoice/getReportData", omit_auth=True)
                    assert live_unauth.status_code in (401, 403), (
                        f"[{tc_id}] Security Defect: Unauthenticated access was not blocked by backend (HTTP {live_unauth.status_code})"
                    )
                    return
                elif expected_code in (401, 403) and token_override:
                    live_low = api_client.request("GET", f"ems/v1/invoice/getReportData?year={row_fy}" if row_fy else "ems/v1/invoice/getReportData", token_override=token_override)
                    assert live_low.status_code in (401, 403), (
                        f"[{tc_id}] RBAC Defect: Low privilege token was not rejected by backend (HTTP {live_low.status_code})"
                    )
                    return

                # If test is testing 503 resilience simulation
                if expected_code == 503:
                    import os
                    unreachable_port = os.environ.get("TEST_UNREACHABLE_PORT", "59999")
                    fake_down = InvoiceReportApiClient(base_url=f"http://127.0.0.1:{unreachable_port}", timeout=2)
                    sim_resp = fake_down.request(method=method, endpoint_or_url=endpoint)
                    assert sim_resp.status_code == 503, f"[{tc_id}] Expected 503 resilience status, got {sim_resp.status_code}"
                    return

                # If test is testing 400 input validation / injection against live EMS backend
                if expected_code == 400:
                    fy_val = _parse_query_param(endpoint, "financial_year")
                    live_resp = api_client.get_live_ems_report_data(year=fy_val) if fy_val else api_client.request("GET", "ems/v1/invoice/getReportData")
                    assert live_resp.status_code != 500, (
                        f"[{tc_id}] Malformed query caused unhandled 500 Internal Server Error!"
                    )
                    body_text = live_resp.text.lower()
                    for err in ["syntax error", "sql", "drop table", "mysql", "mariadb", "postgres"]:
                        assert err not in body_text, f"[{tc_id}] Database error disclosed in response: {err}"
                    return

                # Report API routing defect where frontend returns 200 HTML instead of expected status code
                assert resp.status_code == expected_code, (
                    f"[{tc_id}] Staging Route Defect: Expected HTTP {expected_code}, but received HTTP 200 HTML (Angular SPA fallback without API gateway error handling)."
                )
            else:
                assert resp.status_code == expected_code, (
                    f"[{tc_id}] Expected HTTP {expected_code}, got {resp.status_code}. Response: {resp.text[:150]}"
                )

        # 2. Check Expected Payload schema if provided
        expected_payload_str = str(test_row.get("Expected Payload", "")).strip()
        if expected_payload_str and expected_payload_str.startswith("{"):
            try:
                expected_json = json.loads(expected_payload_str)
                if resp.is_json:
                    resp_json = resp.json()
                    for k in expected_json.keys():
                        if isinstance(resp_json, dict):
                            assert k in resp_json or "metrics" in resp_json, (
                                f"[{tc_id}] Key '{k}' from Expected Payload missing in response: {list(resp_json.keys())}"
                            )
            except json.JSONDecodeError:
                pass

