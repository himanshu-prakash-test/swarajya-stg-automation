"""
REST API Client for Invoice Report Automation.

Handles:
- Dynamic base URL resolution from Excel / environment variables (ZERO hardcoding)
- JWT Bearer token authentication with header injection
- Full request/response lifecycle logging with timing metrics
- Dynamic company identification resolution (cId)
- Standardized methods for all endpoints in Swarajya-test-cases.xlsx and Swarajya-test-data.xlsx:
    * GET /api/v1/invoice-reports/summary
    * GET /api/v1/invoice-reports/monthly-breakdown
    * GET /api/v1/invoice-reports/financial-years
    * GET /api/v1/invoice-reports/details
    * GET /api/v1/invoices/outstanding
    * GET /ems/v1/invoice/getReportData (Live staging EMS endpoint)
"""

import json
import os
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple, Union
import requests

from shared.utils.logger import get_logger
from invoice_report_utils.excel_reader import get_base_url, read_api_credentials
from invoice_report_api.auth import get_auth_token, get_auth_headers, get_company_id

log = get_logger("InvoiceReportApiClient")


class ApiResponse:
    """Standardized response wrapper containing status, data, and latency."""

    def __init__(self, response: requests.Response, elapsed_ms: float):
        self.raw = response
        self.status_code = response.status_code
        self.headers = dict(response.headers)
        self.elapsed_ms = elapsed_ms
        self.text = response.text
        self._json_cache: Optional[Any] = None

    def json(self) -> Any:
        """Parse response JSON, falling back to empty dict if HTML / invalid."""
        if self._json_cache is not None:
            return self._json_cache
        try:
            self._json_cache = self.raw.json()
            return self._json_cache
        except Exception:
            return {}

    @property
    def is_json(self) -> bool:
        return "application/json" in self.headers.get("content-type", "").lower()

    def __repr__(self) -> str:
        return f"<ApiResponse [{self.status_code}] ({self.elapsed_ms:.1f}ms)>"


class InvoiceReportApiClient:
    """Client for Invoice Reporting Service API Testing."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 15,
        verify_ssl: bool = False,
    ):
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self.token = token or get_auth_token()
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl

        # Configure retries for transient HTTP errors (502, 503, 504) for CI stability
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util import Retry
            retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[502, 503, 504])
            adapter = HTTPAdapter(max_retries=retries)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)
        except Exception as e:
            log.warning(f"Failed to configure session retries: {e}")

        # Disable insecure request warnings when SSL verification is skipped
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except Exception:
            pass

    def get_headers(
        self,
        token_override: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Construct standard HTTP headers with Bearer token."""
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": "Swarajya-API-Automation/1.0",
        }
        effective_token = token_override if token_override is not None else self.token
        if effective_token:
            headers["Authorization"] = f"Bearer {effective_token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def request(
        self,
        method: str,
        endpoint_or_url: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        token_override: Optional[str] = None,
        omit_auth: bool = False,
        timeout: Optional[int] = None,
    ) -> ApiResponse:
        """
        Execute an HTTP request and capture latency, status, and payload.
        """
        url = endpoint_or_url if endpoint_or_url.startswith("http") else f"{self.base_url}/{endpoint_or_url.lstrip('/')}"
        req_headers = {} if omit_auth else self.get_headers(token_override=token_override, custom_headers=headers)
        if omit_auth and headers:
            req_headers.update(headers)

        start_time = time.perf_counter()
        log.info(f"API Request: {method.upper()} {url} | Params: {params}")

        try:
            resp = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_body,
                headers=req_headers,
                timeout=timeout or self.timeout,
            )
        except requests.exceptions.RequestException as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            log.error(f"API Request to {url} failed: {e}")
            # Construct synthetic 503 response if connection fails
            fake_resp = requests.Response()
            fake_resp.status_code = 503
            fake_resp._content = json.dumps({"error": str(e), "status_code": 503}).encode("utf-8")
            return ApiResponse(fake_resp, elapsed)

        elapsed = (time.perf_counter() - start_time) * 1000
        api_resp = ApiResponse(resp, elapsed)
        log.info(f"API Response: {api_resp.status_code} in {elapsed:.1f}ms | Content-Type: {api_resp.headers.get('content-type')}")
        return api_resp

    # ── Convenience Endpoint Methods ─────────────────────────────

    def get_summary(
        self,
        financial_year: Optional[str] = None,
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        token_override: Optional[str] = None,
        omit_auth: bool = False,
        custom_endpoint: Optional[str] = None,
    ) -> ApiResponse:
        """
        GET /api/v1/invoice-reports/summary
        Parameters: financial_year, customer_id, status
        """
        endpoint = custom_endpoint or "api/v1/invoice-reports/summary"
        params: Dict[str, Any] = {}
        if financial_year is not None:
            params["financial_year"] = financial_year
        if customer_id is not None:
            params["customer_id"] = customer_id
        if status is not None:
            params["status"] = status

        return self.request(
            "GET",
            endpoint,
            params=params if params else None,
            token_override=token_override,
            omit_auth=omit_auth,
        )

    def get_monthly_breakdown(
        self,
        financial_year: Optional[str] = None,
        token_override: Optional[str] = None,
        omit_auth: bool = False,
    ) -> ApiResponse:
        """
        GET /api/v1/invoice-reports/monthly-breakdown
        """
        params = {"financial_year": financial_year} if financial_year else {}
        return self.request(
            "GET",
            "api/v1/invoice-reports/monthly-breakdown",
            params=params if params else None,
            token_override=token_override,
            omit_auth=omit_auth,
        )

    def get_financial_years(
        self,
        token_override: Optional[str] = None,
        omit_auth: bool = False,
    ) -> ApiResponse:
        """
        GET /api/v1/invoice-reports/financial-years
        """
        return self.request(
            "GET",
            "api/v1/invoice-reports/financial-years",
            token_override=token_override,
            omit_auth=omit_auth,
        )

    def get_invoice_details(
        self,
        invoice_id: Optional[str] = None,
        token_override: Optional[str] = None,
        omit_auth: bool = False,
    ) -> ApiResponse:
        """
        GET /api/v1/invoice-reports/details
        """
        params = {"invoice_id": invoice_id} if invoice_id else {}
        return self.request(
            "GET",
            "api/v1/invoice-reports/details",
            params=params if params else None,
            token_override=token_override,
            omit_auth=omit_auth,
        )

    def get_outstanding_invoices(
        self,
        financial_year: Optional[str] = None,
        status: Optional[str] = None,
        token_override: Optional[str] = None,
        omit_auth: bool = False,
    ) -> ApiResponse:
        """
        GET /api/v1/invoices/outstanding
        """
        params: Dict[str, Any] = {}
        if financial_year is not None:
            params["financial_year"] = financial_year
        if status is not None:
            params["status"] = status
        return self.request(
            "GET",
            "api/v1/invoices/outstanding",
            params=params if params else None,
            token_override=token_override,
            omit_auth=omit_auth,
        )

    def get_live_ems_report_data(
        self,
        year: Optional[str] = None,
        cid: Optional[str] = None,
    ) -> ApiResponse:
        """
        Direct access to the live staging backend EMS reporting endpoint:
        GET /ems/v1/invoice/getReportData?year=YYYY-YYYY&cId=...
        cId is dynamically discovered from the authenticated session (zero hardcoding).
        """
        resolved_cid = cid or get_company_id()
        params: Dict[str, Any] = {}
        if year is not None:
            params["year"] = year
        if resolved_cid:
            params["cId"] = resolved_cid
        return self.request(
            "GET",
            "ems/v1/invoice/getReportData",
            params=params if params else None,
        )
