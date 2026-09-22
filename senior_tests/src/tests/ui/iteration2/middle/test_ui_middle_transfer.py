import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.generators.random_model_generator import (
    RandomModelGenerator
)
from src.main.api.models.create_user_request import (
    CreateUserRequest
)
from src.main.api.models.transfer_request import (
    TransferRequest
)
from src.main.api.testData.account_test_data import (
    AccountTestData
)

from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.user_dashboard import (
    UserDashboard
)

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
        sender_account = (
            api_manager.account_steps.create_account(
                user_spec
            )
        )

        receiver_account = (
            api_manager.account_steps.create_account(
                user_spec
            )
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        transfer_amount = (
            RandomData.generate_valid_transfer_amount()
        )

        self.auth_as_user(
            page,
            user_request
        )

        transfer_page = (
            UserDashboard(page)
            .open()
            .open_transfer_page()
        )

        (
            transfer_page
            .select_sender_account(
                sender_account.id
            )
            .enter_receiver_name(
                user_request.username
            )
            .enter_receiver_account_number(
                receiver_account.accountNumber
            )
            .enter_transfer_amount(
                transfer_amount
            )
            .confirm_transfer_details()
        )

        transfer_page.perform_action_and_check_alert(
            transfer_page.submit_transfer,
            BankAlert.GOOD_TRANSFER.value.format(
                transfer_amount,
                receiver_account.accountNumber
            )
        )

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

        assert len(
            updated_sender.transactions
        ) == 4

        transfer_out = next(
            (
                transaction
                for transaction
                in updated_sender.transactions
                if transaction["type"]
                == "TRANSFER_OUT"
            ),
            None
        )

        assert transfer_out is not None

        assert abs(
            transfer_out["amount"]
        ) == pytest.approx(
            transfer_amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert len(
            updated_receiver.transactions
        ) == 1

        transfer_in = (
            updated_receiver.transactions[0]
        )

        assert (
            transfer_in["type"]
            == "TRANSFER_IN"
        )

        assert abs(
            transfer_in["amount"]
        ) == pytest.approx(
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
        sender_account = (
            api_manager.account_steps.create_account(
                user_spec
            )
        )

        receiver_account = (
            api_manager.account_steps.create_account(
                second_user_spec
            )
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        transfer_amount = (
            RandomData.generate_valid_transfer_amount()
        )

        self.auth_as_user(
            page,
            user_request
        )

        transfer_page = (
            UserDashboard(page)
            .open()
            .open_transfer_page()
        )

        (
            transfer_page
            .select_sender_account(
                sender_account.id
            )
            .enter_receiver_name(
                second_user_request.username
            )
            .enter_receiver_account_number(
                receiver_account.accountNumber
            )
            .enter_transfer_amount(
                transfer_amount
            )
            .confirm_transfer_details()
        )

        transfer_page.perform_action_and_check_alert(
            transfer_page.submit_transfer,
            BankAlert.GOOD_TRANSFER.value.format(
                transfer_amount,
                receiver_account.accountNumber
            )
        )

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
        sender_account = (
            api_manager.account_steps.create_account(
                user_spec
            )
        )

        receiver_account = (
            api_manager.account_steps.create_account(
                user_spec
            )
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        negative_amount = (
            RandomData.generate_negative_transfer_amount()
        )

        self.auth_as_user(
            page,
            user_request
        )

        transfer_page = (
            UserDashboard(page)
            .open()
            .open_transfer_page()
        )

        (
            transfer_page
            .select_sender_account(
                sender_account.id
            )
            .enter_receiver_name(
                user_request.username
            )
            .enter_receiver_account_number(
                receiver_account.accountNumber
            )
            .enter_transfer_amount(
                negative_amount
            )
            .confirm_transfer_details()
        )

        transfer_page.check_alert_message_and_accept(
            BankAlert
            .AMOUNT_MUST_BE_MORE_THAN_MINIMUM
            .value
        )

        transfer_page.submit_transfer()

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

        assert len(
            updated_sender.transactions
        ) == 3

        assert all(
            transaction["type"] == "DEPOSIT"
            for transaction
            in updated_sender.transactions
        )

    def test_user_can_repeat_transfer_with_correct_data(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        sender_account = (
            api_manager.account_steps.create_account(
                user_spec
            )
        )

        receiver_account = (
            api_manager.account_steps.create_account(
                user_spec
            )
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

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

        repeat_transfer_amount = (
            initial_transfer_amount
        )

        self.auth_as_user(
            page,
            user_request
        )

        transfer_page = (
            UserDashboard(page)
            .open()
            .open_transfer_page()
        )

        (
            transfer_page
            .open_transfer_again()
            .search_transactions(
                user_request.username
            )
            .open_incoming_transfer_for_repeat()
            .select_repeat_sender_account(
                sender_account.id
            )
            .enter_repeat_transfer_amount(
                repeat_transfer_amount
            )
            .confirm_repeat_transfer_details()
        )

        transfer_page.perform_action_and_check_alert(
            transfer_page.submit_repeat_transfer,
            BankAlert
            .REPEAT_TRANSFER_SUCCESS
            .value
            .format(
                repeat_transfer_amount,
                sender_account.id,
                receiver_account.id
            )
        )

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
            for transaction
            in updated_sender.transactions
            if transaction["type"]
            == "TRANSFER_OUT"
        ]

        assert len(
            sender_transfer_outs
        ) == 2

        assert all(
            abs(transaction["amount"])
            == pytest.approx(
                initial_transfer_amount,
                abs=AccountTestData.FLOAT_ASSERTION_OFFSET
            )
            for transaction
            in sender_transfer_outs
        )

        assert all(
            transaction["relatedAccountId"]
            == receiver_account.id
            for transaction
            in sender_transfer_outs
        )

        sender_transfer_ins = [
            transaction
            for transaction
            in updated_sender.transactions
            if transaction["type"]
            == "TRANSFER_IN"
        ]

        assert not sender_transfer_ins

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
            for transaction
            in updated_receiver.transactions
            if transaction["type"]
            == "TRANSFER_IN"
        ]

        assert len(
            receiver_transfer_ins
        ) == 2

        assert all(
            abs(transaction["amount"])
            == pytest.approx(
                initial_transfer_amount,
                abs=AccountTestData.FLOAT_ASSERTION_OFFSET
            )
            for transaction
            in receiver_transfer_ins
        )

        assert all(
            transaction["relatedAccountId"]
            == sender_account.id
            for transaction
            in receiver_transfer_ins
        )

        receiver_transfer_outs = [
            transaction
            for transaction
            in updated_receiver.transactions
            if transaction["type"]
            == "TRANSFER_OUT"
        ]

        assert not receiver_transfer_outs

    def test_user_cannot_find_transactions_by_non_existing_user(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        api_manager.account_steps.create_account(
            user_spec
        )

        api_manager.account_steps.create_account(
            user_spec
        )

        non_existing_username = (
            RandomModelGenerator.generate(
                CreateUserRequest
            ).username
        )

        self.auth_as_user(
            page,
            user_request
        )

        transfer_page = (
            UserDashboard(page)
            .open()
            .open_transfer_page()
            .open_transfer_again()
        )

        transfer_page.check_alert_message_and_accept(
            BankAlert.NO_MATCHING_USERS_FOUND.value
        )

        transfer_page.search_transactions(
            non_existing_username
        )

        transfer_page.check_search_results_are_empty()

    def test_user_cannot_repeat_transfer_with_incorrect_amount(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        sender_account = (
            api_manager.account_steps.create_account(
                user_spec
            )
        )

        receiver_account = (
            api_manager.account_steps.create_account(
                user_spec
            )
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

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

        invalid_amount = (
            RandomData.generate_negative_transfer_amount()
        )

        self.auth_as_user(
            page,
            user_request
        )

        transfer_page = (
            UserDashboard(page)
            .open()
            .open_transfer_page()
        )

        (
            transfer_page
            .open_transfer_again()
            .search_transactions(
                user_request.username
            )
            .open_incoming_transfer_for_repeat()
            .select_repeat_sender_account(
                sender_account.id
            )
            .enter_repeat_transfer_amount(
                invalid_amount
            )
            .confirm_repeat_transfer_details()
        )

        transfer_page.check_alert_message_and_accept(
            BankAlert.REPEAT_TRANSFER_FAILED.value
        )

        transfer_page.submit_repeat_transfer()

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

        assert updated_sender.balance == pytest.approx(
            sender_balance_after_initial_transfer,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        sender_transfer_outs = [
            transaction
            for transaction
            in updated_sender.transactions
            if transaction["type"]
            == "TRANSFER_OUT"
        ]

        assert len(
            sender_transfer_outs
        ) == 1

        assert abs(
            sender_transfer_outs[0]["amount"]
        ) == pytest.approx(
            initial_transfer_amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert (
            sender_transfer_outs[0][
                "relatedAccountId"
            ]
            == receiver_account.id
        )

        assert updated_receiver.balance == pytest.approx(
            receiver_balance_after_initial_transfer,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        receiver_transfer_ins = [
            transaction
            for transaction
            in updated_receiver.transactions
            if transaction["type"]
            == "TRANSFER_IN"
        ]

        assert len(
            receiver_transfer_ins
        ) == 1

        assert abs(
            receiver_transfer_ins[0]["amount"]
        ) == pytest.approx(
            initial_transfer_amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert (
            receiver_transfer_ins[0][
                "relatedAccountId"
            ]
            == sender_account.id
        )