"""
Deep Domain Assertions for Customer Insights API Testing.

Covers all scenarios defined in Swarajya-test-cases.xlsx and Swarajya-test-data.xlsx:
- Status code validation
- Revenue insights schema and record integrity
- Fiscal period filtering constraints (CFY, 2FY, 3FY, 5FY)
- Customer revenue verification and precision
- Revenue sorting ordering contracts
- Zero-revenue customer handling
- Empty revenue collection handling
- Error schema validation for invalid periods & query parameters
"""

import math
import re
from typing import Any, Dict, List, Optional, Union
from shared.utils.logger import get_logger

log = get_logger("CustomerInsightsAssertions")


def validate_status_code(actual_code: int, expected_code: int, tc_id: str = ""):
    """Validate HTTP response status code matches expectation."""
    assert actual_code == expected_code, (
        f"[{tc_id}] Expected HTTP status {expected_code}, but received {actual_code}."
    )


def validate_revenue_insights_response(
    data: Union[Dict[str, Any], List[Any]],
    expected_period: Optional[str] = None,
    tc_id: str = "TC_CUST_INS_API_POS_01",
) -> Dict[str, Any]:
    """
    TC_CUST_INS_API_POS_01: Validate customer revenue insights response payload.
    Ensures valid JSON structure, period match, and customer records containing
    valid ID/name and non-null revenue figures.
    """
    assert data is not None, f"[{tc_id}] Response payload is empty or None."

    if isinstance(data, list):
        # List of customer records
        if len(data) > 0:
            first = data[0]
            assert any(k in first for k in ("customer_id", "customerId", "id", "customer_name", "customerName", "revenue")), (
                f"[{tc_id}] Customer record missing key identity/revenue fields: {list(first.keys())[:5]}"
            )
        return {"customers": data, "count": len(data)}

    assert isinstance(data, dict), f"[{tc_id}] Expected JSON object or list payload, got {type(data)}."

    if expected_period and "period" in data:
        assert str(data["period"]).upper() == expected_period.upper(), (
            f"[{tc_id}] Expected period '{expected_period}', got '{data['period']}'."
        )

    # Check for customers collection or metrics
    customers = data.get("customers") or data.get("data") or data.get("records")
    if customers is not None and isinstance(customers, list) and len(customers) > 0:
        for idx, cust in enumerate(customers[:10]):
            assert isinstance(cust, dict), f"[{tc_id}] Customer item #{idx} must be a dict"
            # Verify revenue if present
            rev = cust.get("revenue") or cust.get("total_revenue") or cust.get("amount")
            if rev is not None:
                assert float(rev) >= 0, f"[{tc_id}] Customer revenue cannot be negative: {rev}"

    return data


def validate_fiscal_period_filtering(
    data: Union[Dict[str, Any], List[Any]],
    period: str,
    tc_id: str = "TC_CUST_INS_API_POS_02",
):
    """
    TC_CUST_INS_API_POS_02: Validate that returned revenue data reflects the exact fiscal period requested.
    """
    assert data is not None, f"[{tc_id}] Response data is None for period '{period}'."

    if isinstance(data, dict):
        if "period" in data:
            assert str(data["period"]).upper() == period.upper(), (
                f"[{tc_id}] Period mismatch: expected '{period}', received '{data['period']}'"
            )
        metrics = data.get("metrics", {})
        if "total_revenue" in metrics:
            assert float(metrics["total_revenue"]) >= 0.0, f"[{tc_id}] Total revenue cannot be negative."


def validate_customer_revenue_precision(
    data: Union[Dict[str, Any], List[Any]],
    target_customer_id: str = "TD_CUST_05",
    expected_revenue: Optional[float] = 500000.00,
    currency: Optional[str] = "INR",
    tc_id: str = "TC_CUST_INS_API_POS_03",
):
    """
    TC_CUST_INS_API_POS_03: Validate customer revenue against verified source of truth within precision rules.
    """
    assert data is not None, f"[{tc_id}] Response payload is None."

    customers = []
    if isinstance(data, list):
        customers = data
    elif isinstance(data, dict):
        customers = data.get("customers") or data.get("data") or [data]

    matched_customer = None
    for cust in customers:
        cid = str(cust.get("customer_id") or cust.get("customerId") or cust.get("id") or "").strip()
        if cid == target_customer_id or target_customer_id in cid:
            matched_customer = cust
            break

    if matched_customer:
        rev = matched_customer.get("revenue") or matched_customer.get("total_revenue") or matched_customer.get("amount")
        if rev is not None and expected_revenue is not None:
            diff = abs(float(rev) - float(expected_revenue))
            assert diff <= 0.01, f"[{tc_id}] Revenue mismatch for {target_customer_id}: expected {expected_revenue}, got {rev}"
        if currency and "currency" in matched_customer:
            assert str(matched_customer["currency"]).upper() == currency.upper(), (
                f"[{tc_id}] Expected currency '{currency}', got '{matched_customer.get('currency')}'"
            )


def validate_revenue_sorting(
    data: Union[Dict[str, Any], List[Any]],
    descending: bool = True,
    tc_id: str = "TC_CUST_INS_API_POS_04",
):
    """
    TC_CUST_INS_API_POS_04: Verify revenue sorting in descending order.
    Ensures adjacent values satisfy revenue[i] >= revenue[i+1].
    """
    assert data is not None, f"[{tc_id}] Response data is None."

    customers = []
    if isinstance(data, list):
        customers = data
    elif isinstance(data, dict):
        customers = data.get("customers") or data.get("data") or []

    revenue_values: List[float] = []
    for c in customers:
        rev = c.get("revenue") or c.get("total_revenue") or c.get("amount")
        if rev is not None:
            try:
                revenue_values.append(float(rev))
            except (ValueError, TypeError):
                pass

    if len(revenue_values) > 1:
        for i in range(len(revenue_values) - 1):
            if descending:
                assert revenue_values[i] >= revenue_values[i + 1] - 0.001, (
                    f"[{tc_id}] Revenue values not in descending order at index {i}: "
                    f"{revenue_values[i]} < {revenue_values[i+1]}"
                )


def validate_zero_revenue_customer(
    data: Union[Dict[str, Any], List[Any]],
    target_customer_id: str = "TD_CUST_06",
    tc_id: str = "TC_CUST_INS_API_POS_05",
):
    """
    TC_CUST_INS_API_POS_05: Validate that zero-revenue customer is handled per API contract.
    Zero must be represented as numeric 0/0.00 and not treated as missing/null.
    """
    assert data is not None, f"[{tc_id}] Response payload is None."

    customers = []
    if isinstance(data, list):
        customers = data
    elif isinstance(data, dict):
        customers = data.get("customers") or data.get("data") or [data]

    found = False
    for cust in customers:
        cid = str(cust.get("customer_id") or cust.get("customerId") or cust.get("id") or "").strip()
        if cid == target_customer_id or target_customer_id in cid:
            found = True
            rev = cust.get("revenue") or cust.get("total_revenue") or cust.get("amount")
            assert rev is not None, f"[{tc_id}] Zero-revenue customer has null/missing revenue."
            assert float(rev) == 0.0, f"[{tc_id}] Expected revenue 0.00, got {rev}."
            break


def validate_empty_revenue_results(
    data: Union[Dict[str, Any], List[Any]],
    tc_id: str = "TC_CUST_INS_API_POS_06",
):
    """
    TC_CUST_INS_API_POS_06: API returns valid empty collection ([] or count 0),
    no fabricated records or unhandled exceptions.
    """
    assert data is not None, f"[{tc_id}] Response is None."

    if isinstance(data, list):
        assert len(data) == 0, f"[{tc_id}] Expected empty list, but found {len(data)} items."
        return

    if isinstance(data, dict):
        customers = data.get("customers") or data.get("data")
        if customers is not None:
            assert len(customers) == 0, f"[{tc_id}] Expected empty customers collection, found {len(customers)}."
        count = data.get("count") or data.get("record_count")
        if count is not None:
            assert int(count) == 0, f"[{tc_id}] Expected count 0, got {count}."


def validate_error_response(
    status_code: int,
    response_text: str,
    expected_status: int = 400,
    tc_id: str = "",
):
    """
    Validate error handling contract for negative tests (TC_CUST_INS_API_NEG_01, NEG_02).
    Ensures status code matches expected validation status and no unhandled server stack traces occur.
    """
    # Accept 400 or 422 for validation rejections
    assert status_code in (expected_status, 400, 422), (
        f"[{tc_id}] Expected HTTP {expected_status} (or 422), but got {status_code}. Body: {response_text[:200]}"
    )
    # Ensure no internal server stack trace is exposed
    lower_text = response_text.lower()
    for sensitive in ("traceback (most recent call last)", "fatal error", "exception in thread", "syntaxerror:"):
        assert sensitive not in lower_text, (
            f"[{tc_id}] Response exposed internal stack trace / sensitive details: {response_text[:300]}"
        )
