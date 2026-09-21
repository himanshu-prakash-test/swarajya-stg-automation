import pytest
from po_pages.form_executor import FormExecutor
from po_utils.excel_reader import read_test_cases, is_ui_case

try:
    NEG_TEST_CASES = [tc for tc in read_test_cases("Negative_Tests") if is_ui_case(tc)]
    NEG_IDS = [str(tc.get("Test Case ID", f"TC_PO_NEG_{i+1}")) for i, tc in enumerate(NEG_TEST_CASES)]
except Exception:
    NEG_TEST_CASES = []
    NEG_IDS = []


@pytest.mark.negative
@pytest.mark.purchase_order
class TestPurchaseOrderNegativeFlows:
    """Data-driven negative flow tests from Purchase Order Excel sheet."""

    if not NEG_TEST_CASES:
        def test_waiting_for_negative_test_cases(self):
            """Test cases Excel file will be placed in test_data directory by user."""
            pytest.skip("No negative UI test cases found yet. Please place the test case Excel file in test_data/.")
    else:
        @pytest.mark.parametrize("test_case", NEG_TEST_CASES, ids=NEG_IDS)
        def test_negative_scenario(self, authenticated_page, test_case):
            executor = FormExecutor(authenticated_page)
            executor.execute_test_case(test_case, is_positive=False)
