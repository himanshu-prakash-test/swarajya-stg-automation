"""
Excel Reader and Test Data Utility for Employee Management (Create Module).

Loads test cases from shared/test_data/Swarajya-test-cases.xlsx [Sheet: createemp-mgmt]
and input test data from shared/test_data/Swarajya-test-data.xlsx [Sheet: createemp-mgmt].

Strictly zero hardcoded values: Base URL, credentials, test definitions, and form fields
are all fetched dynamically from Excel.
"""

import os
import sys
from typing import Any, Dict, List, Optional

_MODULE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CREATE_ROOT = os.path.dirname(_MODULE_ROOT)
_WORKSPACE_ROOT = os.path.dirname(_CREATE_ROOT)

for _p in (_MODULE_ROOT, _CREATE_ROOT, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shared.utils.excel_loader import (
    build_automation_id,
    load_cases_and_data,
    load_test_data_sheet,
    read_base_url as _central_read_base_url,
    read_credentials as _central_read_credentials,
    update_test_result as _central_update_test_result,
)
from shared.utils.logger import get_logger
from shared.utils.paths import TEST_CASES_FILE, TEST_DATA_FILE

log = get_logger("emp_excel_reader")

MODULE_KEY = "emp"
SHEET_NAME = "createemp-mgmt"


def get_test_cases_filepath() -> str:
    """Return the absolute path to Swarajya-test-cases.xlsx."""
    return TEST_CASES_FILE


def get_test_data_filepath() -> str:
    """Return the absolute path to Swarajya-test-data.xlsx."""
    return TEST_DATA_FILE


def read_base_url(sheet_name: str = SHEET_NAME) -> str:
    """Dynamically extract Base URL from test data Excel banner or environment variable."""
    return _central_read_base_url(sheet_name=sheet_name)


def get_base_url() -> str:
    """Alias for dynamic Base URL resolution."""
    return read_base_url(SHEET_NAME)


def read_credentials(role: str = "Admin") -> Dict[str, str]:
    """
    Dynamically read credentials from Swarajya-test-data.xlsx banner/sheets.
    Zero hardcoded passwords, employee IDs, or auth codes.
    """
    return _central_read_credentials(role=role, sheet_name=SHEET_NAME)


def read_test_cases(sheet_name: str = SHEET_NAME) -> List[Dict[str, Any]]:
    """
    Read test case rows from Swarajya-test-cases.xlsx merged with input data
    from Swarajya-test-data.xlsx mapped by 'Test Case ID'.
    Automatically filters POS/NEG if specified in sheet_name.
    """
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
    log.info(f"Loaded {len(cases)} test cases for '{sheet_name}' (filter={filter_type}) from Excel workbooks")
    return cases


def load_test_cases(sheet_name: str = SHEET_NAME) -> List[Dict[str, Any]]:
    """Alias for read_test_cases."""
    return read_test_cases(sheet_name=sheet_name)


def get_baseline_employee() -> Dict[str, str]:
    """
    Fetch baseline valid employee test data dynamically from Swarajya-test-data.xlsx [Sheet: createemp-mgmt].
    Zero hardcoded fallback data.
    """
    try:
        data_map = load_test_data_sheet(SHEET_NAME)
        # Search for valid positive baseline record (e.g. TC_POS_EMP_001)
        for tc_id, row in data_map.items():
            if "POS" in tc_id.upper() and row.get("First Name") and row.get("Mobile Number"):
                res: Dict[str, str] = {}
                for k, v in row.items():
                    val = str(v).strip() if v is not None else ""
                    if val.endswith(".0") and val[:-2].isdigit():
                        val = val[:-2]
                    res[k] = val
                return res
    except Exception as exc:
        log.warning(f"Could not load baseline employee dynamically from Excel: {exc}")
    return {}


def is_ui_case(tc: Dict[str, Any]) -> bool:
    """Check if test case is an active UI test case to be executed."""
    exec_type = str(tc.get("Execution Type", "UI")).strip().upper()
    auto_status = str(tc.get("Automation Status", "Automated")).strip().lower()
    return exec_type == "UI" and auto_status not in ("excluded", "not automated", "manual", "deferred")


def update_test_result(
    tc_id: str,
    status: str,
    remarks: Optional[str] = None,
    sheet_name: Optional[str] = None,
    duration_s: float = 0.0,
    **kwargs: Any,
) -> bool:
    """
    Update test execution status, automation id, remarks, and timestamp
    in Swarajya-test-cases.xlsx [Sheet: createemp-mgmt].
    """
    final_remarks = remarks or kwargs.get("remark") or kwargs.get("error_message") or ""
    final_duration = duration_s or kwargs.get("execution_time") or kwargs.get("duration") or 0.0
    final_sheet = sheet_name or kwargs.get("sheet") or SHEET_NAME

    return _central_update_test_result(
        tc_id=tc_id,
        status=status,
        remarks=final_remarks,
        sheet_name=final_sheet,
        duration_s=final_duration,
        module_key=MODULE_KEY,
        **kwargs,
    )
