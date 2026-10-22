"""
Excel Reader utility for Create Purchase Order module.
Delegates strictly to shared/utils/excel_base.py to maintain single source of truth.
ZERO hardcoding: all URLs, credentials, test descriptions, and data records are
dynamically fetched from the shared Excel workbooks.
"""

from typing import Any, Dict, List, Optional
from shared.utils.excel_base import (
    get_base_url as _shared_get_base_url,
    read_credentials as _shared_read_credentials,
    load_test_cases as _shared_load_test_cases,
    load_test_data as _shared_load_test_data,
    get_test_case_by_id as _shared_get_test_case_by_id,
    get_test_data_by_id as _shared_get_test_data_by_id,
    update_test_result as _shared_update_test_result,
    build_automation_id as _shared_build_automation_id,
)

SHEET_NAME = "createpurchase_order"


def get_base_url(sheet_name: str = SHEET_NAME) -> str:
    """Fetch base staging URL dynamically from Excel sheet."""
    return _shared_get_base_url(sheet_name=sheet_name)


def read_credentials(role: str = "Admin", sheet_name: str = SHEET_NAME) -> Dict[str, str]:
    """Fetch authentication credentials dynamically from Excel sheet."""
    return _shared_read_credentials(role=role, sheet_name=sheet_name)


def load_test_cases(sheet_name: str = SHEET_NAME) -> List[Dict[str, Any]]:
    """Fetch all test case rows for purchase order from Excel."""
    return _shared_load_test_cases(sheet_name=sheet_name)


def load_test_data(sheet_name: str = SHEET_NAME) -> List[Dict[str, Any]]:
    """Fetch all test data rows for purchase order from Excel."""
    return _shared_load_test_data(sheet_name=sheet_name)


def get_test_case_by_id(tc_id: str, sheet_name: str = SHEET_NAME) -> Optional[Dict[str, Any]]:
    """Fetch metadata for a single test case ID."""
    return _shared_get_test_case_by_id(tc_id, sheet_name=sheet_name)


def get_test_data_by_id(tc_id: str, sheet_name: str = SHEET_NAME) -> Optional[Dict[str, Any]]:
    """Fetch input dataset for a single test case ID."""
    return _shared_get_test_data_by_id(tc_id, sheet_name=sheet_name)


def update_test_result(
    tc_id: str,
    status: str,
    remarks: str = "",
    auto_id: str = "",
    sheet_name: str = SHEET_NAME,
) -> None:
    """Update execution result (PASS/FAIL/SKIPPED) in Swarajya-test-cases.xlsx."""
    _shared_update_test_result(
        sheet_name,
        tc_id,
        status,
        remarks=remarks,
        auto_id_or_sheet=auto_id,
    )


def build_automation_id(tc_id: str) -> str:
    """Generate normalized script ID like AUT_CPO_POS_01."""
    return _shared_build_automation_id("CPO", tc_id)
