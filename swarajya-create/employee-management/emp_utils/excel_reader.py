"""
Excel reader for Employee Management (Create).
Loads test cases from Swarajya-test-cases.xlsx [Sheet: createemp-mgmt]
and test data from Swarajya-test-data.xlsx [Sheet: createemp-mgmt].
Strictly zero hardcoded values.
"""

import os
import sys
from typing import Any, Dict, List, Optional

_MODULE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WS_ROOT = os.path.dirname(os.path.dirname(_MODULE_ROOT))
for _p in (_WS_ROOT, _MODULE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shared.utils.excel_loader import (
    build_automation_id,
    load_cases_and_data,
    read_base_url,
    read_credentials as _central_read_credentials,
    update_test_result as _central_update_test_result,
)
from shared.utils.logger import get_logger

logger = get_logger("emp_excel_reader")
MODULE_KEY = "emp"
SHEET_NAME = "createemp-mgmt"


def get_test_cases_filepath() -> str:
    """Return path to Swarajya-test-cases.xlsx."""
    from shared.utils.paths import TEST_CASES_FILE
    return TEST_CASES_FILE


def read_credentials(role: str = "Employee") -> Dict[str, str]:
    """Dynamically read credentials from Swarajya-test-data.xlsx banner/sheets or environment."""
    return _central_read_credentials(role=role, sheet_name=SHEET_NAME)


def read_test_cases(sheet_name: str = "createemp-mgmt") -> List[Dict[str, Any]]:
    """Read test case rows merged with input test data from Swarajya-test-cases/data workbooks."""
    filter_type = None
    sn_upper = str(sheet_name).upper()
    if "POS" in sn_upper:
        filter_type = "POS"
    elif "NEG" in sn_upper:
        filter_type = "NEG"
    cases = load_cases_and_data(MODULE_KEY, filter_type=filter_type)
    for tc in cases:
        if "_sheet" not in tc:
            tc["_sheet"] = SHEET_NAME
    return cases


def is_ui_case(tc: Dict[str, Any]) -> bool:
    """Check if test case is an active UI test case."""
    exec_type = str(tc.get("Execution Type", "UI")).strip().upper()
    auto_status = str(tc.get("Automation Status", "Automated")).strip().lower()
    return exec_type == "UI" and auto_status not in ("excluded", "not automated", "manual", "deferred")


def update_test_result(
    tc_id: str,
    status: str,
    auto_id: str = "",
    remark: str = "",
) -> bool:
    """Update test status in Swarajya-test-cases.xlsx."""
    return _central_update_test_result(tc_id, status, remark, SHEET_NAME)
