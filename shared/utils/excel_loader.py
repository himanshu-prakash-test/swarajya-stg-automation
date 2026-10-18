"""
Central Excel reader and data provider for Swarajya Automation.
Loads test definitions from Swarajya-test-cases.xlsx and input data from Swarajya-test-data.xlsx.
Merges cases and data seamlessly by 'Test Case ID'.
"""

import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import openpyxl

from shared.utils.logger import get_logger
from shared.utils.paths import (
    AUTH_STATE_FILE,
    CREDENTIALS_FILE,
    SHARED_TEST_DATA_DIR,
    TEST_CASES_FILE,
    TEST_DATA_DIR,
    TEST_DATA_FILE,
    WORKSPACE_ROOT,
)

logger = get_logger("excel_loader")

# Normalized mapping between module keys and sheet names in both workbooks
# Format: module_key: (test_cases_sheet_name, test_data_sheet_name)
MODULE_SHEET_MAP = {
    # Vendor
    "vendor": ("createvendor-mgmt", "createvendor-mgmt"),
    "createvendor": ("createvendor-mgmt", "createvendor-mgmt"),
    "createvendor-mgmt": ("createvendor-mgmt", "createvendor-mgmt"),
    "vendor-management": ("createvendor-mgmt", "createvendor-mgmt"),
    "create/vendor-mgmt": ("createvendor-mgmt", "createvendor-mgmt"),
    "create/vendor_mgmt": ("createvendor-mgmt", "createvendor-mgmt"),
    # Customer (cases sheet: createcutomer-mgmt, data sheet: createcustomer-mgmt)
    "customer": ("createcutomer-mgmt", "createcustomer-mgmt"),
    "createcustomer": ("createcutomer-mgmt", "createcustomer-mgmt"),
    "createcustomer-mgmt": ("createcutomer-mgmt", "createcustomer-mgmt"),
    "createcutomer-mgmt": ("createcutomer-mgmt", "createcustomer-mgmt"),
    "customer-management": ("createcutomer-mgmt", "createcustomer-mgmt"),
    "create/customer-mgmt": ("createcutomer-mgmt", "createcustomer-mgmt"),
    "create/customer_mgmt": ("createcutomer-mgmt", "createcustomer-mgmt"),
    # Consultant
    "consultant": ("createconsultant_mgmt", "createconsultant_mgmt"),
    "createconsultant": ("createconsultant_mgmt", "createconsultant_mgmt"),
    "createconsultant_mgmt": ("createconsultant_mgmt", "createconsultant_mgmt"),
    "consultant-management": ("createconsultant_mgmt", "createconsultant_mgmt"),
    "create/consultant-mgmt": ("createconsultant_mgmt", "createconsultant_mgmt"),
    "create/consultant_mgmt": ("createconsultant_mgmt", "createconsultant_mgmt"),
    # Purchase Order
    "purchase_order": ("createpurchase_order", "createpurchase_order"),
    "po": ("createpurchase_order", "createpurchase_order"),
    "createpurchase_order": ("createpurchase_order", "createpurchase_order"),
    "purchase-order": ("createpurchase_order", "createpurchase_order"),
    "create/purchase-order": ("createpurchase_order", "createpurchase_order"),
    "create/purchase_order": ("createpurchase_order", "createpurchase_order"),
    # Employee
    "employee": ("createemp-mgmt", "createemp-mgmt"),
    "emp": ("createemp-mgmt", "createemp-mgmt"),
    "createemp-mgmt": ("createemp-mgmt", "createemp-mgmt"),
    "employee-management": ("createemp-mgmt", "createemp-mgmt"),
    "create/emp-mgmt": ("createemp-mgmt", "createemp-mgmt"),
    "create/emp_mgmt": ("createemp-mgmt", "createemp-mgmt"),
    "createemp_mgmt": ("createemp-mgmt", "createemp-mgmt"),
    # Invoice
    "invoice": ("createinvoice-mgmt", "createinvoice-mgmt"),
    "createinvoice": ("createinvoice-mgmt", "createinvoice-mgmt"),
    "createinvoice-mgmt": ("createinvoice-mgmt", "createinvoice-mgmt"),
    "create/invoice-mgmt": ("createinvoice-mgmt", "createinvoice-mgmt"),
    "create/invoice_mgmt": ("createinvoice-mgmt", "createinvoice-mgmt"),
    # Login modules
    "login_hr_admin": ("loginhr_admin", "loginhr_admin"),
    "loginhr_admin": ("loginhr_admin", "loginhr_admin"),
    "login_emp_manager": ("loginemp-manager", "loginemp-manager"),
    "loginemp-manager": ("loginemp-manager", "loginemp-manager"),
    # Update modules
    "update_emp": ("updateemp_mgmt", "updateemp_mgmt"),
    "updateemp_mgmt": ("updateemp_mgmt", "updateemp_mgmt"),
    "update_customer": ("updatecustomer_mgmt", "updatecustomer_mgmt"),
    "updatecustomer_mgmt": ("updatecustomer_mgmt", "updatecustomer_mgmt"),
    "update_po": ("updatepurchase-order", "updatepurchase-order"),
    "updatepurchase-order": ("updatepurchase-order", "updatepurchase-order"),
}


def read_base_url(sheet_name: Optional[str] = None) -> str:
    """
    Dynamically extract Base URL from test data Excel sheets or environment variable.
    Zero hardcoded values.
    """
    env_url = os.environ.get("SWARAJYA_BASE_URL") or os.environ.get("BASE_URL")
    if env_url:
        return env_url.strip()

    if os.path.exists(TEST_DATA_FILE):
        try:
            wb = openpyxl.load_workbook(TEST_DATA_FILE, data_only=True)
            sheets_to_check = [sheet_name] if sheet_name and sheet_name in wb.sheetnames else wb.sheetnames
            for s in sheets_to_check:
                ws = wb[s]
                # Check rows 1 and 2
                for r_idx in range(1, 4):
                    row_vals = [c for c in next(ws.iter_rows(min_row=r_idx, max_row=r_idx, values_only=True))]
                    for c_idx, val in enumerate(row_vals):
                        if val and "base url" in str(val).lower():
                            # Next row or same row next cell
                            val_below = ws.cell(row=r_idx + 1, column=c_idx + 1).value
                            if val_below and str(val_below).startswith("http"):
                                wb.close()
                                return str(val_below).strip()
            wb.close()
        except Exception as e:
            logger.warning("Could not read base URL from test data: %s", e)

    from shared.config.constants import BASE_URL
    return BASE_URL


def read_credentials(role: str = "Admin", sheet_name: Optional[str] = None) -> Dict[str, str]:
    """
    Read credentials dynamically from environment variables, test data sheets,
    or credentials.xlsx with zero hardcoded values.
    """
    # 1. Environment variables override (Production / CI/CD secrets)
    env_user = os.environ.get("SWARAJYA_USER_ID") or os.environ.get(f"SWARAJYA_{role.upper()}_USER_ID")
    env_pass = os.environ.get("SWARAJYA_PASSWORD") or os.environ.get(f"SWARAJYA_{role.upper()}_PASSWORD")
    env_code = os.environ.get("SWARAJYA_AUTH_CODE")
    env_base = os.environ.get("SWARAJYA_BASE_URL") or os.environ.get("BASE_URL")

    if env_user and env_pass:
        return {
            "role": role,
            "employee_id": str(env_user).strip(),
            "user_id": str(env_user).strip(),
            "password": str(env_pass).strip(),
            "auth_code": str(env_code or "").strip(),
            "base_url": str(env_base or read_base_url(sheet_name)).strip(),
        }

    # 2. Check Swarajya-test-data.xlsx
    if os.path.exists(TEST_DATA_FILE):
        try:
            wb = openpyxl.load_workbook(TEST_DATA_FILE, data_only=True)

            # A. If sheet_name is provided, check its row 1 and 2 banner
            if sheet_name and sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                r1 = [str(c).strip().lower() if c is not None else "" for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
                r2 = [c for c in next(ws.iter_rows(min_row=2, max_row=2, values_only=True))]
                emp_id, pwd, code, base_url = None, None, None, None
                for idx, col_h in enumerate(r1):
                    if idx >= len(r2):
                        continue
                    v = r2[idx]
                    if v is None:
                        continue
                    v_str = str(int(v)) if isinstance(v, float) and v.is_integer() else str(v).strip()
                    if "user id" in col_h or "employee_id" in col_h or "user_id" in col_h:
                        emp_id = v_str
                    elif "password" in col_h:
                        pwd = v_str
                    elif "auth code" in col_h or "auth_code" in col_h:
                        code = v_str
                    elif "base url" in col_h:
                        base_url = v_str

                if emp_id and pwd:
                    wb.close()
                    return {
                        "role": role,
                        "employee_id": emp_id,
                        "user_id": emp_id,
                        "password": pwd,
                        "auth_code": code or env_code or "",
                        "base_url": base_url or read_base_url(),
                    }

            # B. Check loginhr_admin and loginemp-manager for role matches
            target_role = role.strip().lower()
            login_sheets = ["loginhr_admin", "loginemp-manager"]
            for sname in login_sheets:
                if sname not in wb.sheetnames:
                    continue
                ws = wb[sname]
                headers = [str(c).strip() if c is not None else "" for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):
                        continue
                    row_dict = dict(zip(headers, row))
                    row_role = str(row_dict.get("Role", "")).strip().lower()
                    if row_role == target_role or (target_role in ("admin", "hr admin") and row_role == "admin"):
                        emp_id = str(row_dict.get("Employee_ID") or "").strip()
                        if emp_id.endswith(".0"):
                            emp_id = emp_id[:-2]
                        pwd = str(row_dict.get("Password") or "").strip()
                        code = str(row_dict.get("Auth_Code") or env_code or "").strip()
                        if code.endswith(".0"):
                            code = code[:-2]
                        base_url = str(row_dict.get("Base URL") or "").strip()
                        wb.close()
                        if emp_id and pwd:
                            return {
                                "role": str(row_dict.get("Role", role)).strip(),
                                "employee_id": emp_id,
                                "user_id": emp_id,
                                "password": pwd,
                                "auth_code": code,
                                "base_url": base_url or read_base_url(),
                            }

            # C. Check any create sheet banner if role is Admin / Default
            for sname in ["createemp-mgmt", "createcustomer-mgmt", "createvendor-mgmt", "createconsultant_mgmt", "createpurchase_order", "createinvoice-mgmt"]:
                if sname in wb.sheetnames:
                    ws = wb[sname]
                    r1 = [str(c).strip().lower() if c is not None else "" for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
                    r2 = [c for c in next(ws.iter_rows(min_row=2, max_row=2, values_only=True))]
                    emp_id, pwd, code, base_url = None, None, None, None
                    for idx, col_h in enumerate(r1):
                        if idx >= len(r2):
                            continue
                        v = r2[idx]
                        if v is None:
                            continue
                        v_str = str(int(v)) if isinstance(v, float) and v.is_integer() else str(v).strip()
                        if "user id" in col_h or "employee_id" in col_h:
                            emp_id = v_str
                        elif "password" in col_h:
                            pwd = v_str
                        elif "auth code" in col_h or "auth_code" in col_h:
                            code = v_str
                        elif "base url" in col_h:
                            base_url = v_str
                    if emp_id and pwd:
                        wb.close()
                        return {
                            "role": role,
                            "employee_id": emp_id,
                            "user_id": emp_id,
                            "password": pwd,
                            "auth_code": code or env_code or "",
                            "base_url": base_url or read_base_url(),
                        }

            wb.close()
        except Exception as e:
            logger.warning("Could not read credentials from test data: %s", e)

    # 3. Check credentials.xlsx if present
    if os.path.exists(CREDENTIALS_FILE):
        try:
            wb = openpyxl.load_workbook(CREDENTIALS_FILE, data_only=True)
            ws = wb["Credentials"] if "Credentials" in wb.sheetnames else wb.active
            headers = [cell.value for cell in ws[1]]
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not any(row):
                    continue
                row_dict = dict(zip(headers, row))
                row_role = str(row_dict.get("Role", "")).strip().lower()
                target_role = role.strip().lower()
                if row_role == target_role or (target_role in ("admin", "manager") and row_role in ("admin", "manager", "employee")):
                    emp_id = str(row_dict.get("Employee_ID") or "").strip()
                    pwd = str(row_dict.get("Password") or "").strip()
                    code = str(row_dict.get("Auth_Code") or env_code or "").strip()
                    base_url = str(row_dict.get("Base URL") or "").strip()
                    wb.close()
                    if emp_id and pwd:
                        return {
                            "role": str(row_dict.get("Role", role)).strip(),
                            "employee_id": emp_id,
                            "user_id": emp_id,
                            "password": pwd,
                            "auth_code": code,
                            "base_url": base_url or read_base_url(),
                        }
            wb.close()
        except Exception as e:
            logger.warning("Could not read credentials.xlsx: %s", e)

    raise ValueError(
        f"Credentials for role '{role}' could not be resolved from {TEST_DATA_FILE} or environment variables."
    )


def read_data_sheet(sheet_name: str) -> Dict[str, Dict[str, Any]]:
    """
    Read input test data from Swarajya-test-data.xlsx for the specified sheet.
    Dynamically discovers the header row (containing 'Test Case ID' or 'TC ID' or 'Role')
    and extracts test data rows mapped by Test Case ID.
    Returns mapping: {tc_id: {column_name: value}}
    """
    if not os.path.exists(TEST_DATA_FILE):
        logger.warning("TEST_DATA_FILE not found: %s", TEST_DATA_FILE)
        return {}

    wb = openpyxl.load_workbook(TEST_DATA_FILE, data_only=True)
    if sheet_name not in wb.sheetnames:
        wb.close()
        logger.warning("Sheet '%s' not found in %s. Available: %s", sheet_name, TEST_DATA_FILE, wb.sheetnames)
        return {}

    ws = wb[sheet_name]

    # Dynamically find header row
    header_row_idx = None
    headers = []
    for r_idx in range(1, 15):
        row_cells = [c for c in next(ws.iter_rows(min_row=r_idx, max_row=r_idx, values_only=True))]
        str_cells = [str(c).strip().lower() if c is not None else "" for c in row_cells]
        if any(k in str_cells for k in ["test case id", "tc id", "test case", "role"]) or any("test case" in c for c in str_cells):
            header_row_idx = r_idx
            headers = [str(c).strip() if c is not None else f"col_{i}" for i, c in enumerate(row_cells)]
            break

    if header_row_idx is None:
        wb.close()
        logger.warning("Could not find header row in sheet '%s'", sheet_name)
        return {}

    data_map = {}
    for row in ws.iter_rows(min_row=header_row_idx + 1, values_only=True):
        if not any(row):
            continue
        row_dict = {}
        for h, val in zip(headers, row):
            if not h:
                continue
            if val is not None and str(val).strip() != "" and str(val).strip().lower() != "none":
                if isinstance(val, float) and val.is_integer():
                    str_val = str(int(val))
                elif isinstance(val, datetime):
                    str_val = val.strftime("%Y-%m-%d")
                else:
                    str_val = str(val).strip()
            else:
                str_val = ""
            if h.startswith("col_") and not str_val:
                continue
            row_dict[h] = str_val
            clean_h = h.rstrip(" *").strip()
            if clean_h != h and clean_h not in row_dict:
                row_dict[clean_h] = str_val

        tc_id = str(row_dict.get("Test Case ID", "")).strip()
        if tc_id:
            data_map[tc_id] = row_dict

    wb.close()
    return data_map


def load_cases_and_data(
    module_key: str,
    filter_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Loads test cases from Swarajya-test-cases.xlsx and merges corresponding input
    data from Swarajya-test-data.xlsx.
    
    filter_type can be:
      - 'Positive_Tests' / 'Positive_Flows' / 'POS': returns only positive test cases
      - 'Negative_Tests' / 'Negative_Flows' / 'NEG': returns only negative test cases
      - None: returns all active test cases
    """
    if not os.path.exists(TEST_CASES_FILE):
        raise FileNotFoundError(f"Test cases workbook not found at: {TEST_CASES_FILE}")

    # Determine sheet names
    cases_sheet, data_sheet = MODULE_SHEET_MAP.get(
        module_key.lower().strip(),
        (module_key, module_key),
    )

    wb = openpyxl.load_workbook(TEST_CASES_FILE, data_only=True)
    if cases_sheet not in wb.sheetnames:
        wb.close()
        raise ValueError(f"Sheet '{cases_sheet}' not found in {TEST_CASES_FILE}. Available: {wb.sheetnames}")

    ws = wb[cases_sheet]
    headers = [str(cell.value).strip() for cell in ws[1] if cell.value is not None]

    # Load separate test data mapping
    data_map = read_data_sheet(data_sheet)

    test_cases = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue
        row_dict = dict(zip(headers, row))
        tc_id = str(row_dict.get("Test Case ID", "")).strip()
        if not tc_id:
            continue

        # Attach raw and parsed data from separate data sheet
        tc_data = data_map.get(tc_id, {})
        row_dict["Test Data"] = tc_data
        row_dict["data"] = tc_data
        row_dict["_sheet"] = cases_sheet

        # Normalize common step and scenario keys
        if "Test Steps" in row_dict and "Steps" not in row_dict:
            row_dict["Steps"] = row_dict["Test Steps"]
        if "Test Scenario" in row_dict and "Scenario" not in row_dict:
            row_dict["Scenario"] = row_dict["Test Scenario"]

        # Filter POS vs NEG if requested
        if filter_type:
            ft_upper = str(filter_type).upper()
            tc_upper = tc_id.upper()
            if "POS" in ft_upper:
                if "POS" not in tc_upper:
                    continue
            elif "NEG" in ft_upper:
                if "NEG" not in tc_upper:
                    continue

        test_cases.append(row_dict)

    wb.close()
    logger.info(
        "Loaded %d test cases for module '%s' (filter=%s)",
        len(test_cases),
        module_key,
        filter_type,
    )
    return test_cases


def build_automation_id(tc_id: str) -> str:
    """Generate automation script ID from test case ID (e.g. TC_POS_01 -> AUT_POS_01)."""
    clean_id = str(tc_id).strip().replace("-", "_")
    if not clean_id.startswith("AUT_"):
        if clean_id.startswith("TC_"):
            clean_id = "AUT_" + clean_id[3:]
        elif clean_id.startswith("TC"):
            clean_id = "AUT_" + clean_id[2:].lstrip("_")
        else:
            clean_id = "AUT_" + clean_id
    return clean_id


def update_test_result(
    tc_id: str,
    status: str,
    remarks: Optional[str] = None,
    sheet_name: Optional[str] = None,
) -> bool:
    """
    Update Test Status, Automation Status, Auto Script ID, and Remarks in Swarajya-test-cases.xlsx.
    Includes retry logic to safely handle open file locks.
    """
    if not os.path.exists(TEST_CASES_FILE):
        return False

    auto_id = build_automation_id(tc_id)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_remarks = f"{timestamp} | {remarks}" if remarks else timestamp

    for attempt in range(5):
        try:
            wb = openpyxl.load_workbook(TEST_CASES_FILE)
            sheets_to_search = [sheet_name] if sheet_name and sheet_name in wb.sheetnames else wb.sheetnames

            found = False
            for sname in sheets_to_search:
                ws = wb[sname]
                headers = [str(cell.value).strip() if cell.value is not None else "" for cell in ws[1]]

                if "Test Case ID" not in headers:
                    continue
                tc_col = headers.index("Test Case ID") + 1

                def get_or_create_col(col_name: str) -> int:
                    # Check exact or partial match
                    for idx, h in enumerate(headers):
                        if h.lower() == col_name.lower():
                            return idx + 1
                    col_num = len(headers) + 1
                    ws.cell(row=1, column=col_num, value=col_name)
                    headers.append(col_name)
                    return col_num

                status_col = get_or_create_col("Test Status")
                auto_status_col = get_or_create_col("Automation Status")
                
                # Check for Remarks or Remarks / Defect Observed
                remarks_header = "Remarks / Defect Observed" if "Remarks / Defect Observed" in headers else "Remarks"
                remarks_col = get_or_create_col(remarks_header)

                for row_idx in range(2, ws.max_row + 1):
                    cell_val = ws.cell(row=row_idx, column=tc_col).value
                    if cell_val and str(cell_val).strip() == tc_id.strip():
                        ws.cell(row=row_idx, column=status_col, value=status)
                        ws.cell(row=row_idx, column=auto_status_col, value="Automated")
                        ws.cell(row=row_idx, column=remarks_col, value=full_remarks)
                        found = True
                        break

                if found:
                    break

            if found:
                wb.save(TEST_CASES_FILE)
                wb.close()
                logger.info("Updated Excel %s in %s: Status=%s", tc_id, os.path.basename(TEST_CASES_FILE), status)
                return True
            wb.close()
            return False
        except PermissionError:
            time.sleep(0.5)
        except Exception as exc:
            logger.error("Failed to update test result for %s: %s", tc_id, exc)
            return False

    return False


# Backward compatibility alias
load_test_data_sheet = read_data_sheet

