import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.testData.account_test_data import AccountTestData

from src.tests.api.iteration2.assertions.account_assertions import AccountAssertions


@pytest.mark.api
class TestTransfer:

    def test_user_can_transfer_between_own_accounts_with_correct_data(
        self,
        api_manager,
        user_spec
    ):
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )
        receiver_account = api_manager.account_steps.create_account(
            user_spec
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        amount = RandomData.generate_valid_transfer_amount()

        transfer_request = TransferRequest(
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=amount
        )

        api_manager.account_steps.transfer_money(
            user_spec,
            transfer_request
        )

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.PREPARED_SENDER_BALANCE - amount
        )

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            receiver_account.id,
            amount
        )

    @pytest.mark.parametrize(
        "amount",
        [
            0.01,
            9999.99,
            10000.0,
        ],
        ids=[
            "min transfer",
            "below max transfer",
            "max transfer",
        ]
    )
    def test_user_can_transfer_to_another_account_with_correct_data(
        self,
        api_manager,
        user_spec,
        second_user_spec,
        amount
    ):
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        receiver_account = api_manager.account_steps.create_account(
            second_user_spec
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=amount
        )

        api_manager.account_steps.transfer_money(
            user_spec,
            transfer_request
        )

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.PREPARED_SENDER_BALANCE - amount
        )

        AccountAssertions.assert_account_balance(
            api_manager,
            second_user_spec,
            receiver_account.id,
            amount
        )

    @pytest.mark.parametrize(
        "amount, response_spec",
        [
            (
                0.0,
                ResponseSpecs.transfer_amount_less_than_min()
            ),
            (
                RandomData.generate_negative_transfer_amount(),
                ResponseSpecs.transfer_amount_less_than_min()
            ),
            (
                10000.01,
                ResponseSpecs.transfer_amount_more_than_max()
            ),
        ],
        ids=[
            "zero transfer",
            "negative transfer",
            "transfer above max",
        ]
    )
    def test_user_cannot_transfer_between_own_accounts_with_invalid_amount(
        self,
        api_manager,
        user_spec,
        amount,
        response_spec
    ):
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        receiver_account = api_manager.account_steps.create_account(
            user_spec
        )

        api_manager.account_steps.prepare_account_with_small_balance(
            user_spec,
            sender_account.id
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=amount
        )

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.TRANSFER,
            response_spec=response_spec
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.SMALL_SENDER_BALANCE
        )

        AccountAssertions.assert_account_is_empty(
            api_manager,
            user_spec,
            receiver_account.id
        )

    def test_user_cannot_transfer_when_balance_is_not_enough(
        self,
        api_manager,
        user_spec
    ):
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        receiver_account = api_manager.account_steps.create_account(
            user_spec
        )

        api_manager.account_steps.prepare_account_with_small_balance(
            user_spec,
            sender_account.id
        )

        amount = RandomData.generate_transfer_amount_more_than_balance(
            AccountTestData.SMALL_SENDER_BALANCE
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=amount
        )

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.TRANSFER,
            response_spec=ResponseSpecs.invalid_transfer()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.SMALL_SENDER_BALANCE
        )

        AccountAssertions.assert_account_is_empty(
            api_manager,
            user_spec,
            receiver_account.id
        )

    def test_user_cannot_transfer_to_non_existing_account(
        self,
        api_manager,
        user_spec
    ):
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        non_existing_account_id = (
            RandomData.generate_non_existing_account_id_based(
                sender_account.id
            )
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account.id,
            receiverAccountId=non_existing_account_id,
            amount=RandomData.generate_valid_transfer_amount()
        )

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.TRANSFER,
            response_spec=ResponseSpecs.invalid_transfer()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.PREPARED_SENDER_BALANCE
        )

    def test_user_cannot_transfer_from_non_existing_account(
        self,
        api_manager,
        user_spec
    ):
        receiver_account = api_manager.account_steps.create_account(
            user_spec
        )

        api_manager.account_steps.prepare_account_with_small_balance(
            user_spec,
            receiver_account.id
        )

        non_existing_account_id = (
            RandomData.generate_non_existing_account_id_based(
                receiver_account.id
            )
        )

        transfer_request = TransferRequest(
            senderAccountId=non_existing_account_id,
            receiverAccountId=receiver_account.id,
            amount=RandomData.generate_valid_transfer_amount()
        )

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.TRANSFER,
            response_spec=ResponseSpecs.unauthorized_access_to_account()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            receiver_account.id,
            AccountTestData.SMALL_SENDER_BALANCE
        )

    def test_user_cannot_transfer_from_another_user_account(
        self,
        api_manager,
        user_spec,
        second_user_spec
    ):
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        receiver_account = api_manager.account_steps.create_account(
            second_user_spec
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=RandomData.generate_valid_transfer_amount()
        )

        CrudRequester(
            request_spec=second_user_spec,
            endpoint=Endpoint.TRANSFER,
            response_spec=ResponseSpecs.unauthorized_access_to_account()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.PREPARED_SENDER_BALANCE
        )

        AccountAssertions.assert_account_is_empty(
            api_manager,
            second_user_spec,
            receiver_account.id
        )

    @pytest.mark.parametrize(
        "request_spec",
        [
            RequestSpecs.unauth_spec(),
            RequestSpecs.broken_auth_spec(),
        ],
        ids=[
            "without authorization",
            "wrong authorization token",
        ]
    )
    def test_user_cannot_transfer_without_valid_authorization(
        self,
        api_manager,
        user_spec,
        second_user_spec,
        request_spec
    ):
        sender_account = api_manager.account_steps.create_account(
            user_spec
        )

        receiver_account = api_manager.account_steps.create_account(
            second_user_spec
        )

        api_manager.account_steps.prepare_account_for_transfer(
            user_spec,
            sender_account.id
        )

        transfer_request = TransferRequest(
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=RandomData.generate_valid_transfer_amount()
        )

        CrudRequester(
            request_spec=request_spec,
            endpoint=Endpoint.TRANSFER,
            response_spec=ResponseSpecs.unauthorized()
        ).post(transfer_request)

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            sender_account.id,
            AccountTestData.PREPARED_SENDER_BALANCE
        )

        AccountAssertions.assert_account_is_empty(
            api_manager,
            second_user_spec,
            receiver_account.id
        )
