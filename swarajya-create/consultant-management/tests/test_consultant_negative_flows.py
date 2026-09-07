import os
import sys
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path_dir in (MODULE_DIR, ROOT_DIR):
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

venv_python = os.path.join(ROOT_DIR, ".venv", "bin", "python3")
if os.path.exists(venv_python) and sys.executable != venv_python and not os.environ.get("_IN_VENV_SUBPROC"):
    os.environ["_IN_VENV_SUBPROC"] = "1"
    os.execv(venv_python, [venv_python] + sys.argv)

from consultant_pages.form_executor import FormExecutor
from consultant_utils.excel_reader import read_test_cases, is_ui_case

try:
    NEG_TEST_CASES = [tc for tc in read_test_cases("Negative_Tests") if is_ui_case(tc)]
    NEG_IDS = [tc["Test Case ID"] for tc in NEG_TEST_CASES]
except Exception as e:
    NEG_TEST_CASES = []
    NEG_IDS = []


@pytest.mark.negative
@pytest.mark.consultant
class TestNegativeFlows:
    """Data-driven negative flow tests from Create-Consultant-Management.xlsx."""

    @pytest.mark.parametrize("test_case", NEG_TEST_CASES, ids=NEG_IDS)
    def test_negative_scenario(self, authenticated_page, test_case):
        executor = FormExecutor(authenticated_page)
        executor.execute_test_case(test_case, is_positive=False)


if __name__ == "__main__":
    config_file = os.path.join(ROOT_DIR, "pytest.ini")
    pytest_args = [__file__, "-c", config_file, "-o", f"rootdir={ROOT_DIR}", "-v", "-s"]
    extra_args = sys.argv[1:]
    if not any(arg in extra_args for arg in ("--headed", "--headless")):
        pytest_args.append("--headed")
    pytest_args.extend(extra_args)
    sys.exit(pytest.main(pytest_args))
