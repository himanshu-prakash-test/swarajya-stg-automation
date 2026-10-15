"""Data-driven Positive automated test scenarios for Invoice Update module."""

import pytest
from invoice_update_pages.form_executor import InvoiceUpdateFormExecutor
from invoice_update_utils.excel_reader import load_test_cases, is_ui_case

positive_cases = [tc for tc in load_test_cases("Positive_Tests") if is_ui_case(tc)]

param_cases = (
    positive_cases
    if positive_cases
    else [pytest.param(None, marks=pytest.mark.skip(reason="No positive UI test cases found in Swarajya-test-cases.xlsx"))]
)
param_ids = (
    [c.get("Test Case ID", f"TC_INV_UPD_POS_{i + 1}") for i, c in enumerate(positive_cases)]
    if positive_cases
    else ["NO_TEST_CASES_YET"]
)


@pytest.mark.positive
@pytest.mark.regression
@pytest.mark.invoice
@pytest.mark.invoice_update
class TestInvoiceUpdatePositiveFlows:
    """Data-driven positive flow tests for Invoice Update module."""

    @pytest.mark.parametrize("case", param_cases, ids=param_ids)
    def test_positive_scenario(self, authenticated_page, case):
        """Execute positive invoice update scenario from Excel test cases."""
        if not case:
            pytest.skip("No test case data available")
        executor = InvoiceUpdateFormExecutor(authenticated_page)
        executor.execute_positive_case(case)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
