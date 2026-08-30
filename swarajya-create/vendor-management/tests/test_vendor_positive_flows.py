import pytest
from vendor_pages.form_executor import FormExecutor
from vendor_utils.excel_reader import read_test_cases, is_ui_case

try:
    POS_TEST_CASES = [tc for tc in read_test_cases("Positive_Tests") if is_ui_case(tc)]
    POS_IDS = [tc["Test Case ID"] for tc in POS_TEST_CASES]
except Exception as e:
    POS_TEST_CASES = []
    POS_IDS = []


@pytest.mark.positive
@pytest.mark.vendor
class TestPositiveFlows:
    """Data-driven positive flow tests from Create-Vendor-Management.xlsx."""

    @pytest.mark.parametrize("test_case", POS_TEST_CASES, ids=POS_IDS)
    def test_positive_scenario(self, authenticated_page, test_case):
        executor = FormExecutor(authenticated_page)
        executor.execute_test_case(test_case, is_positive=True)
