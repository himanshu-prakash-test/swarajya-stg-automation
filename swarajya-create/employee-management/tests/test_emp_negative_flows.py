"""
Data-driven negative flow tests for Employee Management (Create Module).
Loads test definitions and data dynamically from Swarajya-test-cases/data workbooks.
"""

import os
import sys
import pytest

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_TEST_DIR)
_ROOT_DIR = os.path.dirname(os.path.dirname(_MODULE_DIR))

for _p in (_MODULE_DIR, _ROOT_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from emp_pages.form_executor import FormExecutor
from emp_utils.excel_reader import is_ui_case, read_test_cases

NEG_TEST_CASES = [tc for tc in read_test_cases("Negative_Flows") if is_ui_case(tc)]
NEG_IDS = [tc["Test Case ID"] for tc in NEG_TEST_CASES]


@pytest.mark.negative
@pytest.mark.employee
class TestNegativeFlows:
    """Data-driven negative flow tests from Excel workbooks."""

    @pytest.mark.parametrize("test_case", NEG_TEST_CASES, ids=NEG_IDS)
    def test_negative_scenario(self, authenticated_page, test_case):
        executor = FormExecutor(authenticated_page)
        executor.execute_test_case(test_case, is_positive=False)


if __name__ == "__main__":
    config_file = os.path.join(_ROOT_DIR, "pytest.ini")
    pytest_args = [__file__, "-c", config_file, "-o", f"rootdir={_ROOT_DIR}", "-v", "-s"]
    extra_args = sys.argv[1:]
    if not any(arg in extra_args for arg in ("--headed", "--headless")):
        pytest_args.append("--headed")
    pytest_args.extend(extra_args)
    sys.exit(pytest.main(pytest_args))
