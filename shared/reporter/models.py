"""
Data models for the Playwright HTML Reporter.
Defines data structures representing individual test executions and overall test session metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class TestCaseResult:
    """Represents the execution outcome of a single test case."""
    nodeid: str
    name: str
    tc_id: str
    status: str  # "PASS", "FAIL", "SKIPPED"
    duration: float  # in seconds
    module_name: str
    class_name: str = ""
    description: str = ""
    error_message: str = ""
    stacktrace: str = ""
    screenshot_path: Optional[str] = None
    screenshot_base64: Optional[str] = None
    remarks: str = ""
    auto_id: str = ""
    markers: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @property
    def formatted_duration(self) -> str:
        """Returns readable duration string."""
        if self.duration < 1:
            return f"{int(self.duration * 1000)}ms"
        return f"{self.duration:.2f}s"

    @property
    def status_css_class(self) -> str:
        s = self.status.upper()
        if "PASS" in s:
            return "status-pass"
        if "FAIL" in s:
            return "status-fail"
        return "status-skip"


@dataclass
class SessionSummary:
    """Represents aggregated metrics for an entire test suite execution."""
    suite_title: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0
    start_time: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    end_time: str = ""
    environment_info: Dict[str, str] = field(default_factory=dict)
    test_results: List[TestCaseResult] = field(default_factory=list)

    @property
    def pass_percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.passed / self.total) * 100, 1)

    @property
    def fail_percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.failed / self.total) * 100, 1)

    @property
    def skip_percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.skipped / self.total) * 100, 1)

    @property
    def formatted_duration(self) -> str:
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{self.duration:.2f}s"

    @property
    def overall_status(self) -> str:
        if self.failed > 0:
            return f"{self.failed} FAILED"
        if self.passed > 0 and self.failed == 0:
            return "ALL PASSED"
        return "COMPLETED"
