# 📄 Shared Page Object Models (POM)

Universal Page Object Model components and common interaction wrappers for the **Swarajya ERP Test Automation Suite**.

## Components
- `base_page.py`: Base page encapsulation with auto-waiting, dynamic retries, DOM visibility checks, and toast/notification handlers.
- `login_page.py`: Universal Login page object for credential entry, role-based sign-in, and auth redirects.
- `tfa_page.py`: Two-factor authentication (2FA / OTP) dialog handler.
- `sidebar_page.py`: Global sidebar navigation router across ERP modules.
