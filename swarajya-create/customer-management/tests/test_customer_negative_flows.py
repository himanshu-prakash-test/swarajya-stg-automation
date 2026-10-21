import pytest
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
    """Data-driven negative flow tests from Create-Customer-Management.xlsx."""

    if not NEG_TEST_CASES:
        def test_no_input_validation_negative_flows(self):
            """Input validation test cases are excluded per policy (values entered by adult users)."""
            pytest.skip("Input validation test cases are excluded for Customer Management (values entered by adult users).")
    else:
        @pytest.mark.parametrize("test_case", NEG_TEST_CASES, ids=NEG_IDS)
        def test_negative_scenario(self, authenticated_page, test_case):
            executor = FormExecutor(authenticated_page)
            executor.execute_test_case(test_case, is_positive=False)

