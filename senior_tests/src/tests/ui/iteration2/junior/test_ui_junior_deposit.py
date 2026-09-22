import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.testData.account_test_data import AccountTestData
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
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: создаём счёт через API
        account = api_manager.account_steps.create_account(
            user_spec
        )

        account_id = str(account.id)

        # ШАГ 2: получаем токен пользователя
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

        # ШАГ 3: авторизуем пользователя через localStorage
        page.goto(
            self.UI_BASE_URL,
            wait_until="domcontentloaded"
        )

        page.evaluate(
            "(token) => localStorage.setItem('authToken', token)",
            auth_token
        )

        page.goto(
            f"{self.UI_BASE_URL}/dashboard",
            wait_until="domcontentloaded"
        )

        # ШАГ 4: открываем форму депозита
        page.get_by_role(
            "button",
            name="Deposit Money"
        ).click()

        account_selector = page.locator(
            ".account-selector"
        )

        expect(account_selector).to_be_visible()
        expect(account_selector).to_be_enabled()

        account_selector.select_option(
            value=account_id
        )

        # ШАГ 5: вводим корректную сумму
        deposit_amount = (
            RandomData.generate_valid_deposit_amount()
        )

        deposit_amount_value = str(deposit_amount)

        amount_input = page.get_by_placeholder(
            "Enter amount"
        )

        amount_input.fill(deposit_amount_value)

        expect(amount_input).to_have_value(
            deposit_amount_value
        )

        # ШАГ 6: выполняем депозит и ждём alert
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            page.get_by_role(
                "button",
                name="Deposit",
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == (
                f"✅ Successfully deposited ${deposit_amount} "
                f"to account ACC{account_id}!"
            )
        )

        # ШАГ 7: проверяем состояние счёта через API
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
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: создаём счёт через API
        account = api_manager.account_steps.create_account(
            user_spec
        )

        account_id = str(account.id)

        # ШАГ 2: получаем токен пользователя
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

        # ШАГ 3: авторизуем пользователя через localStorage
        page.goto(
            self.UI_BASE_URL,
            wait_until="domcontentloaded"
        )

        page.evaluate(
            "(token) => localStorage.setItem('authToken', token)",
            auth_token
        )

        page.goto(
            f"{self.UI_BASE_URL}/dashboard",
            wait_until="domcontentloaded"
        )

        # ШАГ 4: открываем форму депозита
        page.get_by_role(
            "button",
            name="Deposit Money"
        ).click()

        account_selector = page.locator(
            ".account-selector"
        )

        expect(account_selector).to_be_visible()
        expect(account_selector).to_be_enabled()

        account_selector.select_option(
            value=account_id
        )

        # ШАГ 5: вводим отрицательную сумму
        incorrect_deposit_amount = (
            RandomData.generate_negative_deposit_amount()
        )

        incorrect_deposit_amount_value = str(
            incorrect_deposit_amount
        )

        amount_input = page.get_by_placeholder(
            "Enter amount"
        )

        amount_input.fill(
            incorrect_deposit_amount_value
        )

        expect(amount_input).to_have_value(
            incorrect_deposit_amount_value
        )

        # ШАГ 6: выполняем депозит и ждём alert
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            page.get_by_role(
                "button",
                name="Deposit",
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == "❌ Please enter a valid amount."
        )

        # ШАГ 7: убеждаемся через API,
        # что счёт остался пустым
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