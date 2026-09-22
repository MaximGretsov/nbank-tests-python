from playwright.sync_api import expect

from src.main.ui.pages.base_page import BasePage
from src.main.ui.pages.deposit_page import DepositPage
from src.main.ui.pages.transfer_page import TransferPage
from src.main.ui.pages.edit_profile_page import EditProfilePage


class UserDashboard(BasePage):

    DEFAULT_PROFILE_NAME = "noname"

    @property
    def welcome_text(self):
        return self.page.get_by_text(
            "User Dashboard"
        )

    @property
    def create_new_account_button(self):
        return self.page.get_by_role(
            "button",
            name="➕ Create New Account"
        )

    @property
    def deposit_money_button(self):
        return self.page.get_by_role(
            "button",
            name="Deposit Money"
        )

    @property
    def transfer_button(self):
        return self.page.get_by_role(
            "button",
            name="Make a Transfer"
        )

    @property
    def user_info(self):
        return self.page.locator(
            ".user-info"
        )

    @property
    def welcome_text_span(self):
        return self.page.locator(
            ".welcome-text span"
        )

    @property
    def welcome_message(self):
        return self.page.locator(
            ".welcome-text"
        )

    def url(self) -> str:
        return "/dashboard"

    def create_new_account(self):
        self.create_new_account_button.click()

        return self

    def open_deposit_page(self) -> DepositPage:
        self.deposit_money_button.click()

        return DepositPage(self.page)

    def open_transfer_page(self) -> TransferPage:
        self.transfer_button.click()

        return TransferPage(self.page)

    def open_edit_profile(self) -> EditProfilePage:
        self.user_info.click()

        return EditProfilePage(self.page)

    def check_displayed_name(
        self,
        expected_name: str
    ):
        expect(
            self.welcome_text_span
        ).to_have_text(
            expected_name
        )

        return self

    def should_have_welcome_text(
        self,
        profile_name: str
    ):
        expect(
            self.welcome_message
        ).to_have_text(
            f"Welcome, {profile_name}!"
        )

        return self

    def should_have_default_welcome_text(self):
        return self.should_have_welcome_text(
            self.DEFAULT_PROFILE_NAME
        )