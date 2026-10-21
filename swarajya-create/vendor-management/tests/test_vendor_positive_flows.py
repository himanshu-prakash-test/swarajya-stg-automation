"""
Data-driven positive flow tests for Vendor Management (Create Module).
Loads test definitions and data dynamically from Swarajya-test-cases/data workbooks.
Zero hardcoding.
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

from vendor_pages.form_executor import FormExecutor
from vendor_utils.excel_reader import read_test_cases, is_ui_case

POS_TEST_CASES = [tc for tc in read_test_cases("Positive_Tests") if is_ui_case(tc)]
POS_IDS = [tc["Test Case ID"] for tc in POS_TEST_CASES]


@pytest.mark.positive
@pytest.mark.vendor
class TestPositiveFlows:
    """Data-driven positive flow tests from Swarajya-test-cases.xlsx."""

    @pytest.mark.parametrize("test_case", POS_TEST_CASES, ids=POS_IDS)
    def test_positive_scenario(self, authenticated_page, test_case):
        executor = FormExecutor(authenticated_page)
        executor.execute_test_case(test_case, is_positive=True)
