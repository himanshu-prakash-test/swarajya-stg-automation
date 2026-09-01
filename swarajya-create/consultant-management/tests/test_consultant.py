import pytest
import logging
import re
import os
try:
    from pages.consultant_page import ConsultantPage
except ImportError:
    from consultant_mgmt.pages.consultant_page import ConsultantPage

try:
    from consultant_workbook import ConsultantWorkbook
except ImportError:
    from consultant_mgmt.consultant_workbook import ConsultantWorkbook

log = logging.getLogger(__name__)

def parse_test_data(raw_data_str: str) -> dict:
    """Parses bullet points from excel into a dict of fields."""
    parsed = {}
    if not raw_data_str:
        return parsed
    
    lines = raw_data_str.split("\n")
    for line in lines:
        line = line.strip(" •").strip()
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip(" '")
            
            if val.lower() == "ticked":
                val = True
            elif val.lower() == "unticked":
                val = False
            parsed[key] = val
    return parsed

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_PATH = os.path.join(os.path.dirname(_TEST_DIR), "test_data", "Create-Consultant-Management.xlsx")
if not os.path.exists(_DATA_PATH):
    _DATA_PATH = os.path.join(os.getcwd(), "consultant_mgmt", "test_data", "Create-Consultant-Management.xlsx")

workbook = ConsultantWorkbook(_DATA_PATH)
test_cases = workbook.get_test_cases()

@pytest.fixture
def consultant_page(page, base_url):
    return ConsultantPage(page, base_url)

@pytest.fixture
def admin_login(login_page, tfa_page):
    """Logs in using hardcoded admin credentials (332) and handles 2FA."""
    try:
        emp_id = "332"
        pwd = "test@1234"
        secret = "111111"
        login_page.login(emp_id, pwd)
        
        if "tfa-authcode" in login_page.page.url:
            tfa_page.submit_auth_code(secret)
            tfa_page.is_dashboard_loaded()
        
        yield
    except Exception as e:
        log.error(f"Error in admin_login fixture: {e}")
        import traceback
        traceback.print_exc()
        raise
    
@pytest.mark.usefixtures("admin_login")
class TestConsultantManagement:

    @pytest.mark.parametrize("tc", test_cases, ids=[tc["id"] for tc in test_cases])
    def test_consultant_workflow(self, consultant_page, tc, page, request):
        """Data-driven test executing scenarios from Excel."""
        tc_id = tc["id"]
        scenario = tc["scenario"]
        log.info(f"Executing {tc_id}: {scenario}")
        
        data = parse_test_data(tc["test_data_raw"])
        
        # Ensure screenshot directory exists
        screenshot_dir = os.path.join(os.path.dirname(_TEST_DIR), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        try:
            # 1. Base navigation
            consultant_page.navigate_to_list()
            
            if "search" in scenario.lower() or "Search Term" in data:
                search_term = data.get("Search Term", data.get("First Name", ""))
                include_inactive = data.get("Include Inactive Consultant", False)
                consultant_page.search(search_term, include_inactive)
                
                assert page.locator(f"tbody tr:has-text('{search_term}')").is_visible(), "Consultant not found in search results"
                
            elif "create" in scenario.lower() or "add" in scenario.lower() or "mandatory fields" in scenario.lower():
                consultant_page.click_new_consultant()
                
                for field_name, value in data.items():
                    if field_name.lower() == "active":
                        consultant_page.toggle_active(value)
                    elif field_name.lower() in ("account type", "bank name"):
                        consultant_page.select_option(field_name, value)
                    elif field_name.lower() not in ("search term", "include inactive consultant"):
                        consultant_page.set_field(field_name, value)
                
                if "cancel" in scenario.lower():
                    consultant_page.cancel()
                    assert consultant_page.is_on_dashboard(), "Did not return to dashboard after cancel"
                else:
                    consultant_page.save()
                    if "confirmation pop-up" in scenario.lower():
                        # Take screenshot of popup before handling it
                        page.screenshot(path=f"{screenshot_dir}/{tc_id}_popup.png")
                        
                        confirm_yes = "No" not in scenario
                        consultant_page.confirm_popup(confirm=confirm_yes)
                        
                        if not confirm_yes:
                            assert not consultant_page.is_on_dashboard(), "Should remain on form if NO is clicked"
                        else:
                            assert consultant_page.success_message_visible(), "Success message missing"
                    else:
                        assert consultant_page.success_message_visible(), "Success message missing"
                        
            # Final success screenshot
            page.screenshot(path=f"{screenshot_dir}/{tc_id}_passed.png")
            log.info(f"Test {tc_id} complete. Passed screenshot saved.")
            
        except Exception as e:
            # Capture failure screenshot
            page.screenshot(path=f"{screenshot_dir}/{tc_id}_failed.png")
            log.error(f"Test {tc_id} failed: {e}. Failure screenshot saved.")
            raise
