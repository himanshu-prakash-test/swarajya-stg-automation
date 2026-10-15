"""Data-driven Negative automated test scenarios for Invoice Update module."""

import pytest
from invoice_update_pages.form_executor import InvoiceUpdateFormExecutor
from invoice_update_utils.excel_reader import load_test_cases, is_ui_case

negative_cases = [tc for tc in load_test_cases("Negative_Tests") if is_ui_case(tc)]

if not negative_cases:
    param_cases = [pytest.param(None, marks=pytest.mark.skip(reason="No negative UI test cases found in Swarajya-test-cases.xlsx"))]
    param_ids = ["NO_TEST_CASES_YET"]
else:
    param_cases = negative_cases
    param_ids = [c.get("Test Case ID", f"TC_INV_UPD_NEG_{i+1}") for i, c in enumerate(negative_cases)]


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.invoice
@pytest.mark.invoice_update
class TestInvoiceUpdateNegativeFlows:
    """Data-driven negative validation tests for Invoice Update module."""

    @pytest.mark.parametrize("case", param_cases, ids=param_ids)
    def test_negative_scenario(self, authenticated_page, case):
        """Execute negative invoice update scenario from Excel test cases."""
        if not case:
            pytest.skip("No test case data available")
        executor = InvoiceUpdateFormExecutor(authenticated_page)
        executor.execute_negative_case(case)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
