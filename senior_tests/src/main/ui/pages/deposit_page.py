from src.main.ui.pages.base_page import BasePage


class DepositPage(BasePage):

    @property
    def account_selector(self):
        return self.page.locator(".account-selector")

    @property
    def amount_input(self):
        return self.page.get_by_placeholder("Enter amount")

    @property
    def deposit_button(self):
        return self.page.get_by_role(
            "button",
            name="Deposit"
        )

    def url(self) -> str:
        return "/deposit"

    def select_account(
        self,
        account_id: int
    ):
        self.account_selector.select_option(
            str(account_id)
        )

        return self

    def enter_amount(
        self,
        amount: float
    ):
        self.amount_input.fill(
            str(amount)
        )

        return self

    def submit_deposit(self):
        self.deposit_button.click()

        return self