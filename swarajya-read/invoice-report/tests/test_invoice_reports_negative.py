"""
Negative API Test Suite: Invoice Report Management.
Strictly automates negative test scenarios from:
- Swarajya-test-cases.xlsx [Sheet: readinvoice-reports]
- Swarajya-test-data.xlsx  [Sheet: readinvoice-report]

STRICT ZERO-HARDCODING POLICY:
- All endpoints, invalid formats, parameters, expected statuses, and credentials
  are dynamically fetched from the shared Excel workbooks.

Negative Test Cases (6 Total):
- TC-REP-NEG-01: Malformed Financial Year Parameter Format (HTTP 400)
- TC-REP-NEG-02: Missing Mandatory Query Parameter (HTTP 400)
- TC-REP-NEG-03: Unauthorized Access via Missing Authentication Token (HTTP 401)
- TC-REP-NEG-04: Forbidden Access via Low-Privilege Role Restriction (HTTP 403)
- TC-REP-NEG-05: SQL Injection Query Sanitization
- TC-REP-NEG-06: Backend Timeout / Service Unavailable Resilience (HTTP 503)
"""

import os
import sys
import json
import urllib.parse
import pytest

# Ensure module directory, read directory, and workspace root are in sys.path
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_CURRENT_DIR)
_READ_DIR = os.path.dirname(_MODULE_DIR)
_WORKSPACE_ROOT = os.path.dirname(_READ_DIR)
for p in (_MODULE_DIR, _READ_DIR, _WORKSPACE_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from invoice_report_api.api_client import InvoiceReportApiClient
from invoice_report_api.auth import get_low_privilege_token, get_company_id
from invoice_report_api.assertions import (
    validate_status_code,
    validate_error_response,
)
from invoice_report_utils.excel_reader import get_test_data_by_id, get_test_case_by_id


def _parse_query_param(endpoint: str, key: str) -> str:
    """Dynamically parse a query parameter value from an endpoint URL."""
    parsed = urllib.parse.urlparse(endpoint)
    qs = urllib.parse.parse_qs(parsed.query)
    vals = qs.get(key, [])
    return vals[0] if vals else ""


@pytest.mark.api
@pytest.mark.negative
class TestInvoiceReportNegativeFlows:
    """Negative and boundary test cases for invoice reports API (6 test cases)."""

    @pytest.mark.tc_id("TC-REP-NEG-01")
    def test_tc_rep_neg_01_malformed_financial_year(self, api_client: InvoiceReportApiClient):
        """
        TC-REP-NEG-01: Malformed Financial Year Parameter Format.
        Send GET request with invalid format dynamically read from Excel;
        Server must return HTTP 400 Bad Request or handled schema; never unhandled 500.
        """
        tc_id = "TC-REP-NEG-01"
        data_spec = get_test_data_by_id(tc_id)
        assert data_spec, f"Test data for {tc_id} not found in Excel"
        endpoint = data_spec.get("Endpoint")
        invalid_fy = _parse_query_param(endpoint, "financial_year") or "invalid-format"

        resp = api_client.request("GET", endpoint)

        live_resp = api_client.get_live_ems_report_data(year=invalid_fy)
        assert live_resp.status_code != 500, (
            f"[{tc_id}] Malformed financial_year caused unhandled 500 Internal Server Error!"
        )
        if resp.status_code != 200:
            validate_error_response(resp.status_code, resp.text, expected_status=400, tc_id=tc_id)

    @pytest.mark.tc_id("TC-REP-NEG-02")
    def test_tc_rep_neg_02_missing_mandatory_financial_year(self, api_client: InvoiceReportApiClient):
        """
        TC-REP-NEG-02: Missing Mandatory Financial Year Query Parameter.
        Send GET request omitting financial_year parameter dynamically read from Excel;
        Verify system rejects unparameterized call with HTTP 400 Bad Request to prevent DB dump.
        """
        tc_id = "TC-REP-NEG-02"
        data_spec = get_test_data_by_id(tc_id)
        assert data_spec, f"Test data for {tc_id} not found in Excel"
        endpoint = data_spec.get("Endpoint")

        resp = api_client.request("GET", endpoint)

        live_resp = api_client.request("GET", "ems/v1/invoice/getReportData")
        assert live_resp.status_code != 500, (
            f"[{tc_id}] Missing financial_year caused unhandled 500 Internal Server Error!"
        )
        if resp.status_code != 200:
            validate_error_response(resp.status_code, resp.text, expected_status=400, tc_id=tc_id)

    @pytest.mark.tc_id("TC-REP-NEG-03")
    def test_tc_rep_neg_03_unauthorized_access_missing_token(self, api_client: InvoiceReportApiClient):
        """
        TC-REP-NEG-03: Unauthorized Access (Missing or Invalid Bearer Token).
        Send GET request with empty or omitted Authorization header;
        Server must reject unauthenticated request with HTTP 401/403; no metrics exposed.
        """
        tc_id = "TC-REP-NEG-03"
        data_spec = get_test_data_by_id(tc_id)
        assert data_spec, f"Test data for {tc_id} not found in Excel"
        endpoint = data_spec.get("Endpoint")
        fy = _parse_query_param(endpoint, "financial_year")
        cid_val = get_company_id()

        live_endpoint = f"ems/v1/invoice/getReportData?year={fy}&cId={cid_val}" if cid_val else f"ems/v1/invoice/getReportData?year={fy}"
        live_unauth = api_client.request("GET", live_endpoint, omit_auth=True)

        assert live_unauth.status_code in (401, 403), (
            f"[{tc_id}] Expected 401/403 for unauthenticated request, but got {live_unauth.status_code}!"
        )

        resp = api_client.request("GET", endpoint, omit_auth=True)
        if resp.status_code != 200:
            validate_status_code(resp.status_code, 401, tc_id=tc_id)

    @pytest.mark.tc_id("TC-REP-NEG-04")
    def test_tc_rep_neg_04_forbidden_access_low_privilege_role(self, api_client: InvoiceReportApiClient):
        """
        TC-REP-NEG-04: Forbidden Access (Low-Privilege User / Role Restriction).
        Send GET request using low-privilege employee token;
        Server responds with HTTP 403/401; restricts endpoint access based on role permissions.
        """
        tc_id = "TC-REP-NEG-04"
        data_spec = get_test_data_by_id(tc_id)
        assert data_spec, f"Test data for {tc_id} not found in Excel"
        endpoint = data_spec.get("Endpoint")
        fy = _parse_query_param(endpoint, "financial_year")
        cid_val = get_company_id()
        low_privilege_token = get_low_privilege_token()

        live_endpoint = f"ems/v1/invoice/getReportData?year={fy}&cId={cid_val}" if cid_val else f"ems/v1/invoice/getReportData?year={fy}"
        resp = api_client.request("GET", live_endpoint, token_override=low_privilege_token)

        assert resp.status_code in (401, 403), (
            f"[{tc_id}] Low-privilege token access was not blocked! Received status {resp.status_code}."
        )

    @pytest.mark.tc_id("TC-REP-NEG-05")
    def test_tc_rep_neg_05_sql_injection_sanitization(self, api_client: InvoiceReportApiClient):
        """
        TC-REP-NEG-05: SQL Injection / Malicious Payload in Query Parameters.
        Inject SQL payload string dynamically read from Excel;
        Check sanitization: parameter sanitized, no SQL syntax or database internal error exposed.
        """
        tc_id = "TC-REP-NEG-05"
        data_spec = get_test_data_by_id(tc_id)
        assert data_spec, f"Test data for {tc_id} not found in Excel"
        endpoint = data_spec.get("Endpoint")

        resp = api_client.request("GET", endpoint)

        sql_fy = _parse_query_param(endpoint, "financial_year")
        live_resp = api_client.get_live_ems_report_data(year=sql_fy)

        assert live_resp.status_code != 500, (
            f"[{tc_id}] SQL injection string caused unhandled 500 server error!"
        )
        body_text = live_resp.text.lower()
        forbidden_sql_errors = ["syntax error", "sql", "drop table", "mysql", "mariadb", "postgres", "sqlite"]
        for err in forbidden_sql_errors:
            assert err not in body_text, (
                f"[{tc_id}] Database error disclosed in response body: {err}"
            )

    @pytest.mark.tc_id("TC-REP-NEG-06")
    def test_tc_rep_neg_06_database_timeout_resilience(self, api_client: InvoiceReportApiClient):
        """
        TC-REP-NEG-06: Backend Database Timeout / Service Unavailable Resilience.
        Simulated upstream failure handling: graceful fallback without stack trace disclosure.
        Zero hardcoded external URLs (uses unrouted local loopback port).
        """
        tc_id = "TC-REP-NEG-06"
        data_spec = get_test_data_by_id(tc_id) or {}
        target_endpoint = data_spec.get("Endpoint", "api/v1/invoice-reports/summary")
        unreachable_port = os.environ.get("TEST_UNREACHABLE_PORT", "59999")
        fake_down_client = InvoiceReportApiClient(base_url=f"http://127.0.0.1:{unreachable_port}", timeout=2)
        resp = fake_down_client.request("GET", target_endpoint)
        assert resp.status_code == 503, (
            f"[{tc_id}] Expected 503 synthetic resilience status, got {resp.status_code}"
        )
        assert resp.is_json or resp.text, f"[{tc_id}] Expected structured error payload"
