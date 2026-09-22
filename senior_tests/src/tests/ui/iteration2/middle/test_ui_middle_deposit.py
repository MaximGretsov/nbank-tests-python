import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.testData.account_test_data import AccountTestData

from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.user_dashboard import UserDashboard

from src.tests.ui.base_ui_test import BaseUITest


@pytest.mark.ui
class TestDeposit(BaseUITest):

    def test_user_can_deposit_money_with_correct_data(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        # ШАГ 1: создаём счёт через API
        account = api_manager.account_steps.create_account(
            user_spec
        )

        deposit_amount = (
            RandomData.generate_valid_deposit_amount()
        )

        # ШАГ 2: авторизуем пользователя
        self.auth_as_user(
            page,
            user_request
        )

        # ШАГ 3: открываем Deposit
        deposit_page = (
            UserDashboard(page)
            .open()
            .open_deposit_page()
        )

        # ШАГ 4: заполняем форму
        (
            deposit_page
            .select_account(account.id)
            .enter_amount(deposit_amount)
        )

        # ШАГ 5: заранее подписываемся на alert
        deposit_page.check_alert_message_and_accept(
            BankAlert.GOOD_DEPOSIT.value.format(
                deposit_amount,
                account.id
            )
        )

        deposit_page.submit_deposit()

        # ШАГ 6: проверяем через API
        updated_account = (
            api_manager.account_steps.get_account_by_id(
                user_spec,
                account.id
            )
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
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        # ШАГ 1: создаём счёт
        account = api_manager.account_steps.create_account(
            user_spec
        )

        incorrect_deposit_amount = (
            RandomData.generate_negative_deposit_amount()
        )

        # ШАГ 2: авторизуем пользователя
        self.auth_as_user(
            page,
            user_request
        )

        # ШАГ 3: открываем Deposit
        deposit_page = (
            UserDashboard(page)
            .open()
            .open_deposit_page()
        )

        # ШАГ 4: заполняем форму
        (
            deposit_page
            .select_account(account.id)
            .enter_amount(
                incorrect_deposit_amount
            )
        )

        # ШАГ 5: заранее подписываемся на alert
        deposit_page.check_alert_message_and_accept(
            BankAlert.BAD_DEPOSIT.value
        )

        deposit_page.submit_deposit()

        # ШАГ 6: счёт должен остаться пустым
        updated_account = (
            api_manager.account_steps.get_account_by_id(
                user_spec,
                account.id
            )
        )

        assert updated_account.balance == pytest.approx(
            AccountTestData.EMPTY_ACCOUNT_BALANCE,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert not updated_account.transactions