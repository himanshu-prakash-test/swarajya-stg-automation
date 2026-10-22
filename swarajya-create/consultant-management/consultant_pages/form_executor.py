"""
Form Executor helper for Create Consultant Management:
Orchestrates form population strictly from dynamic Excel test data dictionaries.
ZERO hardcoded values: all fields are populated dynamically from input records.
Dynamic waits ensure stability across varied network and execution speeds.
"""

import logging
from typing import Any, Dict, Optional
from consultant_pages.consultant_page import ConsultantPage

log = logging.getLogger(__name__)


class ConsultantFormExecutor:
    """Automates Create Consultant form filling using key-value pairs from Excel."""

    def __init__(self, consultant_page: ConsultantPage):
        self.consultant = consultant_page

    def populate_form(
        self,
        data: Dict[str, Any],
        submit: bool = False,
        confirm: bool = True,
    ) -> Optional[str]:
        """Populate Consultant form fields dynamically using data from Excel record."""
        tc_id = data.get("Test Case ID", "N/A")
        log.info("Populating Consultant Form for Test Case [%s]", tc_id)

        # 1. First Name
        fn = data.get("First Name")
        if fn is not None:
            self.consultant.enter_first_name(fn)

        # 2. Middle Name
        mn = data.get("Middle Name")
        if mn is not None:
            self.consultant.enter_middle_name(mn)

        # 3. Last Name
        ln = data.get("Last Name")
        if ln is not None:
            self.consultant.enter_last_name(ln)

        # 4. Phone
        ph = data.get("Phone")
        if ph is not None:
            self.consultant.enter_phone(ph)

        # 5. Personal Email
        email = data.get("Personal Email")
        if email is not None:
            self.consultant.enter_personal_email(email)

        # 6. Address
        addr = data.get("Address")
        if addr is not None:
            self.consultant.enter_address(addr)

        # 7. Monthly Fees
        fees = data.get("Monthly Fees")
        if fees is not None:
            self.consultant.enter_monthly_fees(fees)

        # 8. TDS Percentage
        tds = data.get("TDS Percentage (%)") or data.get("TDS Percentage")
        if tds is not None:
            self.consultant.enter_tds_percentage(tds)

        # 9. Bank Name
        bn = data.get("Bank Name")
        if bn is not None:
            self.consultant.enter_bank_name(bn)

        # 10. Account Number
        acc = data.get("Account Number")
        if acc is not None:
            self.consultant.enter_account_number(acc)

        # 11. IFSC Code
        ifsc = data.get("IFSC Code") or data.get("IFSC")
        if ifsc is not None:
            self.consultant.enter_ifsc_code(ifsc)

        # 12. Bank Branch
        branch = data.get("Bank Branch")
        if branch is not None:
            self.consultant.enter_bank_branch(branch)

        # 13. Account Type
        acc_type = data.get("Account Type")
        if acc_type:
            self.consultant.select_account_type(str(acc_type))

        # 14. Status (Active / Inactive)
        status = data.get("Status")
        if status is not None:
            is_active = str(status).strip().lower() in ("active", "true", "1", "yes")
            self.consultant.set_active_checkbox(is_active)

        # 15. Optional submission
        if submit:
            return self.consultant.click_save_and_confirm(confirm=confirm)

        return None
