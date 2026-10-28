"""
Customer Insights API testing layer.
"""

from .api_client import CustomerInsightsApiClient, ApiResponse
from .auth import get_auth_token, get_auth_headers, get_company_id, get_low_privilege_token
from .assertions import (
    validate_status_code,
    validate_revenue_insights_response,
    validate_fiscal_period_filtering,
    validate_customer_revenue_precision,
    validate_revenue_sorting,
    validate_zero_revenue_customer,
    validate_empty_revenue_results,
    validate_error_response,
)

__all__ = [
    "CustomerInsightsApiClient",
    "ApiResponse",
    "get_auth_token",
    "get_auth_headers",
    "get_company_id",
    "get_low_privilege_token",
    "validate_status_code",
    "validate_revenue_insights_response",
    "validate_fiscal_period_filtering",
    "validate_customer_revenue_precision",
    "validate_revenue_sorting",
    "validate_zero_revenue_customer",
    "validate_empty_revenue_results",
    "validate_error_response",
]
