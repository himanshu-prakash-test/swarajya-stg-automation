"""
REST API Client with Dynamic Wait and Retry Mechanism for Customer Insights Automation.

Features:
- Dynamic base URL & endpoint resolution from Excel / environment variables (ZERO hardcoding)
- Dynamic wait & polling helpers (wait_for_condition, request_with_dynamic_wait)
- Automatic retries on transient connection errors and HTTP 502/503/504
- JWT Bearer token authentication with header injection
- Standardized ApiResponse wrapper with response latency metrics
- Convenience methods for all Customer Insights test cases:
    * GET {{base_url}}/{{actual_revenue_endpoint}}?period=CFY
    * GET {{base_url}}/{{actual_revenue_endpoint}}?period={{period}}
    * GET {{base_url}}/{{actual_revenue_endpoint}}?period={{supported_empty_period}}
"""

import json
import os
import time
import urllib.parse
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import requests

from shared.utils.logger import get_logger
from customer_insights_utils.excel_reader import (
    get_base_url,
    read_api_credentials,
    resolve_endpoint_template,
)
from customer_insights_api.auth import get_auth_token, get_auth_headers, get_company_id

log = get_logger("CustomerInsightsApiClient")


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
        """Parse response JSON safely, falling back to empty dict if invalid."""
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


class CustomerInsightsApiClient:
    """Client for Customer Insights API Testing with Dynamic Wait support."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 15,
        default_poll_timeout: float = 10.0,
        default_poll_interval: float = 0.5,
        verify_ssl: bool = False,
    ):
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self.token = token or get_auth_token()
        self.timeout = timeout
        self.default_poll_timeout = default_poll_timeout
        self.default_poll_interval = default_poll_interval
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl

        # Configure retries for transient HTTP errors (502, 503, 504)
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util import Retry
            retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[502, 503, 504])
            adapter = HTTPAdapter(max_retries=retries)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)
        except Exception as e:
            log.warning(f"Failed to configure session retries: {e}")

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
        """Construct standard HTTP headers with dynamic Bearer token."""
        return get_auth_headers(
            token=token_override if token_override is not None else self.token,
            custom_headers=custom_headers,
        )

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
        Execute an HTTP request with dynamic URL template resolution and timing capture.
        """
        # Resolve any template tokens present in endpoint
        resolved_url = resolve_endpoint_template(endpoint_or_url, base_url=self.base_url)
        if not resolved_url.startswith("http"):
            resolved_url = f"{self.base_url}/{resolved_url.lstrip('/')}"

        req_headers = {} if omit_auth else self.get_headers(token_override=token_override, custom_headers=headers)
        if omit_auth and headers:
            req_headers.update(headers)

        start_time = time.perf_counter()
        log.info(f"API Request: {method.upper()} {resolved_url} | Params: {params}")

        try:
            resp = self.session.request(
                method=method.upper(),
                url=resolved_url,
                params=params,
                json=json_body,
                headers=req_headers,
                timeout=timeout or self.timeout,
            )
        except requests.exceptions.RequestException as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            log.warning(f"API Request to {resolved_url} encountered: {e}")
            fake_resp = requests.Response()
            fake_resp.status_code = 503
            fake_resp._content = json.dumps({"error": str(e), "status_code": 503}).encode("utf-8")
            return ApiResponse(fake_resp, elapsed)

        elapsed = (time.perf_counter() - start_time) * 1000
        api_resp = ApiResponse(resp, elapsed)
        log.info(f"API Response: {api_resp.status_code} in {elapsed:.1f}ms")
        return api_resp

    # ── Dynamic Wait & Polling Mechanics ─────────────────────────

    def poll_until(
        self,
        condition_fn: Callable[[], Tuple[bool, Any]],
        timeout: Optional[float] = None,
        poll_interval: Optional[float] = None,
        error_message: str = "Condition not met within dynamic wait timeout",
    ) -> Any:
        """
        Dynamic Wait: repeatedly executes condition_fn every `poll_interval` seconds
        until condition_fn returns (True, result) or timeout expires.
        Zero hardcoded waits.
        """
        max_wait = timeout if timeout is not None else self.default_poll_timeout
        interval = poll_interval if poll_interval is not None else self.default_poll_interval

        start_time = time.time()
        last_result = None

        while (time.time() - start_time) < max_wait:
            success, last_result = condition_fn()
            if success:
                return last_result
            time.sleep(interval)

        # Final evaluation
        success, last_result = condition_fn()
        if success:
            return last_result

        raise TimeoutError(f"{error_message} (waited {max_wait:.1f}s, last result: {last_result})")

    def request_with_dynamic_wait(
        self,
        method: str,
        endpoint: str,
        expected_status: int = 200,
        timeout: Optional[float] = None,
        poll_interval: Optional[float] = None,
        **kwargs,
    ) -> ApiResponse:
        """
        Dynamic Wait: polls an endpoint until the expected HTTP status is received.
        """
        def _check_endpoint() -> Tuple[bool, ApiResponse]:
            resp = self.request(method, endpoint, **kwargs)
            return (resp.status_code == expected_status, resp)

        return self.poll_until(
            _check_endpoint,
            timeout=timeout,
            poll_interval=poll_interval,
            error_message=f"Endpoint {endpoint} did not return status {expected_status}",
        )

    # ── Convenience Endpoint Handlers ────────────────────────────

    def get_customer_revenue(
        self,
        period: str = "CFY",
        token_override: Optional[str] = None,
        omit_auth: bool = False,
        endpoint_override: Optional[str] = None,
    ) -> ApiResponse:
        """
        GET customer revenue data for a given fiscal period.
        """
        endpoint = endpoint_override or resolve_endpoint_template(
            "{{base_url}}/{{actual_revenue_endpoint}}",
            base_url=self.base_url,
            period=period,
        )
        return self.request(
            "GET",
            endpoint,
            params={"period": period},
            token_override=token_override,
            omit_auth=omit_auth,
        )

    def get_live_customer_revenue_data(
        self,
        period: Optional[str] = None,
        cid: Optional[str] = None,
    ) -> ApiResponse:
        """
        Live fallback to customer revenue staging endpoint if available.
        cId is dynamically discovered from the authenticated session.
        """
        resolved_cid = cid or get_company_id()
        params: Dict[str, Any] = {}
        if period is not None:
            params["period"] = period
        if resolved_cid:
            params["cId"] = resolved_cid
        return self.request(
            "GET",
            "ems/v1/customer/getRevenueData",
            params=params if params else None,
        )
