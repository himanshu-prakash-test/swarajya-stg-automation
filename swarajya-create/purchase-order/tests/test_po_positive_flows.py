import pytest
from po_pages.form_executor import FormExecutor
from po_utils.excel_reader import read_test_cases, is_ui_case

try:
    POS_TEST_CASES = [tc for tc in read_test_cases("Positive_Tests") if is_ui_case(tc)]
    POS_IDS = [str(tc.get("Test Case ID", f"TC_PO_POS_{i+1}")) for i, tc in enumerate(POS_TEST_CASES)]
except Exception:
    POS_TEST_CASES = []
    POS_IDS = []


@pytest.mark.positive
@pytest.mark.purchase_order
class TestPurchaseOrderPositiveFlows:
    """Data-driven positive flow tests from Purchase Order Excel sheet."""

    if not POS_TEST_CASES:
        def test_waiting_for_positive_test_cases(self):
            """Test cases Excel file will be placed in test_data directory by user."""
            pytest.skip("No positive UI test cases found yet. Please place the test case Excel file in test_data/.")
    else:
        @pytest.mark.parametrize("test_case", POS_TEST_CASES, ids=POS_IDS)
        def test_positive_scenario(self, authenticated_page, test_case):
            executor = FormExecutor(authenticated_page)
            executor.execute_test_case(test_case, is_positive=True)
