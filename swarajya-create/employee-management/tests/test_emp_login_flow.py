import pytest
from emp_pages.login_page import LoginPage


@pytest.mark.login
class TestLoginFlow:
    """Verify authentication works with the credentials from Excel."""

    def test_employee_login_and_dashboard(self, page, employee_creds):
        lp = LoginPage(page)
        lp.login(
            employee_creds["employee_id"],
            employee_creds["password"],
            employee_creds["auth_code"],
        )
        assert lp.is_on_dashboard(), "Should land on /default after login"

    def test_manager_login_and_dashboard(self, page, manager_creds):
        lp = LoginPage(page)
        lp.login(
            manager_creds["employee_id"],
            manager_creds["password"],
            manager_creds["auth_code"],
        )
        assert lp.is_on_dashboard(), "Should land on /default after login"
