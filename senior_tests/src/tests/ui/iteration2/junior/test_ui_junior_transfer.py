import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.generators.random_model_generator import (
    RandomModelGenerator
)
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.testData.account_test_data import AccountTestData

from src.tests.api.iteration2.assertions.account_assertions import (
    AccountAssertions
)
from src.tests.ui.base_ui_test import BaseUITest


@pytest.mark.ui
class TestTransfer(BaseUITest):

    def test_user_can_transfer_between_own_accounts_with_correct_data(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: создаём два счёта
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        receiver_account = api_manager.account_steps.create_account(
            user_spec
        )

        # ШАГ 2: подготавливаем баланс отправителя
        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        # ШАГ 3: получаем токен пользователя
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

        # ШАГ 4: авторизуемся через localStorage
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

        # ШАГ 5: открываем форму перевода
        page.get_by_role(
            "button",
            name="Make a Transfer"
        ).click()

        account_selector = page.locator(
            ".account-selector"
        )

        expect(account_selector).to_be_visible()
        expect(account_selector).to_be_enabled()

        account_selector.select_option(
            value=str(sender_account.id)
        )

        # ШАГ 6: заполняем данные получателя
        page.get_by_placeholder(
            "Enter recipient name"
        ).fill(user_request.username)

        page.get_by_placeholder(
            "Enter recipient account number"
        ).fill(receiver_account.accountNumber)

        transfer_amount = (
            RandomData.generate_valid_transfer_amount()
        )

        transfer_amount_value = str(transfer_amount)

        amount_input = page.get_by_placeholder(
            "Enter amount"
        )

        amount_input.fill(transfer_amount_value)

        expect(amount_input).to_have_value(
            transfer_amount_value
        )

        checkbox = page.locator(
            "input[type='checkbox']"
        )

        checkbox.check()

        expect(checkbox).to_be_checked()

        # ШАГ 7: выполняем перевод
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            page.get_by_role(
                "button",
                name="Send Transfer"
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == (
                f"✅ Successfully transferred ${transfer_amount} "
                f"to account {receiver_account.accountNumber}!"
            )
        )

        # ШАГ 8: проверяем балансы
        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.PREPARED_SENDER_BALANCE
            - transfer_amount
        )

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            receiver_account.id,
            transfer_amount
        )

        # ШАГ 9: проверяем транзакции
        updated_sender = (
            api_manager.account_steps.get_account_by_id(
                user_spec,
                sender_account.id
            )
        )

        updated_receiver = (
            api_manager.account_steps.get_account_by_id(
                user_spec,
                receiver_account.id
            )
        )

        assert len(updated_sender.transactions) == 4

        transfer_out = next(
            (
                transaction
                for transaction in updated_sender.transactions
                if transaction["type"] == "TRANSFER_OUT"
            ),
            None
        )

        assert transfer_out is not None

        assert abs(transfer_out["amount"]) == pytest.approx(
            transfer_amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert len(updated_receiver.transactions) == 1

        transfer_in = updated_receiver.transactions[0]

        assert transfer_in["type"] == "TRANSFER_IN"

        assert abs(transfer_in["amount"]) == pytest.approx(
            transfer_amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

    def test_user_can_transfer_money_to_another_user_with_correct_data(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        second_user_request: CreateUserRequest,
        second_user_spec: dict,
        api_manager: ApiManager
    ):
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: создаём счёт отправителя
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        # ШАГ 2: создаём счёт другого пользователя
        receiver_account = api_manager.account_steps.create_account(
            second_user_spec
        )

        # ШАГ 3: подготавливаем баланс отправителя
        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        # ШАГ 4: получаем токен отправителя
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

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

        # ШАГ 5: открываем форму перевода
        page.get_by_role(
            "button",
            name="Make a Transfer"
        ).click()

        account_selector = page.locator(
            ".account-selector"
        )

        account_selector.select_option(
            value=str(sender_account.id)
        )

        # ШАГ 6: вводим данные другого пользователя
        page.get_by_placeholder(
            "Enter recipient name"
        ).fill(second_user_request.username)

        page.get_by_placeholder(
            "Enter recipient account number"
        ).fill(receiver_account.accountNumber)

        transfer_amount = (
            RandomData.generate_valid_transfer_amount()
        )

        transfer_amount_value = str(transfer_amount)

        page.get_by_placeholder(
            "Enter amount"
        ).fill(transfer_amount_value)

        checkbox = page.locator(
            "input[type='checkbox']"
        )

        checkbox.check()

        expect(checkbox).to_be_checked()

        # ШАГ 7: выполняем перевод
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            page.get_by_role(
                "button",
                name="Send Transfer"
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == (
                f"✅ Successfully transferred ${transfer_amount} "
                f"to account {receiver_account.accountNumber}!"
            )
        )

        # ШАГ 8: проверяем балансы
        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.PREPARED_SENDER_BALANCE
            - transfer_amount
        )

        AccountAssertions.assert_account_balance(
            api_manager,
            second_user_spec,
            receiver_account.id,
            transfer_amount
        )

    def test_user_cannot_transfer_money_with_negative_amount(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: создаём два счёта
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        receiver_account = api_manager.account_steps.create_account(
            user_spec
        )

        # ШАГ 2: подготавливаем баланс отправителя
        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        # ШАГ 3: получаем токен
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

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

        # ШАГ 4: открываем форму перевода
        page.get_by_role(
            "button",
            name="Make a Transfer"
        ).click()

        page.locator(
            ".account-selector"
        ).select_option(
            value=str(sender_account.id)
        )

        page.get_by_placeholder(
            "Enter recipient name"
        ).fill(user_request.username)

        page.get_by_placeholder(
            "Enter recipient account number"
        ).fill(receiver_account.accountNumber)

        # ШАГ 5: вводим отрицательную сумму
        negative_amount = (
            RandomData.generate_negative_transfer_amount()
        )

        negative_amount_value = str(
            negative_amount
        )

        page.get_by_placeholder(
            "Enter amount"
        ).fill(negative_amount_value)

        checkbox = page.locator(
            "input[type='checkbox']"
        )

        checkbox.check()

        expect(checkbox).to_be_checked()

        # ШАГ 6: отправляем форму
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            page.get_by_role(
                "button",
                name="Send Transfer"
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == "❌ Error: Transfer amount must be at least 0.01"
        )

        # ШАГ 7: состояние счетов не изменилось
        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.PREPARED_SENDER_BALANCE
        )

        AccountAssertions.assert_account_is_empty(
            api_manager,
            user_spec,
            receiver_account.id
        )

        updated_sender = (
            api_manager.account_steps.get_account_by_id(
                user_spec,
                sender_account.id
            )
        )

        assert len(updated_sender.transactions) == 3

        assert all(
            transaction["type"] == "DEPOSIT"
            for transaction in updated_sender.transactions
        )

    def test_user_can_repeat_transfer_with_correct_data(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: создаём два счёта
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        receiver_account = api_manager.account_steps.create_account(
            user_spec
        )

        # ШАГ 2: подготавливаем баланс отправителя до 15000
        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        # Сумма специально до 5000:
        # перевод будет выполнен дважды
        initial_transfer_amount = (
            RandomData.generate_valid_deposit_amount()
        )

        # ШАГ 3: выполняем первоначальный перевод через API
        initial_transfer_request = TransferRequest(
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=initial_transfer_amount
        )

        api_manager.account_steps.transfer_money(
            user_spec,
            initial_transfer_request
        )

        # ШАГ 4: получаем токен пользователя
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

        # ШАГ 5: авторизуемся на UI
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

        # ШАГ 6: открываем Transfer Again
        page.get_by_role(
            "button",
            name="Make a Transfer"
        ).click()

        page.get_by_role(
            "button",
            name="Transfer Again"
        ).click()

        # ШАГ 7: ищем транзакции пользователя
        page.get_by_placeholder(
            "Enter name to find transactions"
        ).fill(user_request.username)

        page.get_by_role(
            "button",
            name="Search Transactions"
        ).click()

        # В Java-тесте используется TRANSFER_IN
        transaction_item = (
            page.locator("li.list-group-item")
            .filter(has_text="TRANSFER_IN")
            .first
        )

        expect(transaction_item).to_be_visible()

        transaction_item.locator(
            "button"
        ).click()

        # ШАГ 8: заполняем модальное окно повторного перевода
        modal = page.locator(
            ".modal.show"
        )

        expect(modal).to_be_visible()
        expect(modal).to_contain_text(
            "Repeat Transfer"
        )

        modal.locator(
            "select"
        ).select_option(
            value=str(sender_account.id)
        )

        amount_input = modal.locator(
            "input[type='number']"
        )

        repeat_transfer_amount = initial_transfer_amount
        repeat_transfer_value = str(
            repeat_transfer_amount
        )

        amount_input.fill(
            repeat_transfer_value
        )

        expect(amount_input).to_have_value(
            repeat_transfer_value
        )

        checkbox = modal.locator(
            "input[type='checkbox']"
        )

        checkbox.check()

        expect(checkbox).to_be_checked()

        # ШАГ 9: повторяем перевод
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            modal.get_by_role(
                "button",
                name="Send Transfer"
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == (
                f"✅ Transfer of ${repeat_transfer_amount} "
                f"successful from Account "
                f"{sender_account.id} to "
                f"{receiver_account.id}!"
            )
        )

        # ШАГ 10: получаем актуальное состояние счетов
        updated_sender = (
            api_manager.account_steps.get_account_by_id(
                user_spec,
                sender_account.id
            )
        )

        updated_receiver = (
            api_manager.account_steps.get_account_by_id(
                user_spec,
                receiver_account.id
            )
        )

        # ШАГ 11: проверяем баланс отправителя
        expected_sender_balance = (
            AccountTestData.PREPARED_SENDER_BALANCE
            - initial_transfer_amount
            - repeat_transfer_amount
        )

        assert updated_sender.balance == pytest.approx(
            expected_sender_balance,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        sender_transfer_outs = [
            transaction
            for transaction in updated_sender.transactions
            if transaction["type"] == "TRANSFER_OUT"
        ]

        assert len(sender_transfer_outs) == 2

        assert all(
            abs(transaction["amount"])
            == pytest.approx(
                initial_transfer_amount,
                abs=AccountTestData.FLOAT_ASSERTION_OFFSET
            )
            for transaction in sender_transfer_outs
        )

        assert all(
            transaction["relatedAccountId"]
            == receiver_account.id
            for transaction in sender_transfer_outs
        )

        sender_transfer_ins = [
            transaction
            for transaction in updated_sender.transactions
            if transaction["type"] == "TRANSFER_IN"
        ]

        assert not sender_transfer_ins

        # ШАГ 12: проверяем баланс получателя
        expected_receiver_balance = (
            initial_transfer_amount
            + repeat_transfer_amount
        )

        assert updated_receiver.balance == pytest.approx(
            expected_receiver_balance,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        receiver_transfer_ins = [
            transaction
            for transaction in updated_receiver.transactions
            if transaction["type"] == "TRANSFER_IN"
        ]

        assert len(receiver_transfer_ins) == 2

        assert all(
            abs(transaction["amount"])
            == pytest.approx(
                initial_transfer_amount,
                abs=AccountTestData.FLOAT_ASSERTION_OFFSET
            )
            for transaction in receiver_transfer_ins
        )

        assert all(
            transaction["relatedAccountId"]
            == sender_account.id
            for transaction in receiver_transfer_ins
        )

        receiver_transfer_outs = [
            transaction
            for transaction in updated_receiver.transactions
            if transaction["type"] == "TRANSFER_OUT"
        ]

        assert not receiver_transfer_outs

    def test_user_cannot_find_transactions_by_non_existing_user(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: создаём два счёта
        api_manager.account_steps.create_account(
            user_spec
        )

        api_manager.account_steps.create_account(
            user_spec
        )

        # ШАГ 2: получаем токен пользователя
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

        # ШАГ 3: авторизуемся на UI
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

        # ШАГ 4: открываем Transfer Again
        page.get_by_role(
            "button",
            name="Make a Transfer"
        ).click()

        page.get_by_role(
            "button",
            name="Transfer Again"
        ).click()

        # Генерируем username, но пользователя с ним не создаём
        non_existing_username = (
            RandomModelGenerator.generate(
                CreateUserRequest
            ).username
        )

        page.get_by_placeholder(
            "Enter name to find transactions"
        ).fill(non_existing_username)

        # ШАГ 5: выполняем поиск
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            page.get_by_role(
                "button",
                name="Search Transactions"
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == "❌ No matching users found."
        )

        # ШАГ 6: результатов поиска нет
        transaction_items = page.locator(
            "ul.list-group li.list-group-item"
        )

        expect(
            transaction_items
        ).to_have_count(0)

        repeat_buttons = (
            page.locator("button")
            .filter(has_text="Repeat")
        )

        expect(
            repeat_buttons
        ).to_have_count(0)

    def test_user_cannot_repeat_transfer_with_incorrect_amount(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: создаём два счёта
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        receiver_account = api_manager.account_steps.create_account(
            user_spec
        )

        # ШАГ 2: подготавливаем баланс отправителя
        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        # ШАГ 3: первоначальный успешный перевод через API
        initial_transfer_amount = (
            RandomData.generate_valid_deposit_amount()
        )

        initial_transfer_request = TransferRequest(
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=initial_transfer_amount
        )

        api_manager.account_steps.transfer_money(
            user_spec,
            initial_transfer_request
        )

        sender_balance_after_initial_transfer = (
            AccountTestData.PREPARED_SENDER_BALANCE
            - initial_transfer_amount
        )

        receiver_balance_after_initial_transfer = (
            initial_transfer_amount
        )

        # ШАГ 4: получаем токен пользователя
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

        # ШАГ 5: авторизуемся на UI
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

        # ШАГ 6: открываем Transfer Again
        page.get_by_role(
            "button",
            name="Make a Transfer"
        ).click()

        page.get_by_role(
            "button",
            name="Transfer Again"
        ).click()

        page.get_by_placeholder(
            "Enter name to find transactions"
        ).fill(user_request.username)

        page.get_by_role(
            "button",
            name="Search Transactions"
        ).click()

        transaction_item = (
            page.locator("li.list-group-item")
            .filter(has_text="TRANSFER_IN")
            .first
        )

        expect(transaction_item).to_be_visible()

        transaction_item.locator(
            "button"
        ).click()

        # ШАГ 7: заполняем Repeat Transfer
        modal = page.locator(
            ".modal.show"
        )

        expect(modal).to_be_visible()
        expect(modal).to_contain_text(
            "Repeat Transfer"
        )

        modal.locator(
            "select"
        ).select_option(
            value=str(sender_account.id)
        )

        invalid_amount = (
            RandomData.generate_negative_transfer_amount()
        )

        invalid_amount_value = str(
            invalid_amount
        )

        amount_input = modal.locator(
            "input[type='number']"
        )

        amount_input.fill(
            invalid_amount_value
        )

        expect(amount_input).to_have_value(
            invalid_amount_value
        )

        checkbox = modal.locator(
            "input[type='checkbox']"
        )

        checkbox.check()

        expect(checkbox).to_be_checked()

        # ШАГ 8: пытаемся повторить перевод
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            modal.get_by_role(
                "button",
                name="Send Transfer"
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == "❌ Transfer failed: Please try again."
        )

        # ШАГ 9: получаем актуальные счета
        updated_sender = (
            api_manager.account_steps.get_account_by_id(
                user_spec,
                sender_account.id
            )
        )

        updated_receiver = (
            api_manager.account_steps.get_account_by_id(
                user_spec,
                receiver_account.id
            )
        )

        # ШАГ 10: после неуспешного repeat
        # баланс отправителя не изменился
        assert updated_sender.balance == pytest.approx(
            sender_balance_after_initial_transfer,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        sender_transfer_outs = [
            transaction
            for transaction in updated_sender.transactions
            if transaction["type"] == "TRANSFER_OUT"
        ]

        assert len(sender_transfer_outs) == 1

        assert abs(
            sender_transfer_outs[0]["amount"]
        ) == pytest.approx(
            initial_transfer_amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert (
            sender_transfer_outs[0]["relatedAccountId"]
            == receiver_account.id
        )

        # ШАГ 11: баланс получателя тоже не изменился
        assert updated_receiver.balance == pytest.approx(
            receiver_balance_after_initial_transfer,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        receiver_transfer_ins = [
            transaction
            for transaction in updated_receiver.transactions
            if transaction["type"] == "TRANSFER_IN"
        ]

        assert len(receiver_transfer_ins) == 1

        assert abs(
            receiver_transfer_ins[0]["amount"]
        ) == pytest.approx(
            initial_transfer_amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert (
            receiver_transfer_ins[0]["relatedAccountId"]
            == sender_account.id
        )