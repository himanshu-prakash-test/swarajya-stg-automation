# shared pages package
from shared.pages.base_page import BasePage
from shared.pages.login_page import LoginPage
from shared.pages.auth_setup_page import AuthSetupPage
from shared.pages.tfa_page import TfaPage

__all__ = ["BasePage", "LoginPage", "AuthSetupPage", "TfaPage"]
