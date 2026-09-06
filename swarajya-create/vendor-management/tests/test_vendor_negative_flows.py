import pytest
from vendor_pages.form_executor import FormExecutor
from vendor_utils.excel_reader import read_test_cases, is_ui_case

NEG_TEST_CASES = [tc for tc in read_test_cases("Negative_Tests") if is_ui_case(tc)]
NEG_IDS = [tc["Test Case ID"] for tc in NEG_TEST_CASES]

if not NEG_TEST_CASES:
    raise RuntimeError(
        "No negative UI test cases found in Create-Vendor-Management.xlsx sheet 'Negative_Tests'. "
        "Check that the file exists in test_data/ and the sheet contains rows with Execution Type != 'API'."
    )


@pytest.mark.negative
@pytest.mark.vendor
class TestNegativeFlows:
    """Data-driven negative flow tests from Create-Vendor-Management.xlsx."""

    @pytest.mark.parametrize("test_case", NEG_TEST_CASES, ids=NEG_IDS)
    def test_negative_scenario(self, authenticated_page, test_case):
        executor = FormExecutor(authenticated_page)
        executor.execute_test_case(test_case, is_positive=False)
