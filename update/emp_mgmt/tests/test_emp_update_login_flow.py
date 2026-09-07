import pytest
from emp_update_pages.login_page import LoginPage
from emp_update_pages.employee_update_page import EmployeeUpdatePage
from emp_update_utils.logger import get_logger

log = get_logger("test_emp_update_login_flow")


@pytest.mark.login
@pytest.mark.sanity
class TestLoginFlow:
    """Authentication and landing verification for Employee Update Module."""

    def test_hr_login_and_employee_update_access(self, unauthenticated_page):
        page = unauthenticated_page
        login_p = LoginPage(page)
        ok = login_p.login(role="HR")
        assert ok, "Failed to authenticate with HR credentials"

        emp_update = EmployeeUpdatePage(page)
        emp_update.open_target_profile()
        assert "/empProfile/" in page.url or "/employeeList" in page.url, (
            f"Expected to navigate to employee profile/list, got {page.url}"
        )
        log.info("HR Login and Employee Profile navigation verified successfully.")


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
