"""
Excel reader and test data utility for Invoice Update Management module.
Loads test cases from shared/test_data/Swarajya-test-cases.xlsx [Sheet: update/invoice_mgmt]
and test data from shared/test_data/Swarajya-test-data.xlsx [Sheet: update/invoice_mgmt].
Strictly zero hardcoded values.
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

import shared.utils.excel_loader as _central_loader
from shared.utils.excel_loader import (
    build_automation_id,
    load_cases_and_data,
    read_base_url as _central_read_base_url,
    read_credentials as _central_read_credentials,
    update_test_result as _central_update_test_result,
    read_data_sheet,
)
from shared.utils.logger import get_logger
from shared.utils.paths import TEST_CASES_FILE

log = get_logger("invoice_update_excel_reader")
MODULE_KEY = "update_invoice"
SHEET_NAME = "updateinvoice_mgmt"

# Self-register module mappings dynamically in shared loader
if hasattr(_central_loader, "MODULE_SHEET_MAP"):
    _central_loader.MODULE_SHEET_MAP.setdefault("update_invoice", ("updateinvoice_mgmt", "updateinvoice_mgmt"))
    _central_loader.MODULE_SHEET_MAP.setdefault("updateinvoice_mgmt", ("updateinvoice_mgmt", "updateinvoice_mgmt"))
    _central_loader.MODULE_SHEET_MAP.setdefault("update/invoice_mgmt", ("updateinvoice_mgmt", "updateinvoice_mgmt"))
    _central_loader.MODULE_SHEET_MAP.setdefault("invoice-management", ("updateinvoice_mgmt", "updateinvoice_mgmt"))


def resolve_excel_path() -> str:
    """Return central test cases workbook path."""
    return TEST_CASES_FILE


def read_base_url() -> str:
    """Dynamically read the staging Base URL from Swarajya-test-data.xlsx."""
    return _central_read_base_url(SHEET_NAME)


get_base_url = read_base_url


def read_credentials(role: str = "Admin") -> Dict[str, str]:
    """Dynamically read credentials from shared test data workbooks or environment."""
    return _central_read_credentials(role=role, sheet_name=SHEET_NAME)


def load_test_cases(sheet_name: str = SHEET_NAME) -> List[Dict[str, Any]]:
    """
    Read all test case rows for invoice update module.
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


read_test_cases = load_test_cases


def is_ui_case(tc: Dict[str, Any]) -> bool:
    """Check if test case is an active UI test case."""
    exec_type = str(tc.get("Execution Type", "UI")).strip().upper()
    auto_status = str(tc.get("Automation Status", "Automated")).strip().lower()
    is_ui = "UI" in exec_type or "AUTOMATED" in exec_type or exec_type == ""
    return is_ui and auto_status not in ("excluded", "not automated", "manual", "deferred")


def get_baseline_invoice() -> Dict[str, Any]:
    """Fetch baseline valid invoice test data dynamically from Swarajya-test-data.xlsx."""
    try:
        data_map = read_data_sheet(SHEET_NAME)
        for tc_id, row in data_map.items():
            if "POS" in tc_id.upper() and (row.get("Customer Name") or row.get("Invoice ID / Invoice No")):
                res = {}
                for k, v in row.items():
                    val = str(v).strip() if v is not None else ""
                    if val.endswith(".0") and val[:-2].isdigit():
                        val = val[:-2]
                    res[k] = val
                return res
    except Exception as exc:
        log.warning(f"Could not load baseline invoice from Excel: {exc}")
    return {}


def update_test_result(
    tc_id: str,
    status: str = "Passed",
    remarks: Optional[str] = None,
    error_message: Optional[str] = None,
    duration_s: Optional[float] = None,
    execution_time: Optional[float] = None,
    duration: Optional[float] = None,
    file_path: Optional[str] = None,
    sheet_name: str = SHEET_NAME,
    **kwargs,
) -> bool:
    """Update execution results in the central test cases workbook."""
    rem = remarks or error_message or kwargs.get("remark") or ""
    dur = duration_s or execution_time or duration
    if dur:
        rem = f"{rem} ({dur:.2f}s)" if rem else f"({dur:.2f}s)"
    return _central_update_test_result(
        tc_id=tc_id,
        status=status,
        remarks=rem,
        duration=dur,
        module_key=MODULE_KEY,
        sheet_name=sheet_name or SHEET_NAME,
    )
