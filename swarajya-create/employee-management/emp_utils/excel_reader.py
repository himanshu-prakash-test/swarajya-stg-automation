"""
Excel Reader adapter for Employee Management module.
Delegates all test case and test data management directly to shared/utils/excel_base.py,
using the centralized shared/test_data/ workbooks.
"""

from typing import Any, Dict, List, Optional
import re

from shared.utils.excel_base import (
    load_suite_cases,
    read_credentials as _shared_read_credentials,
    update_test_result as _shared_update_test_result,
    is_ui_case as _shared_is_ui_case,
    build_automation_id as _shared_build_automation_id,
    TEST_CASES_FILE,
    TEST_DATA_FILE,
)
from shared.utils.logger import get_logger

log = get_logger("excel_reader")

SHEET_NAME = "createemp-mgmt"
CASES_FILE = TEST_CASES_FILE
CREDS_FILE = TEST_DATA_FILE


def build_automation_id(tc_id: str) -> str:
    """Build normalized automation ID matching framework standard."""
    return _shared_build_automation_id("EMP", tc_id)


def is_ui_case(tc: Dict[str, Any]) -> bool:
    """Filter out non-UI / API cases."""
    return _shared_is_ui_case(tc)


def read_credentials(role: str = "Admin") -> Dict[str, str]:
    """
    Pull credentials for Employee Management module.
    Creating and managing employees requires Admin privileges (User ID 332 in createemp-mgmt).
    If Manager is explicitly requested for login verification, returns Manager credentials.
    """
    if role and role.strip().lower() == "manager":
        return _shared_read_credentials(role="Manager", sheet_name=SHEET_NAME)
    return _shared_read_credentials(role="Admin", sheet_name=SHEET_NAME)


def read_test_cases(sheet_name: str) -> List[Dict[str, Any]]:
    """
    Load test cases from the centralized Swarajya-test-cases.xlsx workbook,
    merging field values from Swarajya-test-data.xlsx.
    """
    flow_filter = "positive" if "pos" in sheet_name.lower() else "negative" if "neg" in sheet_name.lower() else None
    cases = load_suite_cases(sheet_name=SHEET_NAME, flow_filter=flow_filter)
    log.info(f"Loaded {len(cases)} test cases for '{sheet_name}' from shared/test_data/")
    return cases


def find_test_case(tc_id: str) -> Optional[Dict[str, Any]]:
    """Locate a single test case by ID from the centralized sheet."""
    for case in load_suite_cases(sheet_name=SHEET_NAME):
        if str(case.get("Test Case ID", "")).strip() == tc_id.strip():
            return case
    return None


def update_test_result(tc_id: str, status: str, auto_id: str = "", remark: str = "") -> None:
    """Update execution outcome back into shared/test_data/Swarajya-test-cases.xlsx."""
    normalized_auto_id = auto_id or build_automation_id(tc_id)
    _shared_update_test_result(
        sheet_name=SHEET_NAME,
        tc_id=tc_id,
        status=status,
        auto_id=normalized_auto_id,
        remarks=remark,
    )
