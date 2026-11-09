
from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/auth/login"

    def __init__(self, page):
        super().__init__(page)

        # TODO B1.5: email, password, submit_button, error, email_error, password_error
        self.email = page.get_by_test_id("email")
        self.password = page.get_by_test_id("password")
        self.submit_button = page.get_by_test_id("login-submit")
        self.error = page.get_by_test_id("login-error")
        self.email_error = page.get_by_test_id("email-error")
        self.password_error = page.get_by_test_id("password-error")

    def login(self, email: str, password: str):
        # TODO B1.5
        self.email.fill(email)
        self.password.fill(password)
        self.submit_button.click()
        return self
