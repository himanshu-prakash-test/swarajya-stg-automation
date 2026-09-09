"""
Playwright HTML Reporter Engine.
Collects test execution metrics, resolves screenshot evidence,
and compiles self-contained interactive HTML dashboards.
"""

import base64
import os
import platform
import shutil
import sys
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional

import jinja2

from .models import SessionSummary, TestCaseResult
from .template import REPORT_HTML_TEMPLATE


def _find_workspace_root() -> str:
    """Find the root directory of the automation repository."""
    curr = os.path.dirname(os.path.abspath(__file__))
    while curr:
        if os.path.exists(os.path.join(curr, "pytest.ini")) or os.path.exists(os.path.join(curr, ".git")):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


WORKSPACE_ROOT = _find_workspace_root()
DEFAULT_REPORTS_DIR = os.path.join(WORKSPACE_ROOT, "reports")


def _get_playwright_version() -> str:
    try:
        import playwright
        return getattr(playwright, "__version__", "1.62.0")
    except Exception:
        return "1.62.0"


def _get_pytest_version() -> str:
    try:
        import pytest
        return getattr(pytest, "__version__", "9.x")
    except Exception:
        return "9.x"


def _encode_image_to_base64(image_path: str) -> Optional[str]:
    """Convert an image file to a base64 data URI for standalone portability."""
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        # Check size - only encode if reasonable (< 5MB)
        if os.path.getsize(image_path) > 5 * 1024 * 1024:
            return None
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(image_path)[1].lower().replace(".", "")
            mime = "image/png" if ext == "png" else f"image/{ext}"
            return f"data:{mime};base64,{encoded}"
    except Exception:
        return None
def _get_coreco_logo_base64() -> str:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "coreco_logo.png")
    return _encode_image_to_base64(logo_path) or ""

class PlaywrightHTMLReporter:
    """
    Orchestrates the generation of comprehensive Playwright HTML test reports.
    """

    def __init__(self, suite_title: str = "Swarajya Staging Automation", output_dir: Optional[str] = None):
        self.suite_title = suite_title
        self.output_dir = output_dir or DEFAULT_REPORTS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        self.start_time = datetime.now()
        self.results: List[TestCaseResult] = []
        self.environment_info: Dict[str, str] = {
            "playwright_version": _get_playwright_version(),
            "pytest_version": _get_pytest_version(),
            "python_version": platform.python_version(),
            "os": f"{platform.system()} {platform.release()}",
            "browser": "Chromium",
            "mode": "Headless (1920x1080)" if os.environ.get("HEADED") != "1" else "Headed (1920x1080)",
            "base_url": "https://swarajya-stg.corecotechnologies.com/",
        }

    def set_environment(self, **kwargs):
        """Update or add environment details."""
        self.environment_info.update(kwargs)

    def add_result(self, result: TestCaseResult):
        """Record a test outcome."""
        # Automatically encode screenshot if available and not already encoded
        if result.screenshot_path and not result.screenshot_base64:
            result.screenshot_base64 = _encode_image_to_base64(result.screenshot_path)
        self.results.append(result)

    def compile_summary(self) -> SessionSummary:
        """Aggregate test execution metrics."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        passed = sum(1 for r in self.results if "PASS" in r.status.upper())
        failed = sum(1 for r in self.results if "FAIL" in r.status.upper())
        skipped = sum(1 for r in self.results if "SKIP" in r.status.upper())
        total = len(self.results)

        return SessionSummary(
            suite_title=self.suite_title,
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            start_time=self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            environment_info=self.environment_info,
            test_results=self.results,
        )

    def generate_report(self, filename_prefix: Optional[str] = None) -> str:
        """
        Renders the interactive HTML report and writes it to disk.
        Returns the absolute path of the generated report.
        """
        summary = self.compile_summary()

        # Compute per-module statistics
        module_map: Dict[str, Dict[str, int]] = {}
        for r in self.results:
            mod = r.module_name or "General"
            if mod not in module_map:
                module_map[mod] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
            module_map[mod]["total"] += 1
            if "PASS" in r.status.upper():
                module_map[mod]["passed"] += 1
            elif "FAIL" in r.status.upper():
                module_map[mod]["failed"] += 1
            else:
                module_map[mod]["skipped"] += 1

        module_stats = []
        for mod_name, counts in module_map.items():
            tot = counts["total"]
            p = round((counts["passed"] / tot) * 100, 1) if tot else 0.0
            f = round((counts["failed"] / tot) * 100, 1) if tot else 0.0
            s = round((counts["skipped"] / tot) * 100, 1) if tot else 0.0
            module_stats.append({
                "name": mod_name,
                "total": tot,
                "passed": counts["passed"],
                "failed": counts["failed"],
                "skipped": counts["skipped"],
                "pass_pct": p,
                "fail_pct": f,
                "skip_pct": s,
            })

        modules_list = sorted(list(module_map.keys()))

        # Render Jinja2 template
        template = jinja2.Template(REPORT_HTML_TEMPLATE)
        html_content = template.render(
            summary=summary,
            module_stats=module_stats,
            modules=modules_list,
            coreco_logo_base64=_get_coreco_logo_base64(),
        )

        # Write to single, clean latest_report.html
        report_path = os.path.join(self.output_dir, "latest_report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return report_path

    @staticmethod
    def open_in_browser(report_path: str):
        """Open the generated report in the system default web browser."""
        try:
            abs_path = os.path.abspath(report_path)
            webbrowser.open(f"file://{abs_path}")
        except Exception as exc:
            print(f"[REPORTER] Could not open browser: {exc}")
