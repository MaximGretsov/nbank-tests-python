import pytest

from middle_tests.src.main.api.generators.random_data import RandomData
from middle_tests.src.main.api.models.transfer_request import TransferRequest
from middle_tests.src.main.api.requests.transfer_requester import TransferRequester
from middle_tests.src.main.api.requests.steps.account_steps import AccountSteps
from middle_tests.src.main.api.requests.steps.admin_steps import AdminSteps
from middle_tests.src.main.api.requests.steps.user_steps import UserSteps
from middle_tests.src.main.api.specs.request_specs import RequestSpecs
from middle_tests.src.main.api.specs.response_specs import ResponseSpecs
from middle_tests.src.main.api.testData.account_test_data import AccountTestData

from middle_tests.src.tests.iteration2.assertions.account_assertions import AccountAssertions


@pytest.mark.api
class TestTransfer:

    def test_user_can_transfer_between_own_accounts_with_correct_data(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        sender_account_id = AccountSteps.create_account(user_spec)
        receiver_account_id = AccountSteps.create_account(user_spec)

        AccountSteps.prepare_account_for_transfer(
            user_spec,
            sender_account_id
        )

        amount = RandomData.generate_valid_transfer_amount()

        sender_expected_balance = (
            AccountTestData.PREPARED_SENDER_BALANCE - amount
        )
        receiver_expected_balance = (
            AccountTestData.EMPTY_ACCOUNT_BALANCE + amount
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )

        TransferRequester(
            user_spec,
            ResponseSpecs.success_transfer_response(
                amount,
                sender_account_id,
                receiver_account_id
            )
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            user_spec,
            sender_account_id,
            sender_expected_balance
        )

        AccountAssertions.assert_account_balance(
            user_spec,
            receiver_account_id,
            receiver_expected_balance
        )

        AdminSteps.delete_user(user_id)

    @pytest.mark.parametrize(
        "amount, expected_amount",
        [
            (0.01, 0.01),
            (9999.99, 9999.99),
            (10000.0, 10000.0)
        ],
        ids=[
            "min transfer",
            "below max transfer",
            "max transfer"
        ]
    )
    def test_user_can_transfer_to_another_account_with_correct_data(
        self,
        amount,
        expected_amount
    ):
        user_id_1, user_spec_1 = UserSteps.create_user_and_get_auth_spec()
        user_id_2, user_spec_2 = UserSteps.create_user_and_get_auth_spec()

        sender_account_id = AccountSteps.create_account(user_spec_1)
        receiver_account_id = AccountSteps.create_account(user_spec_2)

        AccountSteps.prepare_account_for_transfer(
            user_spec_1,
            sender_account_id
        )

        sender_expected_balance = (
            AccountTestData.PREPARED_SENDER_BALANCE - amount
        )
        receiver_expected_balance = (
            AccountTestData.EMPTY_ACCOUNT_BALANCE + amount
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )

        TransferRequester(
            user_spec_1,
            ResponseSpecs.success_transfer_response(
                expected_amount,
                sender_account_id,
                receiver_account_id
            )
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            user_spec_1,
            sender_account_id,
            sender_expected_balance
        )

        AccountAssertions.assert_account_balance(
            user_spec_2,
            receiver_account_id,
            receiver_expected_balance
        )

        AdminSteps.delete_user(user_id_1)
        AdminSteps.delete_user(user_id_2)

    @pytest.mark.parametrize(
        "amount, response_spec",
        [
            (
                0.0,
                ResponseSpecs.transfer_amount_less_than_min()
            ),
            (
                -100.0,
                ResponseSpecs.transfer_amount_less_than_min()
            ),
            (
                10000.01,
                ResponseSpecs.transfer_amount_more_than_max()
            )
        ],
        ids=[
            "zero transfer",
            "negative transfer",
            "transfer above max"
        ]
    )
    def test_user_cannot_transfer_between_own_accounts_with_invalid_amount(
        self,
        amount,
        response_spec
    ):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        sender_account_id = AccountSteps.create_account(user_spec)
        receiver_account_id = AccountSteps.create_account(user_spec)

        AccountSteps.prepare_account_with_small_balance(
            user_spec,
            sender_account_id
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )

        TransferRequester(
            user_spec,
            response_spec
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            user_spec,
            sender_account_id,
            AccountTestData.SMALL_SENDER_BALANCE
        )

        AccountAssertions.assert_account_balance(
            user_spec,
            receiver_account_id,
            AccountTestData.EMPTY_ACCOUNT_BALANCE
        )

        AdminSteps.delete_user(user_id)

    def test_user_cannot_transfer_when_balance_is_not_enough(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        sender_account_id = AccountSteps.create_account(user_spec)
        receiver_account_id = AccountSteps.create_account(user_spec)

        AccountSteps.prepare_account_with_small_balance(
            user_spec,
            sender_account_id
        )

        amount = RandomData.generate_transfer_amount_more_than_balance(
            AccountTestData.SMALL_SENDER_BALANCE
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )

        TransferRequester(
            user_spec,
            ResponseSpecs.invalid_transfer()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            user_spec,
            sender_account_id,
            AccountTestData.SMALL_SENDER_BALANCE
        )

        AccountAssertions.assert_account_balance(
            user_spec,
            receiver_account_id,
            AccountTestData.EMPTY_ACCOUNT_BALANCE
        )

        AdminSteps.delete_user(user_id)

    def test_user_cannot_transfer_to_non_existing_account(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        sender_account_id = AccountSteps.create_account(user_spec)

        AccountSteps.prepare_account_for_transfer(
            user_spec,
            sender_account_id
        )

        amount = RandomData.generate_valid_transfer_amount()

        non_existing_account_id = (
            RandomData.generate_non_existing_account_id_based(
                sender_account_id
            )
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=non_existing_account_id,
            amount=amount
        )

        TransferRequester(
            user_spec,
            ResponseSpecs.invalid_transfer()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            user_spec,
            sender_account_id,
            AccountTestData.PREPARED_SENDER_BALANCE
        )

        AdminSteps.delete_user(user_id)

    def test_user_cannot_transfer_from_non_existing_account(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        receiver_account_id = AccountSteps.create_account(user_spec)

        AccountSteps.prepare_account_with_small_balance(
            user_spec,
            receiver_account_id
        )

        amount = RandomData.generate_valid_transfer_amount()

        non_existing_account_id = (
            RandomData.generate_non_existing_account_id_based(
                receiver_account_id
            )
        )

        transfer_request = TransferRequest(
            senderAccountId=non_existing_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )

        TransferRequester(
            user_spec,
            ResponseSpecs.unauthorized_access_to_account()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            user_spec,
            receiver_account_id,
            AccountTestData.SMALL_SENDER_BALANCE
        )

        AdminSteps.delete_user(user_id)

    def test_user_cannot_transfer_from_another_user_account(self):
        user_id_1, user_spec_1 = UserSteps.create_user_and_get_auth_spec()
        user_id_2, user_spec_2 = UserSteps.create_user_and_get_auth_spec()

        sender_account_id = AccountSteps.create_account(user_spec_1)
        receiver_account_id = AccountSteps.create_account(user_spec_2)

        AccountSteps.prepare_account_for_transfer(
            user_spec_1,
            sender_account_id
        )

        amount = RandomData.generate_valid_transfer_amount()

        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )

        TransferRequester(
            user_spec_2,
            ResponseSpecs.unauthorized_access_to_account()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            user_spec_1,
            sender_account_id,
            AccountTestData.PREPARED_SENDER_BALANCE
        )

        AccountAssertions.assert_account_balance(
            user_spec_2,
            receiver_account_id,
            AccountTestData.EMPTY_ACCOUNT_BALANCE
        )

        AdminSteps.delete_user(user_id_1)
        AdminSteps.delete_user(user_id_2)

    def test_user_cannot_transfer_without_authorization_token(self):
        user_id_1, user_spec_1 = UserSteps.create_user_and_get_auth_spec()
        user_id_2, user_spec_2 = UserSteps.create_user_and_get_auth_spec()

        sender_account_id = AccountSteps.create_account(user_spec_1)
        receiver_account_id = AccountSteps.create_account(user_spec_2)

        AccountSteps.prepare_account_for_transfer(
            user_spec_1,
            sender_account_id
        )

        amount = RandomData.generate_valid_transfer_amount()

        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )

        TransferRequester(
            RequestSpecs.unauth_spec(),
            ResponseSpecs.unauthorized()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            user_spec_1,
            sender_account_id,
            AccountTestData.PREPARED_SENDER_BALANCE
        )

        AccountAssertions.assert_account_balance(
            user_spec_2,
            receiver_account_id,
            AccountTestData.EMPTY_ACCOUNT_BALANCE
        )

        AdminSteps.delete_user(user_id_1)
        AdminSteps.delete_user(user_id_2)

    def test_user_cannot_transfer_with_wrong_authorization_token(self):
        user_id_1, user_spec_1 = UserSteps.create_user_and_get_auth_spec()
        user_id_2, user_spec_2 = UserSteps.create_user_and_get_auth_spec()

        sender_account_id = AccountSteps.create_account(user_spec_1)
        receiver_account_id = AccountSteps.create_account(user_spec_2)

        AccountSteps.prepare_account_for_transfer(
            user_spec_1,
            sender_account_id
        )

        amount = RandomData.generate_valid_transfer_amount()

        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )

        TransferRequester(
            RequestSpecs.broken_auth_spec(),
            ResponseSpecs.unauthorized()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            user_spec_1,
            sender_account_id,
            AccountTestData.PREPARED_SENDER_BALANCE
        )

        AccountAssertions.assert_account_balance(
            user_spec_2,
            receiver_account_id,
            AccountTestData.EMPTY_ACCOUNT_BALANCE
        )

        AdminSteps.delete_user(user_id_1)
        AdminSteps.delete_user(user_id_2)