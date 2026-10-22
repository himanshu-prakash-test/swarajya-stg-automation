"""
Login Page Object for Customer Management.
Inherits from centralized Shared LoginPage to leverage auto 503 retry,
robust 2FA authentication, and storage state management.
"""

from shared.pages.login_page import LoginPage

__all__ = ["LoginPage"]
