"""Data-driven Positive automated test scenarios for Employee Update module."""

import pytest
from emp_update_pages.form_executor import EmployeeUpdateFormExecutor
from emp_update_utils.excel_reader import load_test_cases, is_ui_case

positive_cases = [tc for tc in load_test_cases("Positive_Tests") if is_ui_case(tc)]

if not positive_cases:
    param_cases = [pytest.param(None, marks=pytest.mark.skip(reason="No positive UI test cases found in Swarajya-test-cases.xlsx"))]
    param_ids = ["NO_TEST_CASES_YET"]
else:
    param_cases = positive_cases
    param_ids = [c.get("Test Case ID", f"TC_POS_UPD_{i+1:03d}") for i, c in enumerate(positive_cases)]


@pytest.mark.positive
@pytest.mark.regression
@pytest.mark.employee
@pytest.mark.employee_update
class TestEmployeeUpdatePositiveFlows:
    """Data-driven positive flow tests for Employee Update module."""

    @pytest.mark.parametrize("case", param_cases, ids=param_ids)
    def test_positive_scenario(self, authenticated_page, case):
        """Execute positive employee update scenario from Excel test cases."""
        if not case:
            pytest.skip("No test case data available")
        executor = EmployeeUpdateFormExecutor(authenticated_page)
        executor.execute_positive_case(case)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
