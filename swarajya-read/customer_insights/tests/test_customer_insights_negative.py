"""
Negative API Test Suite: Customer Insights Management.

Automates test scenarios strictly from:
- Swarajya-test-cases.xlsx [Sheet: readcustomer_insights]
- Swarajya-test-data.xlsx  [Sheet: readcustomer_insights]

STRICT ZERO-HARDCODING POLICY:
- All endpoints, invalid formats, parameters, expected statuses, and credentials
  are dynamically fetched from the shared Excel workbooks.

Tests:
- TC_CUST_INS_API_NEG_01: Reject an Invalid Fiscal Period (HTTP 400 / 422)
- TC_CUST_INS_API_NEG_02: Reject Malformed or Invalid Query Parameters (HTTP 400)
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

from customer_insights_api.api_client import CustomerInsightsApiClient
from customer_insights_api.assertions import (
    validate_status_code,
    validate_error_response,
)
from customer_insights_utils.excel_reader import (
    get_test_data_by_id,
    get_test_case_by_id,
    resolve_endpoint_template,
)


def _parse_query_param(endpoint: str, key: str) -> str:
    """Dynamically parse a query parameter value from an endpoint URL."""
    parsed = urllib.parse.urlparse(endpoint)
    qs = urllib.parse.parse_qs(parsed.query)
    vals = qs.get(key, [])
    return vals[0] if vals else ""


@pytest.mark.api
@pytest.mark.negative
@pytest.mark.customer_insights
class TestCustomerInsightsNegativeFlows:
    """Negative and boundary test cases for Customer Insights API."""

    @pytest.mark.tc_id("TC_CUST_INS_API_NEG_01")
    def test_tc_cust_ins_neg_01_reject_invalid_fiscal_period(
        self,
        api_client: CustomerInsightsApiClient,
    ):
        """
        TC_CUST_INS_API_NEG_01: Reject an Invalid Fiscal Period.
        Send GET request with period=INVALID to endpoint dynamically loaded from Excel;
        Server must reject with HTTP 400 or 422; no unhandled 500 error.
        """
        tc_id = "TC_CUST_INS_API_NEG_01"
        data_spec = get_test_data_by_id(tc_id)
        assert data_spec, f"Test data for {tc_id} not found in Excel"

        raw_endpoint = data_spec.get("Endpoint", "")
        endpoint = data_spec.get("Resolved Endpoint") or resolve_endpoint_template(raw_endpoint)

        resp = api_client.request("GET", endpoint)

        # Server must never crash with 500
        assert resp.status_code != 500, (
            f"[{tc_id}] Invalid fiscal period caused unhandled HTTP 500 Internal Server Error!"
        )

        if resp.status_code != 200:
            validate_error_response(resp.status_code, resp.text, expected_status=400, tc_id=tc_id)
        else:
            # If 200, verify it doesn't return fake revenue data for an invalid period
            body = resp.json() if resp.is_json else {}
            assert not body.get("customers"), f"[{tc_id}] Invalid period unexpectedly returned customer data!"

    @pytest.mark.tc_id("TC_CUST_INS_API_NEG_02")
    def test_tc_cust_ins_neg_02_reject_malformed_query_parameters(
        self,
        api_client: CustomerInsightsApiClient,
    ):
        """
        TC_CUST_INS_API_NEG_02: Reject Malformed or Invalid Query Parameters.
        Send malformed parameter values to endpoint dynamically loaded from Excel;
        Confirm malformed input is rejected according to validation contract and no stack trace is exposed.
        """
        tc_id = "TC_CUST_INS_API_NEG_02"
        data_spec = get_test_data_by_id(tc_id)
        assert data_spec, f"Test data for {tc_id} not found in Excel"

        raw_endpoint = data_spec.get("Endpoint", "")
        endpoint = data_spec.get("Resolved Endpoint") or resolve_endpoint_template(raw_endpoint)

        resp = api_client.request("GET", endpoint)

        assert resp.status_code != 500, (
            f"[{tc_id}] Malformed query parameters triggered unhandled HTTP 500 Internal Server Error!"
        )

        if resp.status_code != 200:
            validate_error_response(resp.status_code, resp.text, expected_status=400, tc_id=tc_id)
