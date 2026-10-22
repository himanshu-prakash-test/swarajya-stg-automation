"""Data-driven Negative automated test scenarios for Customer Update module."""

import pytest
from customer_update_pages.form_executor import CustomerUpdateFormExecutor
from customer_update_utils.excel_reader import load_test_cases, is_ui_case

negative_cases = [tc for tc in load_test_cases("Negative_Tests") if is_ui_case(tc)]

param_cases = (
    negative_cases
    if negative_cases
    else [pytest.param(None, marks=pytest.mark.skip(reason="No negative UI test cases found in Swarajya-test-cases.xlsx"))]
)
param_ids = (
    [c.get("Test Case ID", f"TC_CUSTOMER_NEG_{i + 1}") for i, c in enumerate(negative_cases)]
    if negative_cases
    else ["NO_TEST_CASES_YET"]
)


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.customer
@pytest.mark.customer_update
class TestNegativeCustomerUpdateFlows:
    """Data-driven negative validation tests for Customer Update module."""

    @pytest.mark.parametrize("case", param_cases, ids=param_ids)
    def test_negative_scenario(self, authenticated_page, case):
        """Execute negative customer update scenario from Excel test cases."""
        if not case:
            pytest.skip("No test case data available")
        executor = CustomerUpdateFormExecutor(authenticated_page)
        executor.execute_negative_case(case)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
