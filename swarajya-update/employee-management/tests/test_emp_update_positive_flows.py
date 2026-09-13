import pytest
from emp_update_pages.form_executor import EmployeeUpdateFormExecutor
from emp_update_utils.excel_reader import load_test_cases

positive_cases = load_test_cases("Update_Positive_Flows")


@pytest.mark.positive
@pytest.mark.regression
class TestPositiveFlows:
    """Data-driven positive flow tests from Swarajya-Update-Employee-test-cases.xlsx."""

    @pytest.mark.parametrize(
        "case",
        positive_cases,
        ids=[c["Test Case ID"] for c in positive_cases],
    )
    def test_positive_scenario(self, authenticated_page, case):
        executor = EmployeeUpdateFormExecutor(authenticated_page)
        executor.execute_positive_case(case)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
