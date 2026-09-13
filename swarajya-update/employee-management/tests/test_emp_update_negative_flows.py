import pytest
from emp_update_pages.form_executor import EmployeeUpdateFormExecutor
from emp_update_utils.excel_reader import load_test_cases

negative_cases = load_test_cases("Update_Negative_Flows")


@pytest.mark.negative
@pytest.mark.regression
class TestNegativeFlows:
    """Data-driven negative flow tests from Swarajya-Update-Employee-test-cases.xlsx."""

    @pytest.mark.parametrize(
        "case",
        negative_cases,
        ids=[c["Test Case ID"] for c in negative_cases],
    )
    def test_negative_scenario(self, authenticated_page, case):
        executor = EmployeeUpdateFormExecutor(authenticated_page)
        executor.execute_negative_case(case)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
