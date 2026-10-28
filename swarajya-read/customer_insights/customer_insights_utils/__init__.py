"""
Customer Insights utilities package.
"""

from .excel_reader import (
    get_base_url,
    read_api_credentials,
    load_customer_insights_test_cases,
    load_customer_insights_test_data,
    get_merged_test_suite,
    get_test_case_by_id,
    get_test_data_by_id,
    update_test_result,
    build_automation_id,
    resolve_endpoint_template,
    CASES_SHEET,
    DATA_SHEET,
)

__all__ = [
    "get_base_url",
    "read_api_credentials",
    "load_customer_insights_test_cases",
    "load_customer_insights_test_data",
    "get_merged_test_suite",
    "get_test_case_by_id",
    "get_test_data_by_id",
    "update_test_result",
    "build_automation_id",
    "resolve_endpoint_template",
    "CASES_SHEET",
    "DATA_SHEET",
]
