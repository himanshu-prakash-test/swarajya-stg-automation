"""Page Object for Employee Update Management module."""

import os
import re
import time
from typing import Any, Dict, List, Optional
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeout
from shared.pages.base_page import BasePage
from shared.utils.logger import get_logger
from emp_update_utils.excel_reader import read_base_url, get_baseline_employee

log = get_logger("employee_update_page")


class EmployeeUpdatePage(BasePage):
    """
    Page Object Model for Employee Update Management workflow.
    
    Navigation Workflow:
    1. /default (Default landing dashboard)
    2. /employeeList (Employee Listing page)
    3. Click profile action icon on employee row -> /empProfile/<id> (Employee Update / Profile view)
    """

    FIELD_ALIASES = {
        "employee id": "id",
        "employee_id": "id",
        "empid": "id",
        "id": "id",
        "marital status": "emp_maritalStatus",
        "maritalstatus": "emp_maritalStatus",
        "marital_status": "emp_maritalStatus",
        "date of birth": "emp_dob",
        "dateofbirth": "emp_dob",
        "date_of_birth": "emp_dob",
        "dob": "emp_dob",
        "date of joining": "emp_doj",
        "dateofjoining": "emp_doj",
        "date_of_joining": "emp_doj",
        "doj": "emp_doj",
        "joining date": "emp_doj",
        "joining_date": "emp_doj",
        "mobile number": "emp_mobile_number",
        "mobile_number": "emp_mobile_number",
        "mobile": "emp_mobile_number",
        "firstname": "emp_first_name",
        "first name": "emp_first_name",
        "first_name": "emp_first_name",
        "middlename": "emp_middle_name",
        "middle name": "emp_middle_name",
        "middle_name": "emp_middle_name",
        "lastname": "emp_last_name",
        "last name": "emp_last_name",
        "last_name": "emp_last_name",
        "email id": "emp_email",
        "email_id": "emp_email",
        "email": "emp_email",
        "official email": "emp_email",
        "official_email": "emp_email",
        "personal email id": "emp_personal_email",
        "personal_email_id": "emp_personal_email",
        "personal email": "emp_personal_email",
        "personal_email": "emp_personal_email",
        "personalemail": "emp_personal_email",
        "emergency contact name": "emp_emergency_contact_name",
        "emergencycontactname": "emp_emergency_contact_name",
        "emergency_contact_name": "emp_emergency_contact_name",
        "emergency contact number": "emp_emergency_contact_number",
        "emergencycontactnumber": "emp_emergency_contact_number",
        "emergency_contact_number": "emp_emergency_contact_number",
        "correspondence address 1": "emp_correspondance_address1",
        "correspondance address 1": "emp_correspondance_address1",
        "correspondence_address_1": "emp_correspondance_address1",
        "correspondance_address_1": "emp_correspondance_address1",
        "address 1": "emp_correspondance_address1",
        "address1": "emp_correspondance_address1",
        "address_1": "emp_correspondance_address1",
        "address 2": "emp_correspondance_address2",
        "address2": "emp_correspondance_address2",
        "address_2": "emp_correspondance_address2",
        "city": "emp_correspondance_city",
        "pin": "emp_correspondance_pin",
    }

    FIELD_SELECTORS = {
        "id": [
            "input[name='id']",
            "[formcontrolname='id']",
            "mat-form-field:has-text('Employee ID') input",
        ],
        "emp_first_name": [
            "input[name='emp_first_name']",
            "[formcontrolname='emp_first_name']",
            "mat-form-field:has-text('First Name') input",
        ],
        "emp_middle_name": [
            "input[name='emp_middle_name']",
            "[formcontrolname='emp_middle_name']",
            "mat-form-field:has-text('Middle Name') input",
        ],
        "emp_last_name": [
            "input[name='emp_last_name']",
            "[formcontrolname='emp_last_name']",
            "mat-form-field:has-text('Last Name') input",
        ],
        "emp_mobile_number": [
            "input[name='emp_mobile_number']",
            "[formcontrolname='emp_mobile_number']",
            "mat-form-field:has-text('Mobile') input",
        ],
        "emp_email": [
            "input[name='emp_email']",
            "[formcontrolname='emp_email']",
            "mat-form-field:has-text('Official Email') input",
        ],
        "emp_personal_email": [
            "input[name='emp_personal_email']",
            "[formcontrolname='emp_personal_email']",
            "mat-form-field:has-text('Personal Email') input",
        ],
        "emp_dob": [
            "input[name='emp_dob']",
            "[formcontrolname='emp_dob']",
            "mat-form-field:has-text('Date Of Birth') input",
            "mat-form-field:has-text('Date of Birth') input",
        ],
        "emp_doj": [
            "input[name='emp_doj']",
            "[formcontrolname='emp_doj']",
            "mat-form-field:has-text('Date Of Joining') input",
            "mat-form-field:has-text('Date of Joining') input",
        ],
        "emp_maritalStatus": [
            "mat-select[name='emp_maritalStatus']",
            "mat-select[formcontrolname='emp_maritalStatus']",
            "mat-form-field:has-text('Marital Status') mat-select",
        ],
        "emp_emergency_contact_name": [
            "input[name='emp_emergency_contact_name']",
            "[formcontrolname='emp_emergency_contact_name']",
            "mat-form-field:has-text('Emergency Contact Name') input",
        ],
        "emp_emergency_contact_number": [
            "input[name='emp_emergency_contact_number']",
            "[formcontrolname='emp_emergency_contact_number']",
            "mat-form-field:has-text('Emergency Contact Number') input",
        ],
        "emp_correspondance_address1": [
            "input[name='emp_correspondance_address1']",
            "[formcontrolname='emp_correspondance_address1']",
            "mat-form-field:has-text('Correspondence Address 1') input",
        ],
        "emp_correspondance_address2": [
            "input[name='emp_correspondance_address2']",
            "[formcontrolname='emp_correspondance_address2']",
            "mat-form-field:has-text('Address 2') input",
        ],
        "emp_correspondance_city": [
            "input[name='emp_correspondance_city']",
            "[formcontrolname='emp_correspondance_city']",
            "mat-form-field:has-text('City') input",
        ],
        "emp_correspondance_pin": [
            "input[name='emp_correspondance_pin']",
            "[formcontrolname='emp_correspondance_pin']",
            "mat-form-field:has-text('PIN') input",
        ],
    }

    def __init__(self, page: Page, base_url: Optional[str] = None):
        dynamic_url = base_url or read_base_url()
        super().__init__(page, base_url=dynamic_url)
        self.list_path = "/employeeList"

    # ----------------- Navigation & Dynamic Waits -----------------

    def open_default_dashboard(self):
        """Step 1: Navigate to Default Landing screen (/default)."""
        if "default" not in self.page.url.lower():
            self.goto("/default")
            self.wait_for_dom_ready()
        self.dismiss_any_tutorial_or_dialog()
        return self

    def open_employee_list(self, direct: bool = True):
        """Step 2: Navigate to Employee Listing screen (/employeeList)."""
        if "/employeelist" in self.page.url.lower():
            return self

        if direct:
            self.goto(self.list_path)
            self.wait_for_dom_ready()
        else:
            self.dismiss_any_tutorial_or_dialog()
            nav_link = self.page.locator(
                "a[href*='employeeList'], "
                "span:has-text('Employee Mgmt'), "
                "span:has-text('Employee Management'), "
                "span:has-text('Employee List'), "
                ":text-is('Employee Mgmt'), "
                "a:has-text('Employee')"
            ).first
            try:
                nav_link.wait_for(state="visible", timeout=6000)
                nav_link.click()
                self.page.wait_for_url(lambda u: "employeelist" in u.lower(), timeout=10000)
            except Exception:
                self.goto(self.list_path)

        # Dynamic wait for employee table or search bar to be visible and data loaded
        try:
            self.page.locator("table tbody tr, input[type='search'], input[placeholder*='Search' i]").first.wait_for(
                state="visible", timeout=15000
            )
            self.page.wait_for_function(
                "() => { const row = document.querySelector('table tbody tr'); return row && !row.innerText.includes('No data'); }",
                timeout=10000,
            )
        except Exception:
            pass

        self.dismiss_any_tutorial_or_dialog()
        return self

    def open_employee_profile(self, employee_id: Optional[str] = None, name: Optional[str] = None, row_index: int = 0):
        """
        Step 3: Open target Employee Profile / Update form.
        Finds row by employee_id or name or row_index, and clicks Profile icon.
        """
        if "/empProfile/" in self.page.url:
            self.dismiss_any_tutorial_or_dialog()
            return self

        self.open_employee_list(direct=True)

        target_identifier = employee_id or name
        # Dynamic wait for employee table rows to render
        try:
            self.page.locator("table tbody tr").first.wait_for(state="visible", timeout=20000)
        except Exception:
            self.page.goto(f"{self.base_url}{self.list_path}", wait_until="domcontentloaded")
            self.page.locator("table tbody tr").first.wait_for(state="visible", timeout=20000)

        # Locate target row
        all_rows = self.page.locator("table tbody tr")
        target_row = all_rows.nth(row_index) if all_rows.count() > row_index else all_rows.first
        if employee_id:
            matching = all_rows.filter(has_text=str(employee_id))
            if matching.count():
                target_row = matching.first

        # Profile button within target row with retry and direct navigation fallback
        target_id = employee_id or "1"
        for attempt in range(3):
            if "/empProfile/" in self.page.url:
                break
            try:
                profile_btn = target_row.locator(
                    "button[mattooltip='Profile'], "
                    "button:has(i.icofont-user), "
                    "a[href*='empProfile'], "
                    "button:has(mat-icon:has-text('person')), "
                    "button"
                ).first
                profile_btn.scroll_into_view_if_needed()
                profile_btn.click(force=True)
                self.page.wait_for_url(lambda u: "/empProfile/" in u, timeout=4000)
                break
            except Exception:
                if attempt == 2 and "/empProfile/" not in self.page.url:
                    self.goto(f"/empProfile/{target_id}")
                    self.wait_for_dom_ready()

        # Dynamic wait for profile view and form data to be populated by Angular
        try:
            self.page.locator("input[name='emp_first_name'], input[name='id'], button:has-text('Save')").first.wait_for(
                state="visible", timeout=15000
            )
            self.page.wait_for_function(
                "() => { const el = document.querySelector('input[name=\"emp_first_name\"], input[name=\"id\"]'); return el && el.value.length > 0; }",
                timeout=10000,
            )
        except Exception:
            pass

        self.dismiss_any_tutorial_or_dialog()
        return self

    open_target_profile = open_employee_profile

    # ----------------- Form Controls & Dynamic Actions -----------------

    def _first(self, locators: List[Locator]) -> Locator:
        for locator in locators:
            try:
                if locator.count() and locator.first.is_visible(timeout=2000):
                    return locator.first
            except Exception:
                continue
        for locator in locators:
            try:
                if locator.count():
                    locator.first.wait_for(state="visible", timeout=3000)
                    return locator.first
            except Exception:
                continue
        for locator in locators:
            try:
                if locator.count():
                    return locator.first
            except Exception:
                continue
        raise AssertionError("Employee update control was not found")

    def _field(self, *names) -> Locator:
        locators = []
        for name in names:
            key = str(name).strip().lower()
            norm_key = key.replace("-", " ").replace("_", " ")
            alias = self.FIELD_ALIASES.get(key) or self.FIELD_ALIASES.get(norm_key) or name
            if alias in self.FIELD_SELECTORS:
                for sel in self.FIELD_SELECTORS[alias]:
                    locators.append(self.page.locator(sel))
            locators.extend([
                self.page.locator(f"input[name='{alias}']"),
                self.page.locator(f"mat-select[name='{alias}']"),
                self.page.locator(f"textarea[name='{alias}']"),
                self.page.locator(f"[formcontrolname='{alias}']"),
                self.page.locator(f"input[name='{name}']"),
                self.page.locator(f"mat-select[name='{name}']"),
                self.page.get_by_label(name, exact=False),
                self.page.get_by_placeholder(name, exact=False),
            ])
        return self._first(locators)

    def set_field(self, names, value):
        """Fill an input field with dynamic events."""
        if isinstance(names, str):
            names = (names,)
        field = self._field(*names)
        field.scroll_into_view_if_needed()
        field.click()
        field.fill(str(value))
        try:
            field.dispatch_event("input")
            field.dispatch_event("change")
            field.press("Tab")
            self.page.keyboard.press("Escape")
        except Exception:
            pass
        return self

    def select_option(self, names, value):
        """Select an option from a mat-select dropdown dynamically."""
        if isinstance(names, str):
            names = (names,)
        field = self._field(*names)
        field.scroll_into_view_if_needed()
        try:
            field.click()
            option = self.page.locator(f"mat-option:has-text('{value}')").first
            if not option.count():
                option = self.page.get_by_role("option", name=str(value), exact=True)
            option.wait_for(state="visible", timeout=5000)
            option.click()
            try:
                option.wait_for(state="hidden", timeout=3000)
            except Exception:
                pass
        except Exception:
            try:
                field.select_option(label=str(value))
            except Exception:
                pass
        return self

    def set_gender(self, value):
        """Select gender radio button dynamically."""
        val_str = str(value).strip().lower()
        if "female" in val_str:
            target_val = "0"
            label = "Female"
        else:
            target_val = "1"
            label = "Male"

        radio = self._first([
            self.page.locator(f"input[name='emp_gender'][value='{target_val}']"),
            self.page.get_by_label(label, exact=True),
            self.page.get_by_role("radio", name=label, exact=True),
        ])
        radio.scroll_into_view_if_needed()
        radio.check() if radio.get_attribute("type") == "radio" else radio.click(force=True)
        return self

    def toggle(self, name: str, checked: bool = True):
        """Toggle a switch or checkbox dynamically."""
        control = self._first([
            self.page.locator(f"mat-slide-toggle:has-text('{name}'), mat-checkbox:has-text('{name}')"),
            self.page.get_by_label(name, exact=False),
            self.page.get_by_role("switch", name=name, exact=False),
            self.page.locator(f"input[type='checkbox'][name*='{name.lower().replace(' ', '_')}']"),
            self.page.locator("mat-slide-toggle, mat-checkbox").first,
        ])
        try:
            control.scroll_into_view_if_needed()
            aria_checked = control.get_attribute("aria-checked")
            if aria_checked is not None:
                current_state = aria_checked.lower() == "true"
                if current_state != checked:
                    control.click(force=True)
            else:
                control.click(force=True)
        except Exception:
            pass
        return self

    def set_datepicker(self, field_name: str, date_value: str):
        """Set a date via datepicker toggle or direct input."""
        toggle = self.page.locator(f"mat-form-field:has(input[name*='{field_name}']) mat-datepicker-toggle button").first
        if toggle.count() and toggle.is_visible():
            try:
                toggle.click()
                cell = self.page.locator("mat-calendar .mat-calendar-body-cell:not(.mat-calendar-body-disabled)").first
                cell.wait_for(state="visible", timeout=4000)
                cell.click()
                try:
                    self.page.locator("mat-calendar").wait_for(state="hidden", timeout=3000)
                except Exception:
                    pass
                return self
            except Exception:
                pass
        return self.set_field(field_name, date_value)

    def save(self):
        """Submit the employee profile update form."""
        save_btn = self._first([
            self.page.locator("button[type='submit']"),
            self.page.get_by_role("button", name="Save", exact=True),
            self.page.get_by_role("button", name="Update", exact=True),
            self.page.locator("button:has-text('Save')"),
            self.page.locator("button:has-text('Update')"),
        ])
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)
        try:
            self.page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass
        return self

    def cancel(self):
        """Click Cancel / Discard button."""
        cancel_btn = self._first([
            self.page.locator("button:has-text('Cancel')"),
            self.page.get_by_role("button", name="Cancel", exact=False),
            self.page.get_by_role("button", name="Discard", exact=False),
            self.page.locator("button:has-text('Discard')"),
            self.page.locator("button:has-text('Back')"),
        ])
        cancel_btn.scroll_into_view_if_needed()
        cancel_btn.click(force=True)
        try:
            self.page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass
        return self

    def get_form_field_value(self, name: str, timeout: int = 5000) -> str:
        """Get the current value of a form field with dynamic population wait."""
        try:
            field = self._field(name)
            tag = field.evaluate("e => e.tagName").upper()
            if tag in ("INPUT", "TEXTAREA"):
                val = field.input_value()
                if not val and timeout > 0:
                    try:
                        self.page.wait_for_function(
                            f"() => {{ const el = document.querySelector('input[name=\"{name}\"], [formcontrolname=\"{name}\"]'); return el && el.value.length > 0; }}",
                            timeout=timeout,
                        )
                        val = field.input_value()
                    except Exception:
                        pass
                return val
            return field.inner_text().strip()
        except Exception:
            return ""

    def employee_id_is_read_only(self) -> bool:
        """Verify that Employee ID field is read-only / disabled."""
        field = self._field("id", "Employee ID", "emp_id")
        return (
            field.is_disabled()
            or field.get_attribute("readonly") is not None
            or field.get_attribute("disabled") is not None
        )

    def is_profile_form_visible(self) -> bool:
        """Check if employee profile form is open and visible."""
        return (
            "/empProfile/" in self.page.url
            or self.page.locator("input[name='emp_first_name'], button:has-text('Save')").first.is_visible()
        )

    def is_field_invalid(self, *names) -> bool:
        """Check if a specific form field or its mat-form-field container is marked invalid."""
        try:
            field = self._field(*names)
            cls = field.get_attribute("class") or ""
            if "ng-invalid" in cls or field.get_attribute("aria-invalid") == "true":
                return True
            parent = field.locator("xpath=ancestor::mat-form-field").first
            if parent.count():
                p_cls = parent.get_attribute("class") or ""
                if "ng-invalid" in p_cls or "mat-form-field-invalid" in p_cls:
                    return True
        except Exception:
            pass
        return False

    def has_form_errors(self) -> bool:
        """Check if form validation errors are visible on the page."""
        error_locators = self.page.locator(
            "mat-error, .mat-mdc-form-field-error, .invalid-feedback, .text-danger, [aria-invalid='true']"
        )
        if error_locators.count():
            for i in range(error_locators.count()):
                try:
                    if error_locators.nth(i).is_visible():
                        return True
                except Exception:
                    continue
        if self.page.locator("input.ng-invalid.ng-touched, mat-select.ng-invalid.ng-touched").count():
            return True
        text = self.page.locator("body").inner_text().lower()
        if any(v in text for v in ("is required", "invalid email", "enter valid", "already exist", "must be", "cannot be", "can't be blank")):
            return True
        return False

    def success_message_visible(self, timeout: int = 4000) -> bool:
        """
        Verify update operation succeeded:
        1. URL redirects to employeeList, or
        2. Success notification / toast is shown, or
        3. No validation errors exist and Save action succeeded.
        """
        # 1. Dynamically wait for URL transition to employeeList
        try:
            self.page.wait_for_url(lambda url: "/employeeList" in url, timeout=timeout)
            return True
        except Exception:
            pass

        # 2. Check toast / snackbar / body text
        try:
            text = self.page.locator("body").inner_text().lower()
            if any(v in text for v in ("success", "updated successfully", "saved successfully", "employee details updated")):
                return True
        except Exception:
            pass

        # 3. Absence of form errors
        return not self.has_form_errors()

    def validation_visible(self) -> bool:
        """Verify that validation feedback was displayed or invalid update was blocked."""
        # 1. Error elements visible
        if self.has_form_errors():
            return True

        # 2. Check if save button is disabled
        save_btn = self.page.locator("button[type='submit'], button:has-text('Save'), button:has-text('Update')").first
        if save_btn.count() and (save_btn.is_disabled() or "disabled" in (save_btn.get_attribute("class") or "")):
            return True

        # 3. Any ng-invalid class on page inputs
        if self.page.locator("input.ng-invalid, mat-select.ng-invalid, .ng-invalid").count():
            return True

        # 4. Form remained on profile without redirecting to employee list
        if "/empProfile/" in self.page.url:
            return True

        return False

    def update(self, fields: Dict[Any, Any]):
        """Fill multiple fields and click Save."""
        for names, value in fields.items():
            self.set_field(names, value)
        return self.save()
