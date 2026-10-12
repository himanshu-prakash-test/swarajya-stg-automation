"""
Excel reader and test data utility for Customer Update module.
Loads test cases from shared/test_data/Swarajya-test-cases.xlsx [Sheet: updatecustomer_mgmt]
and test data from shared/test_data/Swarajya-test-data.xlsx [Sheet: updatecustomer_mgmt].
Zero hardcoding.
"""

import os
import re
import sys
from typing import Any, Dict, List, Optional

_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULE_ROOT = os.path.dirname(_DIR)
_UPDATE_ROOT = os.path.dirname(_MODULE_ROOT)
_WORKSPACE_ROOT = os.path.dirname(_UPDATE_ROOT)

for _p in (_MODULE_ROOT, _UPDATE_ROOT, _WORKSPACE_ROOT):
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
from shared.utils.paths import TEST_CASES_FILE

log = get_logger("customer_excel_reader")
MODULE_KEY = "update_customer"
SHEET_NAME = "updatecustomer_mgmt"


def resolve_excel_path() -> str:
    """Return central test cases workbook path."""
    return TEST_CASES_FILE


def load_test_cases(sheet_name: str = "updatecustomer_mgmt") -> List[Dict[str, Any]]:
    """
    Read all test case rows for customer update module.
    Automatically filters POS/NEG if specified in sheet_name.
    """
    filter_type = None
    sn_upper = str(sheet_name).upper()
    if "NEG" in sn_upper:
        filter_type = "NEG"
    elif "POS" in sn_upper:
        filter_type = "POS"

    cases = load_cases_and_data(MODULE_KEY, filter_type=filter_type)
    for tc in cases:
        if "_sheet" not in tc:
            tc["_sheet"] = SHEET_NAME
    log.info(f"Loaded {len(cases)} test cases for '{sheet_name}' from central shared workbooks")
    return cases


def read_credentials(role: str = "Admin") -> Dict[str, str]:
    """Dynamically read credentials from shared test data workbooks or environment."""
    return _central_read_credentials(role=role, sheet_name=SHEET_NAME)


def update_test_result(
    tc_id: str,
    status: str,
    remarks: str = "",
    duration_s: float = 0.0,
    sheet_name: Optional[str] = None,
) -> bool:
    """Update execution results in the central test cases workbook."""
    return _central_update_test_result(
        tc_id=tc_id,
        status=status,
        remarks=remarks,
        duration_s=duration_s,
        module_key=MODULE_KEY,
    )


def get_base_url() -> str:
    """Fetch base URL dynamically."""
    return read_base_url(SHEET_NAME)
