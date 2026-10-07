"""
Common Excel Reader & Result Updater for Swarajya Login Modules.

Strictly reads test data and test cases from shared workbooks:
- `shared/test_data/Swarajya-test-data.xlsx`
- `shared/test_data/Swarajya-test-cases.xlsx`

Supports both sheets:
- `loginhr_admin` (Admin & HR)
- `loginemp-manager` (Employee & Manager)
"""

import os
import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import openpyxl
from openpyxl.styles import Font, PatternFill

logger = logging.getLogger(__name__)

# Paths
_COMMON_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
_COMMON_DIR = os.path.dirname(_COMMON_UTILS_DIR)
_LOGIN_DIR = os.path.dirname(_COMMON_DIR)
_WORKSPACE_ROOT = os.path.dirname(_LOGIN_DIR)

SHARED_TEST_DATA_DIR = os.path.join(_WORKSPACE_ROOT, "shared", "test_data")
TEST_DATA_FILE = os.path.join(SHARED_TEST_DATA_DIR, "Swarajya-test-data.xlsx")
TEST_CASES_FILE = os.path.join(SHARED_TEST_DATA_DIR, "Swarajya-test-cases.xlsx")

# Result cell styling
_PASS_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
_PASS_FONT = Font(color="006100", bold=True)
_FAIL_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
_FAIL_FONT = Font(color="9C0006", bold=True)
_SKIP_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
_SKIP_FONT = Font(color="9C6500", bold=True)


def _find_sheet(wb: openpyxl.Workbook, sheet_name: str) -> Optional[str]:
    """Find sheet name case-insensitively and ignoring hyphens/underscores/slashes."""
    target_clean = re.sub(r"[-_/\s]", "", sheet_name.lower())
    for name in wb.sheetnames:
        if re.sub(r"[-_/\s]", "", name.lower()) == target_clean:
            return name
    return None


def get_base_url(sheet_name: str = "loginhr_admin", file_path: Optional[str] = None) -> str:
    """Fetch the Base URL strictly from the test data Excel sheet."""
    path = file_path or TEST_DATA_FILE
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test data file not found at: {path}")

    wb = openpyxl.load_workbook(path, data_only=True)
    real_sheet = _find_sheet(wb, sheet_name)
    if not real_sheet:
        wb.close()
        raise ValueError(f"Sheet '{sheet_name}' not found in {path}. Available: {wb.sheetnames}")

    ws = wb[real_sheet]
    headers = [str(c.value).strip().lower() if c.value is not None else "" for c in ws[1]]
    url_idx = next((i for i, h in enumerate(headers) if "url" in h), 0)

    for row in ws.iter_rows(min_row=2, values_only=True):
        if row and row[url_idx]:
            val = str(row[url_idx]).strip()
            wb.close()
            return val

    wb.close()
    return "https://swarajya-stg.corecotechnologies.com"


def read_credentials(
    role: str = "Admin",
    sheet_name: Optional[str] = None,
    file_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Strictly fetch user credentials for a role from the test data Excel workbook.
    Auto-detects sheet ('loginhr_admin' for Admin/HR, 'loginemp-manager' for Employee/Manager)
    if sheet_name is not provided.
    """
    path = file_path or TEST_DATA_FILE
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test data workbook not found at: {path}")

    wb = openpyxl.load_workbook(path, data_only=True)
    target_role = role.strip().lower()

    # Determine sheets to search
    if sheet_name:
        candidate_sheets = [sheet_name]
    elif target_role in ("admin", "hr"):
        candidate_sheets = ["loginhr_admin", "loginemp-manager"]
    else:
        candidate_sheets = ["loginemp-manager", "loginhr_admin"]

    for sname in candidate_sheets:
        real_sheet = _find_sheet(wb, sname)
        if not real_sheet:
            continue
        ws = wb[real_sheet]
        headers = [str(c.value).strip().lower() if c.value is not None else "" for c in ws[1]]

        role_idx = next((i for i, h in enumerate(headers) if "role" in h), 1)
        url_idx = next((i for i, h in enumerate(headers) if "url" in h), 0)
        id_idx = next((i for i, h in enumerate(headers) if "id" in h or "emp" in h), 2)
        pwd_idx = next((i for i, h in enumerate(headers) if "pass" in h), 3)
        auth_idx = next((i for i, h in enumerate(headers) if "auth" in h or "code" in h), 4)
        valid_idx = next((i for i, h in enumerate(headers) if "valid" in h), 5)

        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[role_idx]:
                continue
            row_role = str(row[role_idx]).strip()
            if row_role.lower() == target_role:
                emp_id = row[id_idx]
                auth_code = row[auth_idx]
                emp_id_str = str(int(emp_id)) if isinstance(emp_id, (int, float)) and int(emp_id) == emp_id else str(emp_id).strip()
                auth_code_str = str(int(auth_code)) if isinstance(auth_code, (int, float)) and int(auth_code) == auth_code else str(auth_code).strip()
                base_url = str(row[url_idx]).strip() if url_idx < len(row) and row[url_idx] else ""
                is_valid = str(row[valid_idx]).strip().lower() == "yes" if valid_idx < len(row) and row[valid_idx] else True

                wb.close()
                return {
                    "role": row_role,
                    "employee_id": emp_id_str,
                    "password": str(row[pwd_idx]).strip() if row[pwd_idx] else "",
                    "auth_code": auth_code_str,
                    "base_url": base_url or get_base_url(sheet_name=real_sheet, file_path=path),
                    "is_valid": is_valid,
                }

    wb.close()
    raise ValueError(f"Role '{role}' not found in Excel test data sheets: {candidate_sheets}")


def read_all_credentials(
    sheet_name: str = "loginhr_admin",
    file_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Read all credentials from the specified test data sheet."""
    path = file_path or TEST_DATA_FILE
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test data workbook not found at: {path}")

    wb = openpyxl.load_workbook(path, data_only=True)
    real_sheet = _find_sheet(wb, sheet_name)
    if not real_sheet:
        wb.close()
        raise ValueError(f"Sheet '{sheet_name}' not found in {path}. Available: {wb.sheetnames}")

    ws = wb[real_sheet]
    headers = [str(c.value).strip().lower() if c.value is not None else "" for c in ws[1]]

    role_idx = next((i for i, h in enumerate(headers) if "role" in h), 1)
    url_idx = next((i for i, h in enumerate(headers) if "url" in h), 0)
    id_idx = next((i for i, h in enumerate(headers) if "id" in h or "emp" in h), 2)
    pwd_idx = next((i for i, h in enumerate(headers) if "pass" in h), 3)
    auth_idx = next((i for i, h in enumerate(headers) if "auth" in h or "code" in h), 4)
    valid_idx = next((i for i, h in enumerate(headers) if "valid" in h), 5)

    creds = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[role_idx]:
            continue
        emp_id = row[id_idx]
        auth_code = row[auth_idx]
        emp_id_str = str(int(emp_id)) if isinstance(emp_id, (int, float)) and int(emp_id) == emp_id else str(emp_id).strip()
        auth_code_str = str(int(auth_code)) if isinstance(auth_code, (int, float)) and int(auth_code) == auth_code else str(auth_code).strip()
        creds.append({
            "role": str(row[role_idx]).strip(),
            "employee_id": emp_id_str,
            "password": str(row[pwd_idx]).strip() if row[pwd_idx] else "",
            "auth_code": auth_code_str,
            "base_url": str(row[url_idx]).strip() if url_idx < len(row) and row[url_idx] else "",
            "is_valid": str(row[valid_idx]).strip().lower() == "yes" if valid_idx < len(row) and row[valid_idx] else True,
        })

    wb.close()
    return creds


def load_test_cases(
    sheet_name: str = "loginhr_admin",
    file_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Load test case definitions from Swarajya-test-cases.xlsx for the specified sheet."""
    path = file_path or TEST_CASES_FILE
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test cases workbook not found at: {path}")

    wb = openpyxl.load_workbook(path, data_only=True)
    real_sheet = _find_sheet(wb, sheet_name)
    if not real_sheet:
        wb.close()
        raise ValueError(f"Sheet '{sheet_name}' not found in {path}. Available: {wb.sheetnames}")

    ws = wb[real_sheet]
    headers = [str(c.value).strip() if c.value is not None else f"col_{i}" for i, c in enumerate(ws[1])]
    cases = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not any(x is not None for x in row):
            continue
        case_dict = {}
        for h, val in zip(headers, row):
            if isinstance(val, (int, float)) and isinstance(val, float) and val.is_integer():
                val = str(int(val))
            elif isinstance(val, datetime):
                val = val.strftime("%d-%m-%Y")
            elif val is not None:
                val = str(val).strip()
            case_dict[h] = val
        if case_dict.get("Test Case ID"):
            cases.append(case_dict)

    wb.close()
    return cases


def get_test_case_by_id(
    tc_id: str,
    sheet_name: Optional[str] = None,
    file_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve metadata for a specific Test Case ID."""
    sheets = [sheet_name] if sheet_name else ["loginhr_admin", "loginemp-manager"]
    for s in sheets:
        try:
            cases = load_test_cases(sheet_name=s, file_path=file_path)
            for c in cases:
                if str(c.get("Test Case ID", "")).strip() == tc_id.strip():
                    return c
        except Exception:
            continue
    return None


def update_test_result(
    tc_id: str,
    result: str,
    remarks: str = "",
    sheet_name: Optional[str] = None,
    file_path: Optional[str] = None,
):
    """
    Update Test Status, Remarks / Defect Observed, and Automation Status
    in Swarajya-test-cases.xlsx. Searches both loginhr_admin and loginemp-manager
    to find the matching Test Case ID.
    """
    path = file_path or TEST_CASES_FILE
    if not os.path.exists(path):
        logger.warning("Test cases file not found at %s; skipping result update", path)
        return

    try:
        wb = openpyxl.load_workbook(path)
        candidates = [sheet_name] if sheet_name else []
        for s in ["loginhr_admin", "loginemp-manager"]:
            if s not in candidates:
                candidates.append(s)

        updated = False
        for sname in candidates:
            real_sheet = _find_sheet(wb, sname)
            if not real_sheet:
                continue

            ws = wb[real_sheet]
            headers = [str(cell.value).strip() if cell.value else "" for cell in ws[1]]

            tc_col = headers.index("Test Case ID") + 1 if "Test Case ID" in headers else 1
            status_col = (headers.index("Test Status") + 1 if "Test Status" in headers
                          else (headers.index("Automation_Result") + 1 if "Automation_Result" in headers else None))
            auto_status_col = headers.index("Automation Status") + 1 if "Automation Status" in headers else None
            remarks_col = (headers.index("Remarks / Defect Observed") + 1 if "Remarks / Defect Observed" in headers
                           else (headers.index("Remarks") + 1 if "Remarks" in headers else None))

            for row_idx in range(2, ws.max_row + 1):
                cell_val = str(ws.cell(row=row_idx, column=tc_col).value or "").strip()
                if cell_val == tc_id.strip():
                    if status_col:
                        res_cell = ws.cell(row=row_idx, column=status_col, value=result)
                        if result == "PASS":
                            res_cell.fill = _PASS_FILL
                            res_cell.font = _PASS_FONT
                        elif result == "FAIL":
                            res_cell.fill = _FAIL_FILL
                            res_cell.font = _FAIL_FONT
                        elif result in ("SKIPPED", "BLOCKED"):
                            res_cell.fill = _SKIP_FILL
                            res_cell.font = _SKIP_FONT

                    if auto_status_col:
                        ws.cell(row=row_idx, column=auto_status_col, value="Automated")

                    if remarks_col:
                        ws.cell(row=row_idx, column=remarks_col, value=remarks or ("None" if result == "PASS" else ""))

                    logger.info("Updated Excel %s [%s]: Status=%s", real_sheet, tc_id, result)
                    updated = True
                    break

            if updated:
                break

        wb.save(path)
        wb.close()
    except Exception as exc:
        logger.warning("Could not update Excel test result for %s: %s", tc_id, exc)
