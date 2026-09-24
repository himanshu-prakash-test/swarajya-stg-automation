"""Data-driven Negative automated test scenarios for Purchase Order Update module."""

import pytest
from po_update_pages.form_executor import POUpdateFormExecutor
from po_update_utils.excel_reader import load_test_cases

negative_cases = load_test_cases("Negative_Tests") or load_test_cases("Update_Negative_Flows")

if not negative_cases:
    param_cases = [pytest.param(None, marks=pytest.mark.skip(reason="Awaiting test cases in Update-Purchase-Order.xlsx"))]
    param_ids = ["NO_TEST_CASES_YET"]
else:
    param_cases = negative_cases
    param_ids = [c.get("Test Case ID", f"TC_PO_NEG_{i+1}") for i, c in enumerate(negative_cases)]


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.purchase_order
@pytest.mark.po_update
class TestPurchaseOrderUpdateNegativeFlows:
    """Data-driven negative validation tests for Purchase Order Update module."""

    @pytest.mark.parametrize("case", param_cases, ids=param_ids)
    def test_negative_scenario(self, authenticated_page, case):
        """Execute negative purchase order update scenario from Excel test cases."""
        if not case:
            pytest.skip("No test case data available")
        executor = POUpdateFormExecutor(authenticated_page)
        executor.execute_negative_case(case)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
