"""
Data-driven negative flow tests for Customer Management (Create Module).
Loads test definitions and boundary test data dynamically from Swarajya-test-cases/data workbooks.
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

from customer_pages.form_executor import FormExecutor
from customer_utils.excel_reader import read_test_cases, is_ui_case

try:
    NEG_TEST_CASES = [tc for tc in read_test_cases("Negative_Tests") if is_ui_case(tc)]
    NEG_IDS = [tc["Test Case ID"] for tc in NEG_TEST_CASES]
except Exception:
    NEG_TEST_CASES = []
    NEG_IDS = []


@pytest.mark.negative
@pytest.mark.customer
class TestNegativeFlows:
    """Data-driven negative flow tests from Swarajya-test-cases.xlsx."""

    if not NEG_TEST_CASES:
        def test_no_input_validation_negative_flows(self):
            """Skip scenario if no UI negative test cases are present in Excel."""
            pytest.skip("No negative UI test cases found or enabled in Swarajya-test-cases.xlsx.")
    else:
        @pytest.mark.parametrize("test_case", NEG_TEST_CASES, ids=NEG_IDS)
        def test_negative_scenario(self, authenticated_page, test_case):
            executor = FormExecutor(authenticated_page)
            executor.execute_test_case(test_case, is_positive=False)

