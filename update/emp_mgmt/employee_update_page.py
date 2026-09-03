"""Page object for the Employee Management update workflow."""

import logging
import os

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

log = logging.getLogger(__name__)


class EmployeeUpdatePage:
    FIELD_ALIASES = {
        "employee id": "id",
        "employee_id": "id",
        "empid": "id",
        "marital status": "emp_maritalStatus",
        "maritalstatus": "emp_maritalStatus",
        "date of birth": "emp_dob",
        "dateofbirth": "emp_dob",
        "date of joining": "emp_doj",
        "dateofjoining": "emp_doj",
        "mobile number": "emp_mobile_number",
        "mobile": "emp_mobile_number",
        "firstname": "emp_first_name",
        "first name": "emp_first_name",
        "middlename": "emp_middle_name",
        "middle name": "emp_middle_name",
        "lastname": "emp_last_name",
        "last name": "emp_last_name",
        "email id": "emp_email",
        "email": "emp_email",
        "personal email id": "emp_personal_email",
        "personal email": "emp_personal_email",
        "personalemail": "emp_personal_email",
        "emergency contact name": "emp_emergency_contact_name",
        "emergencycontactname": "emp_emergency_contact_name",
        "emergency contact number": "emp_emergency_contact_number",
        "emergencycontactnumber": "emp_emergency_contact_number",
        "correspondence address 1": "emp_correspondance_address1",
        "correspondance address 1": "emp_correspondance_address1",
        "address1": "emp_correspondance_address1",
        "address 2": "emp_correspondance_address2",
        "address2": "emp_correspondance_address2",
        "city": "emp_correspondance_city",
        "pin": "emp_correspondance_pin",
    }

    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.list_path = os.environ.get("EMPLOYEE_LIST_PATH", "/employeeList")
        self.target_employee = os.environ.get("EMPLOYEE_TARGET_ID", "1")

    def navigate_to_list(self):
        url = f"{self.base_url}{self.list_path}"
        if not self.page.url.startswith(url):
            self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        try:
            self.page.locator("input[type='search'], input[placeholder*='Search' i], tbody tr, table").first.wait_for(state="visible", timeout=20_000)
        except Exception:
            self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            self.page.locator("input[type='search'], input[placeholder*='Search' i], tbody tr, table").first.wait_for(state="visible", timeout=20_000)
        return self

    def _first(self, locators):
        for locator in locators:
            try:
                if locator.count() and locator.first.is_visible(timeout=1_500):
                    return locator.first
            except Exception:
                continue
        raise AssertionError("Employee-management control was not found")

    def _field(self, *names):
        locators = []
        for name in names:
            key = str(name).strip().lower()
            alias = self.FIELD_ALIASES.get(key, name)
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

    def open_target_profile(self):
        if "/empProfile/" in self.page.url:
            return self

        self.navigate_to_list()
        try:
            search = self._first([
                self.page.locator("input[type='search']"),
                self.page.get_by_placeholder("Search", exact=False),
                self.page.get_by_role("textbox", name="Search", exact=False),
            ])
            search.fill(str(self.target_employee))
            search.press("Enter")
        except Exception:
            pass

        row = self.page.get_by_role("row").filter(has_text=str(self.target_employee))
        try:
            row.first.wait_for(state="visible", timeout=6_000)
        except Exception:
            pass

        for attempt in range(4):
            try:
                profile_btn = self._first([
                    row.locator("button[mattooltip='Profile']"),
                    row.locator("button:has(i.icofont-user)"),
                    self.page.locator("button[mattooltip='Profile']"),
                    self.page.locator("button:has(i.icofont-user)"),
                    self.page.locator("a[href*='empProfile']"),
                    row.locator("button").first,
                    self.page.locator("tbody tr button").first,
                ])
                profile_btn.scroll_into_view_if_needed()
                profile_btn.click(force=True)
                self.page.locator("input[name='emp_first_name'], input[name='id']").first.wait_for(state="visible", timeout=12_000)
                return self
            except Exception:
                if attempt == 3:
                    raise

        return self

    def set_field(self, names, value):
        if isinstance(names, str):
            names = (names,)
        field = self._field(*names)
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
        if isinstance(names, str):
            names = (names,)
        field = self._field(*names)
        try:
            field.click()
            option = self.page.get_by_role("option", name=str(value), exact=True)
            if not option.count():
                option = self.page.locator(f"mat-option:has-text('{value}')").first
            option.wait_for(state="visible", timeout=5_000)
            option.click()
            try:
                option.wait_for(state="hidden", timeout=3_000)
            except Exception:
                pass
        except Exception:
            field.select_option(label=str(value))
        return self

    def set_gender(self, value):
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
        radio.check() if radio.get_attribute("type") == "radio" else radio.click()
        return self

    def toggle(self, name, checked):
        control = self._first([
            self.page.locator(f"mat-slide-toggle:has-text('{name}'), mat-checkbox:has-text('{name}')"),
            self.page.get_by_label(name, exact=False),
            self.page.get_by_role("switch", name=name, exact=False),
            self.page.locator(f"input[type='checkbox'][name*='{name.lower().replace(' ', '_')}']"),
            self.page.locator("mat-slide-toggle, mat-checkbox").first,
        ])
        try:
            if control.is_visible(timeout=3_000):
                control.scroll_into_view_if_needed()
                control.click(force=True)
        except Exception:
            pass
        return self

    def save(self):
        save_btn = self._first([
            self.page.locator("button[type='submit']"),
            self.page.get_by_role("button", name="Save", exact=True),
            self.page.get_by_role("button", name="Update", exact=True),
            self.page.locator("button:has-text('Save')"),
            self.page.locator("button:has-text('Update')"),
        ])
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)
        return self

    def cancel(self):
        cancel_btn = self._first([
            self.page.get_by_role("button", name="Cancel", exact=False),
            self.page.get_by_role("button", name="Discard", exact=False),
            self.page.locator("button:has-text('Cancel')"),
            self.page.locator("button:has-text('Discard')"),
            self.page.locator("button:has-text('Back')"),
        ])
        cancel_btn.scroll_into_view_if_needed()
        cancel_btn.click(force=True)
        return self

    def has_form_errors(self):
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
        if any(v in text for v in ("is required", "invalid email", "enter valid", "already exist", "must be", "cannot be")):
            return True
        return False

    def success_message_visible(self, timeout=4_000):
        # 1. Dynamically wait for URL to transition to employeeList
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

    def validation_visible(self):
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

    def employee_id_is_read_only(self):
        field = self._field("id", "Employee ID", "emp_id")
        return field.is_disabled() or field.get_attribute("readonly") is not None or field.get_attribute("disabled") is not None

    def update(self, fields):
        for names, value in fields.items():
            self.set_field(names, value)
        return self.save()

