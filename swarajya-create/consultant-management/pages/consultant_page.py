"""Page object for Consultant Management."""

import logging
import os

log = logging.getLogger(__name__)

class ConsultantPage:
    FIELD_ALIASES = {
        "first name": "firstName",
        "last name": "lastName",
        "middle name": "middleName",
        "phone": "phone",
        "personal email": "email",
        "email": "email",
        "monthly fees": "monthlyFees",
        "tds percentage": "tds",
        "bank name": "bankName",
        "account number": "accountNumber",
        "ifsc code": "ifscCode",
        "account type": "accountType",
        "address": "address",
        "bank branch": "bankBranch"
    }

    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.list_path = os.environ.get("CONSULTANT_LIST_PATH", "/consultantList")

    def navigate_to_list(self):
        url = f"{self.base_url}{self.list_path}"
        if self.page.url != url:
            self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        
        # Dynamic wait for table or new button
        self.page.locator("button:has-text('New Consultant'), tbody tr").first.wait_for(state="visible", timeout=15_000)
        return self

    def click_new_consultant(self):
        self.navigate_to_list()
        btn = self.page.locator("button:has-text('New Consultant')").or_(
            self.page.get_by_role("button", name="New Consultant", exact=False)
        )
        btn.click()
        # Wait for form to appear
        self.page.locator("input[formcontrolname='firstName'], input[name='firstName']").first.wait_for(state="visible", timeout=10_000)
        return self

    def _first(self, locators):
        for locator in locators:
            try:
                if locator.count() and locator.first.is_visible(timeout=1_500):
                    return locator.first
            except Exception:
                continue
        raise AssertionError("Consultant control was not found")

    def _field(self, name):
        key = str(name).strip().lower()
        alias = self.FIELD_ALIASES.get(key, name)
        locators = [
            self.page.locator(f"input[formcontrolname='{alias}']"),
            self.page.locator(f"input[name='{alias}']"),
            self.page.locator(f"mat-select[formcontrolname='{alias}']"),
            self.page.locator(f"mat-select[name='{alias}']"),
            self.page.locator(f"textarea[formcontrolname='{alias}']"),
            self.page.get_by_label(name, exact=False),
            self.page.get_by_placeholder(name, exact=False)
        ]
        return self._first(locators)

    def set_field(self, name, value):
        field = self._field(name)
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

    def select_option(self, name, value):
        field = self._field(name)
        try:
            field.click()
            option = self.page.get_by_role("option", name=str(value), exact=True)
            if not option.count():
                option = self.page.locator(f"mat-option:has-text('{value}')").first
            option.wait_for(state="visible", timeout=5_000)
            option.click()
        except Exception:
            field.select_option(label=str(value))
        return self

    def toggle_active(self, active: bool):
        control = self._first([
            self.page.get_by_label("Active", exact=False),
            self.page.get_by_role("switch", name="Active", exact=False),
            self.page.locator("input[type='checkbox'][formcontrolname='isActive']")
        ])
        try:
            if control.is_checked() != active:
                control.click()
        except Exception:
            control.click()
        return self

    def save(self):
        save_btn = self._first([
            self.page.get_by_role("button", name="Save", exact=True),
            self.page.locator("button:has-text('Save')"),
            self.page.locator("button[type='submit']")
        ])
        save_btn.scroll_into_view_if_needed()
        save_btn.click(force=True)
        return self

    def cancel(self):
        cancel_btn = self._first([
            self.page.get_by_role("button", name="Cancel", exact=True),
            self.page.locator("button:has-text('Cancel')")
        ])
        cancel_btn.click()
        return self

    def confirm_popup(self, confirm: bool = True):
        # Wait for dialog
        dialog = self.page.locator("mat-dialog-container, .modal-dialog").first
        dialog.wait_for(state="visible", timeout=5_000)
        btn_text = "Yes" if confirm else "No"
        btn = self.page.locator(f"button:has-text('{btn_text}')").or_(
            self.page.get_by_role("button", name=btn_text, exact=True)
        ).first
        btn.click()
        return self

    def search(self, term, include_inactive=False):
        if include_inactive:
            self.toggle_include_inactive(True)
            
        search_input = self.page.locator("input[type='search'], input[placeholder*='Search']").first
        search_input.fill(str(term))
        search_input.press("Enter")
        
        # Dynamically wait for table update via network activity
        try:
            self.page.wait_for_load_state("networkidle", timeout=5_000)
            self.page.locator("tbody tr").first.wait_for(state="visible", timeout=10_000)
        except Exception:
            pass
        return self

    def toggle_include_inactive(self, check: bool):
        cb = self.page.locator("mat-checkbox:has-text('Include Inactive'), input[type='checkbox']").first
        if cb.is_checked() != check:
            cb.click()
        return self

    def edit_consultant(self, name):
        self.search(name, include_inactive=True)
        row = self.page.get_by_role("row").filter(has_text=name).first
        row.wait_for(state="visible", timeout=5_000)
        edit_btn = row.locator("button:has(i.icofont-edit), button[mattooltip='Edit']").first
        edit_btn.click()
        self.page.locator("input[formcontrolname='firstName']").first.wait_for(state="visible", timeout=5_000)
        return self

    def success_message_visible(self, timeout=6_000) -> bool:
        # Check toast / snackbar / body text
        try:
            text = self.page.locator("body").inner_text().lower()
            if any(v in text for v in ("success", "saved successfully", "consultant added")):
                return True
        except Exception:
            pass
        return False

    def is_on_dashboard(self) -> bool:
        try:
            self.page.wait_for_url(lambda url: self.list_path in url, timeout=5_000)
            return True
        except Exception:
            return False
