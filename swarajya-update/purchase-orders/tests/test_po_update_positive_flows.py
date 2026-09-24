"""Data-driven Positive automated test scenarios for Purchase Order Update module."""

import pytest
from po_update_pages.form_executor import POUpdateFormExecutor
from po_update_utils.excel_reader import load_test_cases

positive_cases = load_test_cases("Positive_Tests") or load_test_cases("Update_Positive_Flows")

if not positive_cases:
    param_cases = [pytest.param(None, marks=pytest.mark.skip(reason="Awaiting test cases in Update-Purchase-Order.xlsx"))]
    param_ids = ["NO_TEST_CASES_YET"]
else:
    param_cases = positive_cases
    param_ids = [c.get("Test Case ID", f"TC_PO_POS_{i+1}") for i, c in enumerate(positive_cases)]


@pytest.mark.positive
@pytest.mark.regression
@pytest.mark.purchase_order
@pytest.mark.po_update
class TestPurchaseOrderUpdatePositiveFlows:
    """Data-driven positive flow tests for Purchase Order Update module."""

    @pytest.mark.parametrize("case", param_cases, ids=param_ids)
    def test_positive_scenario(self, authenticated_page, case):
        """Execute positive purchase order update scenario from Excel test cases."""
        if not case:
            pytest.skip("No test case data available")
        executor = POUpdateFormExecutor(authenticated_page)
        executor.execute_positive_case(case)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
