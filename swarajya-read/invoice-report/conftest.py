"""
Pytest configuration and fixtures for Invoice Report API Automation.

Strictly adheres to framework standards:
- Dynamic test data and test case loading from shared Excel workbooks:
  * Swarajya-test-cases.xlsx [Sheet: readinvoice-reports]
  * Swarajya-test-data.xlsx  [Sheet: readinvoice-report]
- Automatic token resolution from session or dynamic login
- Bi-directional test result updates to Excel workbooks with PASS/FAIL styling
- Full assertion validation and execution tracking
"""

import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import pytest

# Ensure module root, read root, and workspace root are in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
READ_DIR = os.path.dirname(MODULE_DIR)
WORKSPACE_ROOT = os.path.dirname(READ_DIR)
for p in (MODULE_DIR, READ_DIR, WORKSPACE_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from shared.utils.logger import get_logger
from shared.reporter import PytestReporterPlugin
from shared.utils.popup import show_summary_popup
from invoice_report_utils.excel_reader import (
    get_base_url as _get_base_url,
    read_api_credentials,
    load_invoice_report_test_cases,
    load_invoice_report_test_data,
    get_test_case_by_id,
    get_test_data_by_id,
    get_merged_test_suite,
    update_test_result,
    build_automation_id,
    CASES_SHEET,
    DATA_SHEET,
)
from invoice_report_api.api_client import InvoiceReportApiClient
from invoice_report_api.auth import get_auth_token

log = get_logger("InvoiceReportConftest")

_start_time = datetime.now()

# Results accumulator for session report
_RESULTS_ACCUMULATOR: Dict[str, Dict[str, Any]] = {}
_html_reporter = PytestReporterPlugin(suite_title="Invoice Report API Automation")
_html_reporter.reporter.set_environment(browser="API Client (REST/HTTP)", mode="Automated API Tests")


def pytest_addoption(parser):
    """Register custom CLI options for API test execution."""
    existing = set()
    for grp in getattr(parser, "_groups", []):
        for opt in getattr(grp, "options", []):
            existing.update(getattr(opt, "_short_opts", []))
            existing.update(getattr(opt, "_long_opts", []))
    for opt in getattr(getattr(parser, "_anonymous", None), "options", []):
        existing.update(getattr(opt, "_short_opts", []))
        existing.update(getattr(opt, "_long_opts", []))

    if "--api-url" not in existing:
        try:
            parser.addoption(
                "--api-url",
                action="store",
                default=None,
                help="Base URL for invoice report API endpoints (overrides Excel).",
            )
        except ValueError:
            pass
    if "--bearer-token" not in existing:
        try:
            parser.addoption(
                "--bearer-token",
                action="store",
                default=None,
                help="Custom Bearer token for API authentication.",
            )
        except ValueError:
            pass
    if "--popup" not in existing:
        try:
            parser.addoption(
                "--popup",
                action="store_true",
                default=False,
                help="Force display desktop summary popup even in CI.",
            )
        except ValueError:
            pass
    if "--headed" not in existing:
        try:
            parser.addoption(
                "--headed",
                action="store_true",
                default=False,
                help="Run browser in headed mode.",
            )
        except ValueError:
            pass
    if "--headless" not in existing:
        try:
            parser.addoption(
                "--headless",
                action="store_true",
                default=False,
                help="Run browser headless.",
            )
        except ValueError:
            pass
    if "--slowmo" not in existing:
        try:
            parser.addoption(
                "--slowmo",
                action="store",
                default=0,
                type=int,
                help="Slowdown Playwright actions (ms).",
            )
        except ValueError:
            pass


@pytest.fixture(scope="session")
def base_url(request) -> str:
    """Provide target base URL dynamically resolved from Excel or CLI option."""
    cli_url = request.config.getoption("--api-url", default=None)
    if cli_url:
        return cli_url.rstrip("/")
    return _get_base_url()


@pytest.fixture(scope="session")
def auth_token(request) -> str:
    """Provide active JWT Bearer token dynamically."""
    cli_token = request.config.getoption("--bearer-token", default=None)
    if cli_token:
        return cli_token.strip()
    return get_auth_token()


@pytest.fixture(scope="session")
def api_client(base_url: str, auth_token: str) -> InvoiceReportApiClient:
    """Session-scoped initialized API client."""
    client = InvoiceReportApiClient(base_url=base_url, token=auth_token)
    log.info(f"Initialized InvoiceReportApiClient -> Base: {base_url}")
    return client


@pytest.fixture(scope="session")
def test_cases_list() -> List[Dict[str, Any]]:
    """Return all test case definitions from Excel."""
    return load_invoice_report_test_cases()


@pytest.fixture(scope="session")
def test_data_list() -> List[Dict[str, Any]]:
    """Return all test data rows from Excel."""
    return load_invoice_report_test_data()


@pytest.fixture(scope="session")
def merged_suite() -> List[Dict[str, Any]]:
    """Return merged test case + test data records."""
    return get_merged_test_suite()


# ── Pytest Hooks for Excel Result Reporting ────────────────────────

def _extract_tc_id_from_item(item) -> Optional[str]:
    """Extract Test Case ID from markers or function name."""
    # Check tc_id marker
    tc_marker = item.get_closest_marker("tc_id")
    if tc_marker and tc_marker.args:
        return str(tc_marker.args[0]).strip()

    # Match in function name, e.g. test_tc_rep_pos_01_...
    match = re.search(r"TC[-_]REP[-_](?:POS|NEG)[-_]\d+", item.name, re.IGNORECASE)
    if match:
        raw_id = match.group(0).upper().replace("_", "-")
        return raw_id

    # Check parameterized argument
    if hasattr(item, "callspec") and "test_data" in item.callspec.params:
        data_arg = item.callspec.params["test_data"]
        if isinstance(data_arg, dict) and "Test Case ID" in data_arg:
            return data_arg["Test Case ID"]

    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Inspect test execution result and bi-directionally update Excel sheets.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" or (report.when == "setup" and report.failed):
        tc_id = _extract_tc_id_from_item(item)
        item_key = tc_id or item.name

        status = "PASS" if report.passed else ("FAIL" if report.failed else "SKIPPED")
        remarks = ""

        if report.failed:
            # Capture failure traceback summary
            err_msg = str(report.longrepr) if hasattr(report, "longrepr") else "Test failed"
            err_first_line = err_msg.strip().split("\n")[-1] if err_msg else "AssertionError"
            remarks = f"Failed: {err_first_line[:200]}"
        elif report.passed:
            remarks = "API assertion passed successfully"

        auto_id = build_automation_id(tc_id) if tc_id else f"AUT_{item.name}"
        _RESULTS_ACCUMULATOR[item_key] = {
            "status": status,
            "remarks": remarks,
            "auto_id": auto_id,
            "duration": getattr(report, "duration", 0.0),
        }

        # Update both Swarajya-test-cases.xlsx and Swarajya-test-data.xlsx if tc_id is present
        if tc_id:
            try:
                update_test_result(
                    tc_id=tc_id,
                    status=status,
                    remarks=remarks,
                    auto_id=auto_id,
                )
            except Exception as e:
                log.warning(f"Could not write result for {tc_id} to Excel: {e}")

        # Enrich with Excel test case and test data specifications
        excel_case = get_test_case_by_id(tc_id) if tc_id else None
        excel_data = get_test_data_by_id(tc_id) if tc_id else None

        desc_parts = []
        if excel_case:
            if excel_case.get("Scenario"):
                desc_parts.append(f"📌 Scenario: {excel_case['Scenario']}")
            if excel_case.get("Pre-condition"):
                desc_parts.append(f"🔹 Pre-condition: {excel_case['Pre-condition']}")
            if excel_case.get("Test Steps"):
                desc_parts.append(f"📝 Test Steps:\n{excel_case['Test Steps']}")
            if excel_case.get("Expected Result"):
                desc_parts.append(f"🎯 Expected Result:\n{excel_case['Expected Result']}")
        elif getattr(item, "obj", None) and item.obj.__doc__:
            desc_parts.append(item.obj.__doc__.strip())

        full_description = "\n\n".join(desc_parts)

        param_dict = {}
        if excel_data:
            if excel_data.get("Method"):
                param_dict["HTTP Method"] = excel_data["Method"]
            if excel_data.get("Endpoint"):
                param_dict["Endpoint / Resource"] = excel_data["Endpoint"]
            if excel_data.get("Expected Status"):
                param_dict["Expected Status"] = str(excel_data["Expected Status"])
            if excel_data.get("Headers"):
                param_dict["Headers"] = excel_data["Headers"]
            if excel_data.get("Expected Payload"):
                param_dict["Expected Payload"] = str(excel_data["Expected Payload"])
            if excel_data.get("Assertions"):
                param_dict["Expected Assertions"] = excel_data["Assertions"]
        elif hasattr(item, "callspec"):
            for k, v in item.callspec.params.items():
                if isinstance(v, dict):
                    for subk, subv in v.items():
                        if subv is not None and str(subv).strip() != "":
                            param_dict[str(subk)] = str(subv)
                else:
                    param_dict[str(k)] = str(v)

        # Captured stdout / logs from pytest sections
        stdout_parts = []
        if hasattr(report, "sections"):
            for sec_name, sec_content in report.sections:
                if sec_content and sec_content.strip():
                    stdout_parts.append(f"[{sec_name}]\n{sec_content.strip()}")
        captured_logs = "\n\n".join(stdout_parts)

        # Record test into standardized Swarajya Playwright HTML report
        try:
            _html_reporter.record_test(
                item=item,
                report=report,
                status=status,
                remarks=remarks,
                auto_id=auto_id,
                screenshot_path=None,
                duration=getattr(report, "duration", 0.0),
                description=full_description,
                parameters=param_dict,
                stdout=captured_logs,
            )
        except Exception as exc:
            log.warning(f"HTML reporter could not record {item.name}: {exc}")


def pytest_sessionfinish(session, exitstatus):
    """Print clean execution summary at the end of the test run and display popup."""
    if getattr(session.config.option, "collectonly", False):
        return

    duration = datetime.now() - _start_time if _start_time else None
    dur_str = str(duration).split(".")[0] if duration else "0:00:00"

    total = len(_RESULTS_ACCUMULATOR)
    passed = sum(1 for r in _RESULTS_ACCUMULATOR.values() if r["status"] == "PASS")
    failed = sum(1 for r in _RESULTS_ACCUMULATOR.values() if r["status"] == "FAIL")
    skipped = sum(1 for r in _RESULTS_ACCUMULATOR.values() if r["status"] == "SKIPPED")

    failed_cases = [f"{tc}: {r.get('remarks', '')}" for tc, r in _RESULTS_ACCUMULATOR.items() if r["status"] == "FAIL"]

    log.info("=" * 60)
    log.info("INVOICE REPORT API AUTOMATION TEST SUITE SUMMARY")
    log.info(f"Total Cases Executed : {total}")
    log.info(f"Passed               : {passed}")
    log.info(f"Failed               : {failed}")
    log.info(f"Skipped              : {skipped}")
    log.info(f"Duration             : {dur_str}")
    log.info(f"Cases Sheet Updated  : {CASES_SHEET}")
    log.info(f"Data Sheet Updated   : {DATA_SHEET}")
    log.info("=" * 60)

    # Honor CLI --popup flag to force popup
    if session.config.getoption("--popup", default=False):
        os.environ["FORCE_POPUP"] = "1"

    report_path = None
    try:
        report_path = _html_reporter.finalize_report(filename_prefix="read_invoice_report")
    except Exception as exc:
        log.warning(f"Could not finalize HTML report: {exc}")

    if not report_path or not os.path.exists(report_path):
        report_path = getattr(session.config.option, "htmlpath", None)
        if not report_path:
            default_report = os.path.join(WORKSPACE_ROOT, "reports", "read_invoice_report.html")
            if os.path.exists(default_report):
                report_path = default_report

    try:
        show_summary_popup(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration_str=str(dur_str),
            failed_tests=failed_cases,
            suite_title="Invoice Report API Automation",
            report_path=str(report_path) if report_path else None,
        )
    except Exception as exc:
        log.warning(f"Could not display summary popup: {exc}")
