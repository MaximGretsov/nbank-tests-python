from playwright.sync_api import expect

from src.main.ui.pages.base_page import BasePage


class TransferPage(BasePage):

    INCOMING_TRANSFER_TYPE = "TRANSFER_IN"

    @property
    def account_selector(self):
        return self.page.locator(
            ".account-selector"
        )

    @property
    def recipient_name_input(self):
        return self.page.get_by_placeholder(
            "Enter recipient name"
        )

    @property
    def recipient_account_number_input(self):
        return self.page.get_by_placeholder(
            "Enter recipient account number"
        )

    @property
    def transfer_amount_input(self):
        return self.page.get_by_placeholder(
            "Enter amount"
        )

    @property
    def confirmation_checkbox(self):
        return self.page.locator(
            "input[type='checkbox']"
        )

    @property
    def send_transfer_button(self):
        return self.page.get_by_role(
            "button",
            name="Send Transfer"
        )

    @property
    def transfer_again_button(self):
        return self.page.get_by_role(
            "button",
            name="Transfer Again"
        )

    @property
    def transaction_search_input(self):
        return self.page.get_by_placeholder(
            "Enter name to find transactions"
        )

    @property
    def search_transactions_button(self):
        return self.page.get_by_role(
            "button",
            name="Search Transactions"
        )

    @property
    def transactions_list(self):
        return self.page.locator(
            "ul.list-group"
        )

    @property
    def transaction_items(self):
        return self.page.locator(
            "li.list-group-item"
        )

    @property
    def repeat_buttons(self):
        return (
            self.page
            .locator("button")
            .filter(has_text="Repeat")
        )

    @property
    def repeat_transfer_modal(self):
        return self.page.locator(
            ".modal.show"
        )

    @property
    def repeat_sender_account_selector(self):
        return self.repeat_transfer_modal.locator(
            "select"
        )

    @property
    def repeat_transfer_amount_input(self):
        return self.repeat_transfer_modal.locator(
            "input[type='number']"
        )

    @property
    def repeat_confirmation_checkbox(self):
        return self.repeat_transfer_modal.locator(
            "input[type='checkbox']"
        )

    @property
    def repeat_transfer_button(self):
        return self.repeat_transfer_modal.get_by_role(
            "button",
            name="Send Transfer"
        )

    def url(self) -> str:
        return "/transfer"

    def select_sender_account(
        self,
        sender_account_id: int
    ):
        self.account_selector.select_option(
            str(sender_account_id)
        )

        return self

    def enter_receiver_name(
        self,
        receiver_name: str
    ):
        self.recipient_name_input.fill(
            receiver_name
        )

        return self

    def enter_receiver_account_number(
        self,
        receiver_account_number: str
    ):
        self.recipient_account_number_input.fill(
            receiver_account_number
        )

        return self

    def enter_transfer_amount(
        self,
        transfer_amount: float
    ):
        self.transfer_amount_input.fill(
            str(transfer_amount)
        )

        return self

    def confirm_transfer_details(self):
        self.confirmation_checkbox.check()

        return self

    def submit_transfer(self):
        self.send_transfer_button.click()

        return self

    def open_transfer_again(self):
        self.transfer_again_button.click()

        return self

    def search_transactions(
        self,
        username: str
    ):
        self.transaction_search_input.fill(
            username
        )

        self.search_transactions_button.click()

        return self

    def open_repeat_transfer_for(
        self,
        transaction_type: str
    ):
        transaction = (
            self.transaction_items
            .filter(has_text=transaction_type)
            .first
        )

        transaction.locator("button").click()

        expect(
            self.repeat_transfer_modal
        ).to_be_visible()

        expect(
            self.repeat_transfer_modal
        ).to_contain_text(
            "Repeat Transfer"
        )

        return self

    def open_incoming_transfer_for_repeat(self):
        return self.open_repeat_transfer_for(
            self.INCOMING_TRANSFER_TYPE
        )

    def select_repeat_sender_account(
        self,
        sender_account_id: int
    ):
        self.repeat_sender_account_selector.select_option(
            str(sender_account_id)
        )

        return self

    def enter_repeat_transfer_amount(
        self,
        amount: float
    ):
        self.repeat_transfer_amount_input.fill(
            str(amount)
        )

        return self

    def confirm_repeat_transfer_details(self):
        self.repeat_confirmation_checkbox.check()

        return self

    def submit_repeat_transfer(self):
        self.repeat_transfer_button.click()

        return self

    def check_search_results_are_empty(self):
        expect(
            self.transactions_list
        ).to_be_attached()

        expect(
            self.transaction_items
        ).to_have_count(0)

        expect(
            self.repeat_buttons
        ).to_have_count(0)

        return self