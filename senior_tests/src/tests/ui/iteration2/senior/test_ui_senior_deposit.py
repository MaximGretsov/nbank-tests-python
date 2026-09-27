import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.testData.account_test_data import AccountTestData
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
@pytest.mark.user_session(1)
class TestDeposit:

    def test_user_can_deposit_money_with_correct_data(
        self,
        page: Page,
        user_spec: dict,
        api_manager: ApiManager
    ):
        account = api_manager.account_steps.create_account(user_spec)
        deposit_amount = RandomData.generate_valid_deposit_amount()

        deposit_page = (
            UserDashboard(page)
            .open()
            .open_deposit_page()
        )

        (
            deposit_page
            .select_account(account.id)
            .enter_amount(deposit_amount)
        )

        deposit_page.perform_action_and_check_alert(
            deposit_page.submit_deposit,
            BankAlert.GOOD_DEPOSIT.value.format(
                deposit_amount,
                account.id
            )
        )

        updated_account = api_manager.account_steps.get_account_by_id(
            user_spec,
            account.id
        )

        assert updated_account.balance == pytest.approx(
            deposit_amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert len(updated_account.transactions) == 1

        transaction = updated_account.transactions[0]

        assert transaction["amount"] == pytest.approx(
            deposit_amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )
        assert transaction["type"] == "DEPOSIT"

    def test_user_cannot_deposit_money_with_incorrect_data(
        self,
        page: Page,
        user_spec: dict,
        api_manager: ApiManager
    ):
        account = api_manager.account_steps.create_account(user_spec)
        incorrect_deposit_amount = RandomData.generate_negative_deposit_amount()

        deposit_page = (
            UserDashboard(page)
            .open()
            .open_deposit_page()
        )

        (
            deposit_page
            .select_account(account.id)
            .enter_amount(incorrect_deposit_amount)
        )

        deposit_page.perform_action_and_check_alert(
            deposit_page.submit_deposit,
            BankAlert.BAD_DEPOSIT.value
        )

        updated_account = api_manager.account_steps.get_account_by_id(
            user_spec,
            account.id
        )

        assert updated_account.balance == pytest.approx(
            AccountTestData.EMPTY_ACCOUNT_BALANCE,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert not updated_account.transactions