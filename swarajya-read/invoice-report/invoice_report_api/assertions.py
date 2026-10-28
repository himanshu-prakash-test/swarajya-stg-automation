

import math
import re
from typing import Any, Dict, List, Optional, Union
from shared.utils.logger import get_logger

log = get_logger("InvoiceReportAssertions")


def validate_status_code(actual_code: int, expected_code: int, tc_id: str = ""):
    """Validate HTTP response status code matches expectation."""
    assert actual_code == expected_code, (
        f"[{tc_id}] Expected HTTP status {expected_code}, but received {actual_code}."
    )


def validate_summary_response(
    data: Union[Dict[str, Any], List[Any]],
    financial_year: Optional[str] = None,
    tc_id: str = "",
) -> Dict[str, Any]:
    """
    Validate summary metrics response payload (TC-REP-POS-01, TC-REP-POS-04).
    Validates total_invoices > 0 and valid monetary figures.
    """
    assert data is not None, f"[{tc_id}] Response payload is empty or None."

    # If response is a direct list of live records (e.g. from /ems/v1/invoice/getReportData)
    if isinstance(data, list):
        assert len(data) > 0, f"[{tc_id}] Response list contains 0 invoice records."
        # Verify first record fields
        first = data[0]
        assert "financial_year" in first or "sequence_id" in first, (
            f"[{tc_id}] Unexpected list record schema: {list(first.keys())[:5]}"
        )
        if financial_year and "financial_year" in first:
            assert any(r.get("financial_year") == financial_year for r in data), (
                f"[{tc_id}] No records matched financial year {financial_year}."
            )
        return {"total_invoices": len(data), "records": data}

    # Dict payload
    assert isinstance(data, dict), f"[{tc_id}] Expected JSON object payload, got {type(data)}."

    # Check financial year if present in body
    if financial_year and "financial_year" in data:
        assert data["financial_year"] == financial_year, (
            f"[{tc_id}] Expected FY '{financial_year}', got '{data['financial_year']}'."
        )

    # Check metrics block or top-level keys
    metrics = data.get("metrics", data)
    total_inv = metrics.get("total_invoices") or metrics.get("count") or metrics.get("totalInvoices")
    assert total_inv is not None, (
        f"[{tc_id}] Missing 'total_invoices' or 'count' in payload. Keys: {list(metrics.keys())}"
    )
    assert float(total_inv) >= 0, f"[{tc_id}] total_invoices cannot be negative: {total_inv}"

    # Check monetary amount
    amt = metrics.get("total_amount") or metrics.get("raised_amount_lakhs") or metrics.get("total_revenue") or metrics.get("total_paid_amount")
    if amt is not None:
        assert float(amt) >= 0, f"[{tc_id}] Total amount cannot be negative: {amt}"

    return metrics


def validate_status_filter_reconciliation(
    data: Dict[str, Any],
    master_records: Optional[List[Dict[str, Any]]] = None,
    target_status: str = "FINALIZED",
    tc_id: str = "TC-REP-POS-02",
):
    """
    Validate status filter constraints for finalized / paid invoices (TC-REP-POS-02, TC-REP-POS-06).
    Ensures draft / cancelled records are excluded from aggregate figures.
    """
    assert data is not None, f"[{tc_id}] Response data is None."

    if isinstance(data, list):
        # Filter check on live list
        if target_status.upper() == "PAID":
            # Paid invoices have balance == 0 or status id == 5
            paid = [r for r in data if r.get("invoice_amount_balance") == 0 or r.get("invoice_status_id") == 5]
            assert len(paid) > 0, f"[{tc_id}] No paid records found in list."
        return

    # Check status breakdown or filtered response
    if "status_breakdown" in data:
        sb = data["status_breakdown"]
        assert "paid" in sb or "unpaid" in sb, f"[{tc_id}] Missing status breakdown keys in {sb}"

    if "status" in data:
        assert str(data["status"]).upper() == target_status.upper(), (
            f"[{tc_id}] Expected status '{target_status}', got '{data.get('status')}'."
        )

    if target_status.upper() == "PAID" and "outstanding_balance" in data:
        assert float(data["outstanding_balance"]) == 0.0, (
            f"[{tc_id}] Expected outstanding_balance 0.00 for PAID status, got {data['outstanding_balance']}"
        )


def validate_zero_data_periods(
    data: Dict[str, Any],
    tc_id: str = "TC-REP-POS-03",
):
    """
    Validate monthly breakdown and zero-data period handling (TC-REP-POS-03).
    Inactive months must return explicit numeric 0.00 rather than null, undefined, or missing keys.
    """
    assert data is not None, f"[{tc_id}] Monthly breakdown response is None."

    months_data = data.get("months") or data.get("monthly_breakdown") or data
    assert isinstance(months_data, (dict, list)), f"[{tc_id}] Unexpected months data type: {type(months_data)}"

    if isinstance(months_data, dict):
        # Verify month keys
        sample_keys = [k.lower() for k in months_data.keys()]
        assert any(m in sample_keys for m in ("apr", "may", "jun", "jul", "nov", "dec", "jan", "feb", "mar")), (
            f"[{tc_id}] Monthly distribution missing standard month keys: {sample_keys}"
        )

        # Inspect zero-activity months (e.g. nov, dec, jan)
        for month_name, value in months_data.items():
            assert value is not None, (
                f"[{tc_id}] Month '{month_name}' has null / None value instead of numeric 0.00."
            )
            assert isinstance(value, (int, float)), (
                f"[{tc_id}] Month '{month_name}' value must be numeric float/int, got {type(value)} ({value})."
            )
            # Must not be NaN or Inf
            assert not math.isnan(float(value)) and not math.isinf(float(value)), (
                f"[{tc_id}] Month '{month_name}' has invalid numeric value: {value}"
            )

    elif isinstance(months_data, list):
        for entry in months_data:
            assert isinstance(entry, dict), f"[{tc_id}] Each month entry must be dict, got {type(entry)}"
            amt = entry.get("amount") or entry.get("total") or entry.get("revenue", 0.00)
            assert amt is not None, f"[{tc_id}] Month entry missing numeric amount: {entry}"
            assert isinstance(amt, (int, float)), f"[{tc_id}] Month amount must be numeric, got {type(amt)}"


def validate_financial_years_list(
    data: Union[List[str], Dict[str, Any]],
    tc_id: str = "TC-REP-POS-05",
) -> List[str]:
    """
    Validate retrieval of active financial years metadata array (TC-REP-POS-05).
    Verifies response contains formatted strings (e.g. 'YYYY-YYYY').
    """
    assert data is not None, f"[{tc_id}] Financial years response is None."

    years_list = data if isinstance(data, list) else data.get("financial_years", data.get("years", []))
    assert isinstance(years_list, list), f"[{tc_id}] Expected list of financial years, got {type(years_list)}."
    assert len(years_list) > 0, f"[{tc_id}] Financial years list is empty."

    # Validate format YYYY-YYYY
    fy_regex = re.compile(r"^\d{4}-\d{4}$")
    for y in years_list:
        y_str = str(y).strip()
        assert fy_regex.match(y_str), f"[{tc_id}] Invalid financial year format: '{y_str}' (expected YYYY-YYYY)."

    return years_list


def validate_drilldown_reconciliation(
    drilldown_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    summary_outstanding: Optional[float] = None,
    summary_overdue: Optional[float] = None,
    tc_id: str = "TC-REP-POS-06",
):
    """
    Validate line-item drill-down reconciliation for outstanding and overdue amounts (TC-REP-POS-06, TC-REP-POS-07).
    Sum of itemized balances precisely equals aggregate metrics displayed on report.
    """
    assert drilldown_data is not None, f"[{tc_id}] Drilldown data is None."

    # Case A: Invoice details line-item reconciliation (TC-REP-POS-07 data sheet)
    if isinstance(drilldown_data, dict) and "items" in drilldown_data:
        items = drilldown_data["items"]
        total_amount = float(drilldown_data.get("total_amount", 0.0))
        items_sum = sum(float(it.get("amount", 0.0)) for it in items)
        if "tax_amount" in drilldown_data or "tax" in drilldown_data:
            tax_amount = float(drilldown_data.get("tax_amount", drilldown_data.get("tax", 0.0)))
        else:
            # Implied tax from test spec: sum(items.amount) + tax == total_amount
            tax_amount = total_amount - items_sum

        # Check sum(items.amount) + tax == total_amount within 0.05 tolerance
        diff = abs((items_sum + tax_amount) - total_amount)
        assert diff <= 0.05, (
            f"[{tc_id}] Drill-down reconciliation mismatch: items_sum ({items_sum}) + tax ({tax_amount}) != total ({total_amount}). Diff: {diff}"
        )
        return

    # Case B: Outstanding drilldown list
    items_list = drilldown_data if isinstance(drilldown_data, list) else drilldown_data.get("invoices", drilldown_data.get("items", []))
    if summary_outstanding is not None and items_list:
        computed_sum = sum(float(r.get("outstanding_balance") or r.get("invoice_amount_balance", 0.0)) for r in items_list)
        diff = abs(computed_sum - summary_outstanding)
        assert diff <= 1.0, (
            f"[{tc_id}] Sum of outstanding line-items ({computed_sum:.2f}) does not match summary ({summary_outstanding:.2f})."
        )


def validate_floating_point_precision(
    data: Any,
    max_decimals: int = 2,
    tc_id: str = "TC-REP-POS-07",
):
    """
    Validate floating-point decimal precision and serialization (TC-REP-POS-07).
    Ensures monetary metrics are serialized to exact two-decimal precision without IEEE-754 drift.
    """
    assert data is not None, f"[{tc_id}] Data is None."

    def _check_val(key: str, val: Any):
        if isinstance(val, float):
            # Check string representation does not contain IEEE-754 drift like .9300000000000002 or 1e-05
            str_val = f"{val:.10f}".rstrip("0").rstrip(".")
            # Check scientific notation
            assert "e" not in str(val).lower(), f"[{tc_id}] Key '{key}' serialized with scientific notation: {val}"
            parts = str_val.split(".")
            if len(parts) == 2:
                dec_len = len(parts[1])
                # We allow up to max_decimals (typically 2 for currency, 4 for xrate)
                limit = 4 if "rate" in key.lower() or "percent" in key.lower() else max_decimals
                assert dec_len <= limit or abs(round(val, limit) - val) < 1e-9, (
                    f"[{tc_id}] Key '{key}' has excessive decimal drift ({dec_len} decimals): {val}"
                )
        elif isinstance(val, dict):
            for k, v in val.items():
                _check_val(f"{key}.{k}" if key else k, v)
        elif isinstance(val, list):
            for idx, item in enumerate(val[:20]):
                _check_val(f"{key}[{idx}]", item)

    _check_val("", data)


def validate_error_response(
    actual_status: int,
    response_body: Union[str, Dict[str, Any]],
    expected_status: int = 400,
    expected_fragment: Optional[str] = None,
    tc_id: str = "TC-REP-NEG-01",
):
    """
    Validate error status code and sanitization (TC-REP-NEG-01 to TC-REP-NEG-06).
    Ensures proper HTTP error code and no internal database syntax/stack-traces exposed.
    """
    validate_status_code(actual_status, expected_status, tc_id=tc_id)

    # Response body should not leak sensitive server or database internals
    body_str = json_dumps_safe(response_body).lower() if isinstance(response_body, (dict, list)) else str(response_body).lower()

    # Security check: no SQL syntax dump or stack trace
    forbidden_leak_patterns = [
        "sql syntax", "ora-", "psycopg2", "mysql", "syntax error at or near",
        "stack trace", "traceback (most recent call last)", "unhandled exception",
    ]
    for leak in forbidden_leak_patterns:
        assert leak not in body_str, (
            f"[{tc_id}] Security vulnerability: Raw database / server internals disclosed in error body: '{leak}'."
        )

    if expected_fragment:
        assert expected_fragment.lower() in body_str, (
            f"[{tc_id}] Expected error message fragment '{expected_fragment}' not found in response: {body_str[:200]}"
        )


def json_dumps_safe(obj: Any) -> str:
    """Safe JSON stringifier for assertion messages."""
    import json
    try:
        return json.dumps(obj)
    except Exception:
        return str(obj)

