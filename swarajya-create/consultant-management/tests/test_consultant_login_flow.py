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

from consultant_pages.login_page import LoginPage
from consultant_utils.excel_reader import read_credentials


@pytest.mark.login
class TestLoginFlow:
    """Authentication and landing verification for Consultant Management."""

    def test_admin_login_and_consultant_access(self, unauthenticated_page):
        page = unauthenticated_page
        login_page = LoginPage(page)
        creds = read_credentials("Admin")
        success = login_page.login(
            employee_id=creds["employee_id"],
            password=creds["password"],
            auth_code=creds.get("auth_code", "111111"),
        )
        assert success, "Admin login failed to authenticate"
        assert not ("login" in page.url.lower() or "tfa" in page.url.lower()), f"User did not reach authenticated dashboard: {page.url}"


if __name__ == "__main__":
    config_file = os.path.join(ROOT_DIR, "pytest.ini")
    pytest_args = [__file__, "-c", config_file, "-o", f"rootdir={ROOT_DIR}", "-v", "-s"]
    extra_args = sys.argv[1:]
    if not any(arg in extra_args for arg in ("--headed", "--headless")):
        pytest_args.append("--headed")
    pytest_args.extend(extra_args)
    sys.exit(pytest.main(pytest_args))
