"""
Excel Reader and Synchronization Utility for Customer Insights Automation.

Strictly adheres to framework ZERO-HARDCODING standard:
- Test cases loaded dynamically from Swarajya-test-cases.xlsx [Sheet: readcustomer_insights]
- Test data & credentials loaded dynamically from Swarajya-test-data.xlsx [Sheet: readcustomer_insights]
- Bi-directional test result updates to Excel workbooks with PASS/FAIL styling
- Dynamic template token resolution for {{base_url}}, {{actual_revenue_endpoint}}, {{period}}, etc.
"""

import os
import re
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill

from shared.utils.logger import get_logger
from shared.utils.paths import (
    SHARED_TEST_DATA_DIR,
    TEST_CASES_FILE,
    TEST_DATA_FILE,
)
from shared.utils.excel_base import (
    _find_sheet,
    get_base_url as _shared_get_base_url,
    read_credentials as _shared_read_credentials,
    update_test_result as _shared_update_test_result,
    build_automation_id as _shared_build_automation_id,
)

log = get_logger("CustomerInsightsExcelReader")

CASES_SHEET = "readcustomer_insights"
DATA_SHEET = "readcustomer_insights"

# Styling constants for Excel cell updates
_PASS_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
_PASS_FONT = Font(color="006100", bold=True)
_FAIL_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
_FAIL_FONT = Font(color="9C0006", bold=True)
_SKIP_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
_SKIP_FONT = Font(color="9C6500", bold=True)


def _resolve_file_path(default_path: str, pattern: str) -> str:
    """Resolve file path, falling back to glob matching if default does not exist."""
    if os.path.exists(default_path):
        return default_path
    import glob
    candidates = sorted(glob.glob(os.path.join(SHARED_TEST_DATA_DIR, pattern)), key=os.path.getmtime, reverse=True)
    if candidates:
        return candidates[0]
    return default_path


def get_cases_file_path() -> str:
    """Return the absolute path to the test cases workbook."""
    return _resolve_file_path(TEST_CASES_FILE, "Swarajya-test-cases*.xlsx")


def get_data_file_path() -> str:
    """Return the absolute path to the test data workbook."""
    return _resolve_file_path(TEST_DATA_FILE, "Swarajya-test-data*.xlsx")


def get_base_url() -> str:
    """
    Fetch the Base URL dynamically from environment variables or Excel sheet banner.
    ZERO hardcoding.
    """
    env_url = os.environ.get("SWARAJYA_BASE_URL") or os.environ.get("BASE_URL")
    if env_url:
        return env_url.rstrip("/")

    data_path = get_data_file_path()
    if os.path.exists(data_path):
        try:
            wb = openpyxl.load_workbook(data_path, data_only=True)
            sheet_name = _find_sheet(wb, DATA_SHEET) or DATA_SHEET
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                for row in ws.iter_rows(min_row=1, max_row=3, values_only=True):
                    for cell in row:
                        if cell and str(cell).strip().lower().startswith(("http://", "https://")):
                            wb.close()
                            return str(cell).strip().rstrip("/")
            wb.close()
        except Exception as e:
            log.warning(f"Error reading base URL from {data_path}: {e}")

    return _shared_get_base_url().rstrip("/")


def read_api_credentials(role: str = "Admin") -> Dict[str, str]:
    """
    Read credentials dynamically from environment variables or the Excel workbook banner.
    Returns: { 'role', 'user_id', 'employee_id', 'password', 'auth_code', 'base_url' }
    """
    env_user = os.environ.get("SWARAJYA_USER_ID") or os.environ.get("SWARAJYA_EMPLOYEE_ID")
    env_pass = os.environ.get("SWARAJYA_PASSWORD")
    env_auth = os.environ.get("SWARAJYA_AUTH_CODE")
    env_base = os.environ.get("SWARAJYA_BASE_URL")

    if env_user and env_pass:
        return {
            "role": role,
            "user_id": str(env_user).strip(),
            "employee_id": str(env_user).strip(),
            "password": str(env_pass).strip(),
            "auth_code": str(env_auth or "").strip(),
            "base_url": str(env_base or get_base_url()).rstrip("/"),
        }

    data_path = get_data_file_path()
    if os.path.exists(data_path):
        try:
            wb = openpyxl.load_workbook(data_path, data_only=True)
            sheet_name = _find_sheet(wb, DATA_SHEET) or DATA_SHEET
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                rows = list(ws.iter_rows(min_row=1, max_row=2, values_only=True))
                if len(rows) >= 2:
                    row1 = [str(c).strip().lower() if c is not None else "" for c in rows[0]]
                    row2 = list(rows[1])

                    url_idx = next((i for i, h in enumerate(row1) if "url" in h), None)
                    id_idx = next((i for i, h in enumerate(row1) if "user" in h or "id" in h), None)
                    pwd_idx = next((i for i, h in enumerate(row1) if "pass" in h), None)
                    auth_idx = next((i for i, h in enumerate(row1) if "code" in h or "auth" in h), None)

                    base_url = str(row2[url_idx]).strip() if url_idx is not None and row2[url_idx] else get_base_url()
                    user_id = str(int(row2[id_idx])) if id_idx is not None and isinstance(row2[id_idx], (int, float)) and int(row2[id_idx]) == row2[id_idx] else str(row2[id_idx] or "" if id_idx is not None else "")
                    pwd = str(row2[pwd_idx] or "").strip() if pwd_idx is not None else ""
                    auth_code = str(int(row2[auth_idx])) if auth_idx is not None and isinstance(row2[auth_idx], (int, float)) and int(row2[auth_idx]) == row2[auth_idx] else str(row2[auth_idx] or "").strip() if auth_idx is not None else ""

                    wb.close()
                    if user_id and pwd:
                        return {
                            "role": role,
                            "user_id": user_id,
                            "employee_id": user_id,
                            "password": pwd,
                            "auth_code": auth_code,
                            "base_url": base_url.rstrip("/"),
                        }
            wb.close()
        except Exception as e:
            log.warning(f"Error reading credentials from {data_path}: {e}")

    # Fallback to shared loader
    shared_creds = _shared_read_credentials(role=role, sheet_name="loginhr_admin")
    return {
        "role": shared_creds.get("role", role),
        "user_id": shared_creds.get("employee_id", ""),
        "employee_id": shared_creds.get("employee_id", ""),
        "password": shared_creds.get("password", ""),
        "auth_code": shared_creds.get("auth_code", ""),
        "base_url": shared_creds.get("base_url", get_base_url()),
    }


def load_customer_insights_test_cases() -> List[Dict[str, Any]]:
    """
    Load test case definitions from Swarajya-test-cases.xlsx [Sheet: readcustomer_insights].
    """
    path = get_cases_file_path()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test cases workbook not found at: {path}")

    wb = openpyxl.load_workbook(path, data_only=True)
    real_sheet = _find_sheet(wb, CASES_SHEET) or CASES_SHEET
    if real_sheet not in wb.sheetnames:
        wb.close()
        raise ValueError(f"Sheet '{CASES_SHEET}' not found in {path}. Available sheets: {wb.sheetnames}")

    ws = wb[real_sheet]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not rows:
        return []

    # Headers on row 1
    headers = [str(c).strip() if c is not None else f"col_{i}" for i, c in enumerate(rows[0])]
    cases = []
    for r in rows[1:]:
        if not r or not any(x is not None for x in r):
            continue
        case_dict = {}
        for h, val in zip(headers, r):
            if isinstance(val, float) and val.is_integer():
                val = str(int(val))
            elif isinstance(val, datetime):
                val = val.strftime("%d-%m-%Y")
            elif val is not None:
                val = str(val).strip()
            case_dict[h] = val
        if case_dict.get("Test Case ID"):
            cases.append(case_dict)

    log.info(f"Loaded {len(cases)} test cases from sheet '{real_sheet}'")
    return cases


def load_customer_insights_test_data() -> List[Dict[str, Any]]:
    """
    Load test data from Swarajya-test-data.xlsx [Sheet: readcustomer_insights].
    Header is expected at row 4.
    """
    path = get_data_file_path()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test data workbook not found at: {path}")

    wb = openpyxl.load_workbook(path, data_only=True)
    real_sheet = _find_sheet(wb, DATA_SHEET) or DATA_SHEET
    if real_sheet not in wb.sheetnames:
        wb.close()
        raise ValueError(f"Sheet '{DATA_SHEET}' not found in {path}. Available sheets: {wb.sheetnames}")

    ws = wb[real_sheet]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not rows:
        return []

    # Locate table header row containing 'Test Case ID'
    header_idx = None
    for idx, r in enumerate(rows[:10]):
        row_str = " ".join(str(c).lower() for c in r if c is not None)
        if "test case id" in row_str:
            header_idx = idx
            break

    if header_idx is None:
        header_idx = 3 if len(rows) > 3 else 0

    header_row = rows[header_idx]
    data_rows = rows[header_idx + 1:]

    headers = [str(c).strip() if c is not None else f"col_{i}" for i, c in enumerate(header_row)]
    results = []

    for r in data_rows:
        if not r or not any(x is not None for x in r):
            continue
        record = {}
        for h, val in zip(headers, r):
            if isinstance(val, float) and val.is_integer():
                val = str(int(val))
            elif isinstance(val, datetime):
                val = val.strftime("%d-%m-%Y")
            elif val is not None:
                val = str(val).strip()
            record[h] = val
        if record.get("Test Case ID"):
            results.append(record)

    log.info(f"Loaded {len(results)} test data records from sheet '{real_sheet}'")
    return results


def resolve_endpoint_template(
    endpoint_template: str,
    base_url: Optional[str] = None,
    actual_endpoint: Optional[str] = None,
    period: Optional[str] = None,
    supported_empty_period: Optional[str] = None,
) -> str:
    """
    Dynamically resolve template tokens inside an endpoint string:
    - {{base_url}} -> active base URL
    - {{actual_revenue_endpoint}} -> active customer insights/revenue API endpoint path
    - {{period}} -> fiscal period parameter
    - {{supported_empty_period}} -> supported empty period parameter
    """
    resolved_base = (base_url or get_base_url()).rstrip("/")
    resolved_actual = (
        actual_endpoint
        or os.environ.get("CUSTOMER_INSIGHTS_ENDPOINT")
        or "api/v1/customer-insights/revenue"
    ).strip("/")

    resolved = endpoint_template
    resolved = resolved.replace("{{base_url}}", resolved_base)
    resolved = resolved.replace("{{actual_revenue_endpoint}}", resolved_actual)

    if period:
        resolved = resolved.replace("{{period}}", period)
    if supported_empty_period:
        resolved = resolved.replace("{{supported_empty_period}}", supported_empty_period)
    else:
        resolved = resolved.replace("{{supported_empty_period}}", "EMPTY_FY")

    return resolved


def get_merged_test_suite(category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Merge test definitions with input test data matching by 'Test Case ID'.
    """
    cases = load_customer_insights_test_cases()
    data = load_customer_insights_test_data()

    cases_map = {c["Test Case ID"]: c for c in cases if c.get("Test Case ID")}
    data_map = {d["Test Case ID"]: d for d in data if d.get("Test Case ID")}

    all_ids = list(dict.fromkeys(list(cases_map.keys()) + list(data_map.keys())))
    merged = []

    for tc_id in all_ids:
        c = cases_map.get(tc_id, {})
        d = data_map.get(tc_id, {})

        raw_endpoint = d.get("Endpoint") or ""
        item = {
            "tc_id": tc_id,
            "Test Case ID": tc_id,
            "category": d.get("Category") or ("Positive" if "_POS_" in tc_id else "Negative"),
            "scenario": d.get("Scenario") or c.get("Scenario", ""),
            "pre_condition": d.get("Pre-condition") or c.get("Pre-condition", ""),
            "test_steps": d.get("Test Steps") or c.get("Test Steps", ""),
            "method": d.get("Method", "GET"),
            "raw_endpoint": raw_endpoint,
            "endpoint": resolve_endpoint_template(raw_endpoint),
            "headers": d.get("Headers") or "Authorization: Bearer {token}, Accept: application/json",
            "expected_status": d.get("Expected Status") or "200 OK",
            "expected_outcome": d.get("Expected Outcome") or "",
            "assertions": d.get("Assertions") or c.get("Expected Result", ""),
            "status": c.get("Test Status", "Pending"),
            "remarks": c.get("Remarks / Defect Observed", ""),
        }

        if category_filter:
            cat_upper = category_filter.upper()
            if "POS" in cat_upper and "_POS_" not in tc_id:
                continue
            if "NEG" in cat_upper and "_NEG_" not in tc_id:
                continue

        merged.append(item)

    return merged


def get_test_case_by_id(tc_id: str) -> Optional[Dict[str, Any]]:
    """Fetch test case definition by Test Case ID."""
    cases = load_customer_insights_test_cases()
    for c in cases:
        if str(c.get("Test Case ID", "")).strip().upper() == tc_id.strip().upper():
            return c
    return None


def get_test_data_by_id(tc_id: str) -> Optional[Dict[str, Any]]:
    """Fetch test data record by Test Case ID."""
    data = load_customer_insights_test_data()
    for d in data:
        if str(d.get("Test Case ID", "")).strip().upper() == tc_id.strip().upper():
            # Return copy with resolved endpoint as well
            record = dict(d)
            record["Resolved Endpoint"] = resolve_endpoint_template(str(d.get("Endpoint", "")))
            return record
    return None


def build_automation_id(tc_id: str) -> str:
    """Generate normalized script ID like AUT_CUST_INS_POS_01."""
    return _shared_build_automation_id("CUST_INS", tc_id)


def update_test_result(
    tc_id: str,
    status: str,
    remarks: str = "",
    auto_id: str = "",
) -> None:
    """
    Update test execution result in both Swarajya-test-cases.xlsx and Swarajya-test-data.xlsx.
    Colors the cell green (PASS) or red (FAIL) and records defect remarks.
    """
    clean_status = status.upper().strip()
    if clean_status not in ("PASS", "FAIL", "SKIPPED", "BLOCKED"):
        clean_status = "PASS" if "PASS" in clean_status else ("FAIL" if "FAIL" in clean_status else "SKIPPED")

    generated_auto_id = auto_id or build_automation_id(tc_id)

    # 1. Update in test cases workbook
    cases_path = get_cases_file_path()
    try:
        _shared_update_test_result(
            CASES_SHEET,
            tc_id,
            clean_status,
            remarks=remarks,
            auto_id_or_sheet=generated_auto_id,
            file_path=cases_path,
        )
        log.info(f"Updated {cases_path} [{CASES_SHEET}] for {tc_id} -> {clean_status}")
    except Exception as e:
        log.warning(f"Could not update test cases file {cases_path}: {e}")

    # 2. Update in test data workbook
    data_path = get_data_file_path()
    try:
        wb = openpyxl.load_workbook(data_path)
        real_data_sheet = _find_sheet(wb, DATA_SHEET) or DATA_SHEET
        if real_data_sheet in wb.sheetnames:
            ws = wb[real_data_sheet]
            header_idx = None
            for idx, r in enumerate(list(ws.iter_rows(values_only=True))[:10]):
                if "test case id" in " ".join(str(c).lower() for c in r if c is not None):
                    header_idx = idx + 1
                    break

            if header_idx:
                headers = [str(ws.cell(header_idx, c).value or "").strip() for c in range(1, ws.max_column + 1)]
                tc_col = next((i + 1 for i, h in enumerate(headers) if "test case id" in h.lower()), 1)
                status_col = next((i + 1 for i, h in enumerate(headers) if h.lower() in ("status", "test status")), None)

                if status_col:
                    for row_num in range(header_idx + 1, ws.max_row + 1):
                        cell_tc = str(ws.cell(row_num, tc_col).value or "").strip()
                        if cell_tc.upper() == tc_id.upper():
                            stat_cell = ws.cell(row_num, status_col)
                            stat_cell.value = clean_status
                            if clean_status == "PASS":
                                stat_cell.fill = _PASS_FILL
                                stat_cell.font = _PASS_FONT
                            elif clean_status == "FAIL":
                                stat_cell.fill = _FAIL_FILL
                                stat_cell.font = _FAIL_FONT
                            else:
                                stat_cell.fill = _SKIP_FILL
                                stat_cell.font = _SKIP_FONT
                            break

            wb.save(data_path)
            log.info(f"Updated {data_path} [{real_data_sheet}] for {tc_id} -> {clean_status}")
        wb.close()
    except Exception as e:
        log.warning(f"Could not update test data file {data_path}: {e}")
