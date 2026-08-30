from typing import Optional, Dict
from pages.base_page import BasePage


class ProjectPage(BasePage):
    """Page object for Project Management module actions and form validations."""

    NAV_PATH = "/project-management"
    CREATE_BTN = "button:has-text('Create New Project'), button:has-text('Add Project'), .btn-create"
    NAME_INPUT = "input[name='projectName'], #projectName, input[placeholder*='Project Name']"
    CODE_INPUT = "input[name='projectCode'], #projectCode, input[placeholder*='Project Code']"
    TYPE_DROPDOWN = "select[name='projectType'], #projectType, .project-type-select"
    SAVE_BTN = "button:has-text('Save'), button:has-text('Submit'), button[type='submit']"
    SEARCH_INPUT = "input[placeholder*='Search'], .search-box input"

    def navigate_to_project_module(self) -> None:
        """Navigates to Project Management dashboard."""
        self.goto(self.NAV_PATH)

    def click_create_project(self) -> None:
        """Clicks the Create New Project button."""
        self.click(self.CREATE_BTN)

    def fill_project_form(self, name: str, code: str, ptype: Optional[str] = None) -> None:
        """Fills project form fields."""
        if name and name.lower() != "blank":
            self.fill(self.NAME_INPUT, name)
        if code and code.lower() != "blank":
            self.fill(self.CODE_INPUT, code)
        if ptype and ptype.lower() not in ("blank", "select", "--select--"):
            el = self.page.locator(self.TYPE_DROPDOWN).first
            el.wait_for(state="visible", timeout=5000)
            el.select_option(label=ptype)

    def submit_form(self) -> None:
        """Clicks Save/Submit button."""
        self.click(self.SAVE_BTN)

    def create_project(self, name: str, code: str, ptype: Optional[str] = None) -> None:
        """Complete workflow to create a project."""
        self.click_create_project()
        self.fill_project_form(name, code, ptype)
        self.submit_form()

    def search_project(self, name_or_code: str) -> bool:
        """Searches for a project in list table."""
        if self.is_visible(self.SEARCH_INPUT, timeout=2000):
            self.fill(self.SEARCH_INPUT, name_or_code)
            self.page.keyboard.press("Enter")
        return self.is_visible(f"text={name_or_code}", timeout=5000)

    def get_validation_message(self) -> str:
        """Captures form field validation or toast error message."""
        return self.get_toast(timeout=3000)
