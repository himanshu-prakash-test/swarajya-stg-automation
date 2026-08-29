import pytest

from emp_pages.form_executor import FormExecutor
from emp_utils.excel_reader import is_ui_case, read_test_cases

negative_cases = read_test_cases("Negative_Flows")


def _excel_params(cases):
    params = []
    for case in cases:
        marks = []
        if not is_ui_case(case):
            marks.append(pytest.mark.skip(reason="Execution Type is API in Excel workbook"))
        params.append(pytest.param(case, marks=marks, id=case["Test Case ID"]))
    return params


@pytest.mark.negative
class TestNegativeFlows:
    """Data-driven negative flow tests from the Excel workbook."""

    @pytest.mark.parametrize("tc", _excel_params(negative_cases))
    def test_negative_scenario(self, logged_in_page, tc):
        executor = FormExecutor(logged_in_page)
        executor.execute_test_case(tc, is_positive=False)
