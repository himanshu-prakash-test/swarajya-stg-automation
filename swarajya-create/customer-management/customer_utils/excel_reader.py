"""
Excel reader for Customer Management (Create).
Loads test cases from Swarajya-test-cases.xlsx [Sheet: createcutomer-mgmt]
and test data from Swarajya-test-data.xlsx [Sheet: createcustomer-mgmt].
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
    read_base_url as _central_read_base_url,
    read_credentials as _central_read_credentials,
    update_test_result as _central_update_test_result,
    read_data_sheet,
)
from shared.utils.logger import get_logger

logger = get_logger("customer_excel_reader")
MODULE_KEY = "customer"
SHEET_NAME_CASES = "createcutomer-mgmt"
SHEET_NAME_DATA = "createcustomer-mgmt"
SHEET_NAME = SHEET_NAME_CASES


def get_test_cases_filepath() -> str:
    """Return path to Swarajya-test-cases.xlsx."""
    from shared.utils.paths import TEST_CASES_FILE
    return TEST_CASES_FILE


def read_base_url() -> str:
    """Dynamically read the staging Base URL from Swarajya-test-data.xlsx."""
    return _central_read_base_url()


def read_credentials(role: str = "Admin") -> Dict[str, str]:
    """Dynamically read credentials from Swarajya-test-data.xlsx banner/sheets or environment."""
    return _central_read_credentials(role=role, sheet_name=SHEET_NAME_DATA)


def read_test_cases(sheet_name: str = SHEET_NAME_CASES) -> List[Dict[str, Any]]:
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
            tc["_sheet"] = SHEET_NAME_CASES
    return cases


def is_ui_case(tc: Dict[str, Any]) -> bool:
    """Check if test case is an active UI test case."""
    exec_type = str(tc.get("Execution Type", "UI")).strip().upper()
    auto_status = str(tc.get("Automation Status", "Automated")).strip().lower()
    return exec_type == "UI" and auto_status not in ("excluded", "not automated", "manual", "deferred")


def get_baseline_customer() -> Dict[str, str]:
    """Fetch baseline valid customer test data dynamically from Swarajya-test-data.xlsx."""
    try:
        data_map = read_data_sheet(SHEET_NAME_DATA)
        preferred = None
        for tc_id, row in data_map.items():
            if "POS" in tc_id.upper() and (row.get("Customer Name") or row.get("name")):
                if row.get("Address Line 1") and row.get("City"):
                    preferred = row
                    break
                elif not preferred:
                    preferred = row
        if preferred:
            res = {}
            for k, v in preferred.items():
                val = str(v).strip() if v is not None else ""
                if val.endswith(".0") and val[:-2].isdigit():
                    val = val[:-2]
                res[k] = val
            return res
    except Exception as exc:
        logger.warning(f"Could not load baseline customer from Excel: {exc}")
    return {}


def update_test_result(
    tc_id: str,
    status: str,
    remarks: Optional[str] = None,
    error_message: Optional[str] = None,
    duration_s: Optional[float] = None,
    execution_time: Optional[float] = None,
    sheet_name: str = SHEET_NAME_CASES,
    **kwargs,
) -> bool:
    """Update test status in Swarajya-test-cases.xlsx."""
    rem = remarks or error_message or kwargs.get("remark") or ""
    dur = duration_s or execution_time
    if dur:
        rem = f"{rem} ({dur:.2f}s)" if rem else f"({dur:.2f}s)"
    return _central_update_test_result(tc_id, status, rem, sheet_name)
