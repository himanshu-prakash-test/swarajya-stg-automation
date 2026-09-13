import glob
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import openpyxl
from shared.utils.logger import get_logger

logger = get_logger("excel_reader")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = os.path.join(ROOT, "test_data")
CREDENTIALS_FILE = os.path.join(TEST_DATA_DIR, "credentials.xlsx")


def get_test_cases_filepath() -> str:
    """Find Create-Customer-Management.xlsx in test_data directory."""
    target = os.path.join(TEST_DATA_DIR, "Create-Customer-Management.xlsx")
    if os.path.exists(target):
        return target
    candidates = glob.glob(os.path.join(TEST_DATA_DIR, "*customer*.xlsx"))
    if candidates:
        return candidates[0]
    raise FileNotFoundError(f"No customer test cases Excel file found in: {TEST_DATA_DIR}")


def read_credentials(role: str = "Admin") -> Dict[str, str]:
    """Read login credentials for the given role from credentials.xlsx."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_FILE}")

    wb = openpyxl.load_workbook(CREDENTIALS_FILE, data_only=True)
    ws = wb["Credentials"] if "Credentials" in wb.sheetnames else wb.active
    headers = [cell.value for cell in ws[1]]

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue
        row_dict = dict(zip(headers, row))
        row_role = str(row_dict.get("Role", "")).strip().lower()
        if row_role == role.strip().lower() or (
            role.lower() in ("admin", "manager") and row_role in ("admin", "manager", "employee")
        ):
            wb.close()
            return {
                "role": str(row_dict.get("Role", "")).strip(),
                "employee_id": str(row_dict.get("Employee_ID", "")).strip(),
                "password": str(row_dict.get("Password", "")).strip(),
                "auth_code": str(row_dict.get("Auth_Code", "111111")).strip(),
            }

    wb.close()
    return {"role": "Admin", "employee_id": "332", "password": "test@1234", "auth_code": "111111"}


def read_test_cases(sheet_name: str) -> List[Dict[str, Any]]:
    """Read test case rows from specified sheet in Create-Customer-Management.xlsx."""
    file_path = get_test_cases_filepath()
    wb = openpyxl.load_workbook(file_path, data_only=True)

    if sheet_name not in wb.sheetnames:
        wb.close()
        raise ValueError(f"Sheet '{sheet_name}' not found in {file_path}. Available: {wb.sheetnames}")

    ws = wb[sheet_name]
    headers = [cell.value for cell in ws[1]]

    test_cases = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue
        row_dict = dict(zip(headers, row))
        tc_id = row_dict.get("Test Case ID")
        if tc_id and str(tc_id).strip().startswith("TC_CUSTOMER"):
            row_dict["_sheet"] = sheet_name
            if "Test Steps" in row_dict and "Steps" not in row_dict:
                row_dict["Steps"] = row_dict["Test Steps"]
            test_cases.append(row_dict)

    wb.close()
    logger.info("Loaded %d test cases from '%s'", len(test_cases), sheet_name)
    return test_cases


def is_ui_case(tc: Dict[str, Any]) -> bool:
    """Check if test case execution type is UI and active for automation."""
    exec_type = str(tc.get("Execution Type", "UI")).strip().upper()
    auto_status = str(tc.get("Automation Status", "Automated")).strip().lower()
    return exec_type == "UI" and auto_status not in ("excluded", "not automated", "manual", "deferred")


def build_automation_id(tc_id: str) -> str:
    """Generate automation script ID from test case ID (e.g. TC_CUSTOMER_POS_01 -> AUT_CUSTOMER_POS_01)."""
    return tc_id.replace("TC_", "AUT_")


def update_test_result(
    tc_id: str,
    status: str,
    error_message: Optional[str] = None,
    execution_time: Optional[float] = None,
):
    """Update test case execution status and remarks in the Excel sheet."""
    try:
        file_path = get_test_cases_filepath()
        wb = openpyxl.load_workbook(file_path)

        updated = False
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            headers = [cell.value for cell in ws[1]]
            if "Test Case ID" not in headers:
                continue

            tc_id_col = headers.index("Test Case ID") + 1
            status_col = headers.index("Test Status") + 1 if "Test Status" in headers else None
            remarks_col = headers.index("Remarks") + 1 if "Remarks" in headers else None
            auto_id_col = headers.index("Auto Script ID") + 1 if "Auto Script ID" in headers else None

            for row_idx in range(2, ws.max_row + 1):
                val = ws.cell(row=row_idx, column=tc_id_col).value
                if val and str(val).strip() == tc_id:
                    if status_col:
                        ws.cell(row=row_idx, column=status_col, value=status)
                    if auto_id_col:
                        ws.cell(row=row_idx, column=auto_id_col, value=build_automation_id(tc_id))
                    if remarks_col:
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        remarks_val = f"{now_str} - {status}"
                        if error_message:
                            remarks_val += f": {error_message[:150]}"
                        ws.cell(row=row_idx, column=remarks_col, value=remarks_val)
                    updated = True
                    break

            if updated:
                break

        if updated:
            wb.save(file_path)
            logger.info("Updated Excel result for %s: %s", tc_id, status)
        wb.close()
    except Exception as exc:
        logger.warning("Could not update Excel test result for %s: %s", tc_id, exc)
