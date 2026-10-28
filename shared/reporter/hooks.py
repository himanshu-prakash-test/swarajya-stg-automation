"""
Pytest integration hooks and helpers for Playwright HTML Reporter.
Connects pytest test lifecycle events to the HTML reporting engine.
"""

import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from .html_reporter import PlaywrightHTMLReporter
from .models import TestCaseResult


def _extract_tc_id(item) -> str:
    """Extract Excel Test Case ID from markers, params, or function name."""
    # 1. From @pytest.mark.tc_id("...")
    marker = item.get_closest_marker("tc_id")
    if marker and marker.args:
        return str(marker.args[0])

    # 2. From parameterized callspec
    if hasattr(item, "callspec"):
        for param_val in item.callspec.params.values():
            if isinstance(param_val, dict) and "Test Case ID" in param_val:
                return str(param_val["Test Case ID"])

    # 3. From test name regex
    match = re.search(r"(TC[-_][A-Za-z0-9\-_]+)", item.name, re.IGNORECASE)
    if match:
        return match.group(1).upper().replace("_", "-")

    return "UNKNOWN"


def _extract_module_name(nodeid: str) -> str:
    """Determine friendly module name from nodeid path."""
    n = nodeid.lower()
    if "invoice-report" in n or "invoice_report" in n:
        return "Invoice Report"
    if "employee-management" in n:
        return "Employee Management"
    if "vendor-management" in n:
        return "Vendor Management"
    if "consultant-management" in n:
        return "Consultant Management"
    if "customer-management" in n:
        return "Customer Management"
    if "swarajya-login" in n or "login" in n:
        return "Login Authentication"
    if "emp_mgmt" in n or "update" in n:
        return "Update Employee"
    return "Core Automation"


def _clean_failure_details(report) -> tuple[str, str]:
    """Extract clean error message and formatted stacktrace."""
    if not report.failed or not report.longrepr:
        return "", ""

    longrepr_str = str(report.longrepr)
    error_msg = "Test Assertion / Execution Failure"

    for line in reversed(longrepr_str.splitlines()):
        line = line.strip()
        if not line:
            continue
        if "AssertionError:" in line:
            error_msg = line.split("AssertionError:", 1)[1].strip()
            break
        if line.startswith("E "):
            error_msg = line[2:].strip()
            break

    return error_msg, longrepr_str


class PytestReporterPlugin:
    """
    Manages session-level test collection and HTML report generation.
    """

    def __init__(self, suite_title: str = "Swarajya Staging Automation"):
        self.reporter = PlaywrightHTMLReporter(suite_title=suite_title)
        self.recorded_nodeids = set()

    def record_test(
        self,
        item,
        report,
        status: str,
        remarks: str = "",
        auto_id: str = "",
        screenshot_path: Optional[str] = None,
        duration: Optional[float] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        stdout: Optional[str] = None,
    ):
        """Record a test execution from a pytest hook."""
        if report.nodeid in self.recorded_nodeids:
            return
        self.recorded_nodeids.add(report.nodeid)

        tc_id = _extract_tc_id(item)
        module_name = _extract_module_name(report.nodeid)
        error_msg, stacktrace = _clean_failure_details(report)

        # Extract markers
        markers = [
            m.name for m in item.iter_markers()
            if m.name not in ("tc_id", "parametrize", "usefixtures")
        ]

        # Extract docstring if present and not provided
        if not description:
            description = item.obj.__doc__.strip() if getattr(item, "obj", None) and item.obj.__doc__ else ""

        # Extract parameters if not provided
        if parameters is None and hasattr(item, "callspec"):
            parameters = {}
            for k, v in item.callspec.params.items():
                if isinstance(v, dict):
                    for subk, subv in v.items():
                        if subv is not None and str(subv).strip() != "":
                            parameters[str(subk)] = str(subv)
                else:
                    parameters[str(k)] = str(v)

        # Extract captured stdout / logs if not provided
        if stdout is None and hasattr(report, "sections"):
            sec_lines = []
            for sec_name, sec_content in report.sections:
                if sec_content and sec_content.strip():
                    sec_lines.append(f"[{sec_name}]\n{sec_content.strip()}")
            stdout = "\n\n".join(sec_lines) if sec_lines else ""

        # Test duration
        dur = duration if duration is not None else getattr(report, "duration", 0.0)

        result = TestCaseResult(
            nodeid=report.nodeid,
            name=item.name,
            tc_id=tc_id,
            status=status,
            duration=dur,
            module_name=module_name,
            description=description or "",
            error_message=error_msg,
            stacktrace=stacktrace,
            screenshot_path=screenshot_path,
            remarks=remarks,
            auto_id=auto_id,
            markers=markers,
            parameters=parameters or {},
            stdout=stdout or "",
        )
        self.reporter.add_result(result)

    def finalize_report(self, filename_prefix: Optional[str] = None) -> str:
        """Generate report on session finish and print status."""
        report_path = self.reporter.generate_report(filename_prefix=filename_prefix)
        try:
            print(f"\n{'=' * 65}")
            print(f"  📊 PLAYWRIGHT HTML REPORT GENERATED SUCCESSFULLY")
            print(f"  File: {report_path}")
            print(f"{'=' * 65}\n")
        except Exception:
            print(f"\n{'=' * 65}\n  PLAYWRIGHT HTML REPORT GENERATED SUCCESSFULLY\n  File: {report_path}\n{'=' * 65}\n")
        return report_path
