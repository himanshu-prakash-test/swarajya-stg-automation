import datetime
import re
from typing import Dict, List, Optional

from playwright.sync_api import Page

from emp_pages.base_page import BasePage
from emp_utils.logger import get_logger

log = get_logger("EmployeePage")


def format_date_for_adapter(date_str: str) -> str:
    """Convert Excel dates to a stable browser input value."""
    clean = str(date_str).strip()
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            parsed = datetime.datetime.strptime(clean, fmt)
            return f"{parsed.month}/{parsed.day}/{parsed.year}"
        except ValueError:
            pass
    return clean


class EmployeePage(BasePage):
    """Page object for Employee Management create/list workflows."""

    LIST_PATH = "/employeeList"
    CREATE_PATH = "/addNewEmployee"

    SAVE_BTN = "button:has-text('Save'), button[type='submit']"
    CANCEL_BTN = "button:has-text('Cancel'), button:has-text('Reset')"
    SEARCH_INPUT = "input[placeholder*='Search' i], input[type='search'], .search-box input"
    CONFIRM_YES_BTN = (
        "mat-card-actions button:has-text('Yes'), "
        "button:has-text('Yes'), button:has-text('Confirm'), button:has-text('OK')"
    )

    FIELD_MAP = {
        "first name": "input[name='emp_first_name'], #emp_first_name",
        "middle name": "input[name='emp_middle_name'], #emp_middle_name",
        "last name": "input[name='emp_last_name'], #emp_last_name",
        "personal email": "input[name='emp_personal_email']",
        "mobile number": "input[name='emp_mobile_number']",
        "official email": "input[name='emp_email']",
        "date of birth": "input[name='emp_dob']",
        "joining date": "input[name='emp_join_date']",
        "gender": "mat-select[name='gender']",
        "department": "mat-select[name='dep']",
        "designation": "mat-select[name='empdesignation']",
        "reporting manager": "mat-select[name='manager']",
        "role": "mat-select[name='role']",
    }

    DROPDOWN_MAP = {
        "gender": "mat-select[name='gender']",
        "department": "mat-select[name='dep']",
        "designation": "mat-select[name='empdesignation']",
        "reporting manager": "mat-select[name='manager']",
        "role": "mat-select[name='role']",
    }

    DATE_MAP = {
        "date of birth": "input[name='emp_dob']",
        "joining date": "input[name='emp_join_date']",
    }

    def navigate_to_employee_list(self) -> None:
        self.goto(self.LIST_PATH)
        self._dismiss_tutorial()
        try:
            self.page.locator(self.SEARCH_INPUT).first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

    def open_create_employee_form(self) -> None:
        first_input = self.page.locator(
            "#emp_first_name, input[name='emp_first_name'], input[placeholder*='First Name' i]"
        ).first

        # Check if already on the create form
        if "addnewemployee" in self.page.url.lower() and first_input.is_visible():
            try:
                # Clear all text inputs to ensure a clean starting state
                for inp in self.page.locator("form input, input[type='text'], input[type='email']").all():
                    if inp.is_visible():
                        inp.fill("")
                self._dismiss_tutorial()
                return
            except Exception:
                pass

        # Try clicking button from dashboard / list if available
        new_employee_button = self.page.locator(
            "button:has-text('New Employee'), button:has-text('Create New Employee'), button:has-text('Add Employee')"
        ).first
        if new_employee_button.is_visible():
            new_employee_button.click()
            self._dismiss_tutorial()
            try:
                first_input.wait_for(state="visible", timeout=8000)
                return
            except Exception:
                pass

        # Navigate directly to the create path
        self.goto(self.CREATE_PATH)
        self._dismiss_tutorial()
        try:
            first_input.wait_for(state="visible", timeout=12000)
        except Exception:
            # Fallback reload via list path if SPA state stalled
            self.goto(self.LIST_PATH)
            self._dismiss_tutorial()
            self.goto(self.CREATE_PATH)
            self._dismiss_tutorial()
            first_input.wait_for(state="visible", timeout=12000)

    def fill_field(self, field_label: str, value: str) -> bool:
        key = field_label.strip().lower()
        raw_value = "" if value is None else str(value)

        if raw_value.lower() in ("blank", "(blank)", "unselected", "none", "not attached", "empty"):
            log.info(f"Leaving field '{field_label}' blank as per Excel test data")
            return True

        if key in self.DROPDOWN_MAP:
            return self.select_dropdown(key, raw_value)

        if key in self.DATE_MAP or "date" in key or "dob" in key:
            return self.fill_date(key, raw_value)

        selector = self.FIELD_MAP.get(key)
        if not selector:
            cleaned = key.replace(" ", "_")
            selector = f"input[name*='{cleaned}' i], input[placeholder*='{field_label}' i]"

        try:
            input_locator = self.page.locator(selector).first
            input_locator.wait_for(state="visible", timeout=5000)
            input_locator.click()
            input_locator.fill("")
            input_locator.press_sequentially(raw_value, delay=10)
            input_locator.dispatch_event("input")
            input_locator.dispatch_event("change")
            input_locator.press("Tab")
            log.info(f"Filled '{field_label}' from Excel data")
            return True
        except Exception as exc:
            log.warning(f"Could not fill text field '{field_label}': {exc}")
            return False

    def fill_date(self, date_field_key: str, date_str: str) -> bool:
        selector = self.DATE_MAP.get(date_field_key, "input[name='emp_dob']")
        formatted_value = format_date_for_adapter(date_str)
        try:
            input_locator = self.page.locator(selector).first
            input_locator.wait_for(state="visible", timeout=5000)
            input_locator.click()
            input_locator.fill("")
            input_locator.press_sequentially(formatted_value, delay=10)
            input_locator.dispatch_event("input")
            input_locator.dispatch_event("change")
            input_locator.press("Tab")
            log.info(f"Filled date '{date_field_key}' = '{date_str}'")
            return True
        except Exception as exc:
            log.warning(f"Failed to fill date '{date_field_key}': {exc}")
            return False

    def _visible_dropdown_options(self) -> List:
        return self.page.locator("mat-option:visible").all()

    def _option_texts(self) -> List[str]:
        options = []
        for option in self._visible_dropdown_options():
            text = option.inner_text().strip()
            if text and text.lower() not in ("select", "--select--", "choose"):
                options.append(text)
        return options

    def select_dropdown(self, dropdown_key: str, option_text: str) -> bool:
        selector = self.DROPDOWN_MAP.get(dropdown_key, f"mat-select[name='{dropdown_key}']")
        wanted = option_text.strip()
        try:
            mat_select = self.page.locator(selector).first
            mat_select.wait_for(state="visible", timeout=6000)
            mat_select.scroll_into_view_if_needed()
            mat_select.click()

            try:
                self.page.locator("mat-option:visible").first.wait_for(state="visible", timeout=4000)
            except Exception:
                pass

            options = self._visible_dropdown_options()
            if not options:
                self.page.keyboard.press("Escape")
                return False

            if "select from given" in wanted.lower() or wanted.lower() in ("select", "--select--", ""):
                for option in options:
                    text = option.inner_text().strip()
                    if text and text.lower() not in ("select", "--select--", "choose"):
                        option.click()
                        try:
                            self.page.locator("mat-option:visible").first.wait_for(state="hidden", timeout=2000)
                        except Exception:
                            pass
                        log.info(f"Selected '{dropdown_key}' from given options: '{text}'")
                        return True
            else:
                # First pass: Exact match (avoids 'Male' matching 'Female')
                for option in options:
                    text = option.inner_text().strip()
                    if text.lower() == wanted.lower():
                        option.click()
                        try:
                            self.page.locator("mat-option:visible").first.wait_for(state="hidden", timeout=2000)
                        except Exception:
                            pass
                        log.info(f"Selected '{dropdown_key}' = '{text}'")
                        return True
                # Second pass: Substring match only if exact match is not found
                for option in options:
                    text = option.inner_text().strip()
                    if wanted.lower() in text.lower():
                        option.click()
                        try:
                            self.page.locator("mat-option:visible").first.wait_for(state="hidden", timeout=2000)
                        except Exception:
                            pass
                        log.info(f"Selected '{dropdown_key}' (substring match) = '{text}'")
                        return True

            self.page.keyboard.press("Escape")
            return False
        except Exception as exc:
            log.warning(f"Error selecting dropdown '{dropdown_key}': {exc}")
            try:
                self.page.keyboard.press("Escape")
            except Exception:
                pass
            return False

    def get_dropdown_options(self, dropdown_key: str) -> List[str]:
        selector = self.DROPDOWN_MAP.get(dropdown_key, f"mat-select[name='{dropdown_key}']")
        try:
            mat_select = self.page.locator(selector).first
            mat_select.wait_for(state="visible", timeout=6000)
            mat_select.scroll_into_view_if_needed()
            mat_select.click()
            try:
                self.page.locator("mat-option:visible").first.wait_for(state="visible", timeout=4000)
            except Exception:
                pass
            options = self._option_texts()
            self.page.keyboard.press("Escape")
            try:
                self.page.locator("mat-option:visible").first.wait_for(state="hidden", timeout=2000)
            except Exception:
                pass
            return options
        except Exception as exc:
            log.warning(f"Error reading options for '{dropdown_key}': {exc}")
            return []

    def validate_all_options_for_dropdown(self, dropdown_key: str) -> List[str]:
        options = self.get_dropdown_options(dropdown_key)
        assert options, f"No options found for dropdown '{dropdown_key}'"
        # Select the first valid option to verify interactivity
        self.select_dropdown(dropdown_key, options[0])
        log.info(f"Validated dropdown '{dropdown_key}' has {len(options)} options; selected '{options[0]}'")
        return options

    def click_save(self) -> None:
        button = self.page.locator(self.SAVE_BTN).first
        button.wait_for(state="visible", timeout=5000)
        button.click()
        log.info("Clicked Save button")

    def click_save_and_confirm(self) -> Dict[str, object]:
        self.click_save()
        confirmation_seen = False

        try:
            yes_button = self.page.locator(self.CONFIRM_YES_BTN).first
            yes_button.wait_for(state="visible", timeout=3000)
            confirmation_seen = True
            yes_button.click()
            try:
                yes_button.wait_for(state="hidden", timeout=3000)
            except Exception:
                pass
            log.info("Confirmed save popup")
        except Exception:
            log.info("No save confirmation popup appeared")

        return {
            "confirmation_seen": confirmation_seen,
            "message": self.get_confirmation_message(timeout=3500),
        }

    def click_cancel(self) -> bool:
        try:
            first_input = self.page.locator(self.FIELD_MAP["first name"]).first
            before_url = self.page.url
            button = self.page.locator(self.CANCEL_BTN).first
            button.wait_for(state="visible", timeout=5000)
            button.click()

            try:
                self.page.wait_for_function(
                    f"() => window.location.href !== '{before_url}' || (document.querySelector('#emp_first_name') && document.querySelector('#emp_first_name').value === '')",
                    timeout=4000,
                )
            except Exception:
                pass

            if self.page.url != before_url:
                return True
            if first_input.is_visible():
                return first_input.input_value().strip() == ""
            return True
        except Exception as exc:
            log.warning(f"Could not validate Cancel/Reset action: {exc}")
            return False

    def get_confirmation_message(self, timeout: int = 1500) -> str:
        combined_selector = (
            "simple-snack-bar, .mat-mdc-snack-bar-label, .toast-message, "
            "[role='alert'], .alert-success, .swal2-title"
        )
        try:
            locator = self.page.locator(combined_selector).first
            locator.wait_for(state="visible", timeout=timeout)
            message = locator.inner_text().strip()
            log.info(f"Captured confirmation message: '{message}'")
            return message
        except Exception:
            return ""

    def get_validation_errors(self) -> List[str]:
        errors = []
        selectors = [
            "mat-error",
            ".mat-mdc-form-field-error",
            ".error-message",
            ".invalid-feedback",
            ".text-danger",
            "simple-snack-bar",
            "[role='alert']",
        ]
        for selector in selectors:
            try:
                for locator in self.page.locator(f"{selector}:visible").all():
                    text = locator.inner_text().strip()
                    if text and "success" not in text.lower() and "added successfully" not in text.lower() and text not in errors:
                        errors.append(text)
            except Exception:
                pass
        return errors

    def is_form_invalid(self) -> bool:
        return self.page.evaluate(
            """() => {
                const form = document.querySelector('form');
                if (form && form.classList.contains('ng-invalid')) return true;
                const invalidFields = document.querySelectorAll(
                    'input.ng-invalid, mat-select.ng-invalid, .mat-mdc-form-field-error, mat-error'
                );
                return invalidFields.length > 0;
            }"""
        )

    def search_employee_in_list(self, query: str, expected_last_name: str = "") -> Optional[Dict[str, str]]:
        self.navigate_to_employee_list()
        cleaned_query = query.strip()

        try:
            input_locator = self.page.locator(self.SEARCH_INPUT).first
            input_locator.wait_for(state="visible", timeout=6000)
            input_locator.click()
            input_locator.fill("")
            input_locator.press_sequentially(cleaned_query, delay=20)
            input_locator.press("Enter")
            
            try:
                self.page.locator("tr, [role='row'], .mat-mdc-row, .mat-row").first.wait_for(state="visible", timeout=6000)
            except Exception:
                pass

            row_selectors = "tr, [role='row'], .mat-mdc-row, .mat-row"
            for row in self.page.locator(row_selectors).all():
                text = row.inner_text().strip()
                lower_text = text.lower()
                if cleaned_query.lower() not in lower_text:
                    continue
                if expected_last_name and expected_last_name.strip().lower() not in lower_text:
                    continue
                return {"row_text": text, "employee_id": self._extract_employee_id(text)}

            body_text = self.page.locator("body").inner_text()
            if cleaned_query.lower() in body_text.lower():
                return {"row_text": body_text, "employee_id": self._extract_employee_id(body_text)}
        except Exception as exc:
            log.warning(f"Error searching employee list for '{cleaned_query}': {exc}")
        return None

    def search_and_verify_employee_in_list(self, first_name: str, last_name: str = "") -> bool:
        return self.search_employee_in_list(first_name, last_name) is not None

    @staticmethod
    def _extract_employee_id(text: str) -> str:
        match = re.search(r"\b(?:EMP[-\s]?)?\d{3,}\b", text, re.IGNORECASE)
        return match.group(0) if match else ""
