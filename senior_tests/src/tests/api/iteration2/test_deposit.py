import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs

from src.tests.api.iteration2.assertions.account_assertions import AccountAssertions


@pytest.mark.api
class TestDeposit:

    def test_user_can_deposit_with_random_correct_amount(
        self,
        api_manager,
        user_spec
    ):
        account = api_manager.account_steps.create_account(user_spec)

        amount = RandomData.generate_valid_deposit_amount()

        api_manager.account_steps.deposit_money_on_account(
            user_spec,
            account.id,
            amount,
            amount
        )

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            account.id,
            amount
        )

    @pytest.mark.parametrize(
        "amount",
        [
            0.01,
            4999.99,
            5000.0,
        ],
        ids=[
            "min deposit",
            "below max deposit",
            "max deposit",
        ]
    )
    def test_user_can_deposit_with_boundary_correct_amount(
        self,
        api_manager,
        user_spec,
        amount
    ):
        account = api_manager.account_steps.create_account(user_spec)

        api_manager.account_steps.deposit_money_on_account(
            user_spec,
            account.id,
            amount,
            amount
        )

        AccountAssertions.assert_account_balance(
            api_manager,
            user_spec,
            account.id,
            amount
        )

    @pytest.mark.parametrize(
        "amount, response_spec",
        [
            (
                0.0,
                ResponseSpecs.deposit_amount_less_than_min()
            ),
            (
                5000.01,
                ResponseSpecs.deposit_amount_more_than_max()
            ),
        ],
        ids=[
            "zero deposit",
            "deposit above max",
        ]
    )
    def test_user_cannot_deposit_with_boundary_incorrect_amount(
        self,
        api_manager,
        user_spec,
        amount,
        response_spec
    ):
        account = api_manager.account_steps.create_account(user_spec)

        deposit_request = DepositRequest(
            id=account.id,
            balance=amount
        )

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.DEPOSIT,
            response_spec=response_spec
        ).post(deposit_request)

        AccountAssertions.assert_account_is_empty(
            api_manager,
            user_spec,
            account.id
        )

    @pytest.mark.parametrize(
        "amount, response_spec",
        [
            (
                RandomData.generate_negative_deposit_amount(),
                ResponseSpecs.deposit_amount_less_than_min()
            ),
            (
                RandomData.generate_deposit_amount_more_than_max(),
                ResponseSpecs.deposit_amount_more_than_max()
            ),
        ],
        ids=[
            "negative deposit",
            "random deposit above max",
        ]
    )
    def test_user_cannot_deposit_with_random_incorrect_amount(
        self,
        api_manager,
        user_spec,
        amount,
        response_spec
    ):
        account = api_manager.account_steps.create_account(user_spec)

        deposit_request = DepositRequest(
            id=account.id,
            balance=amount
        )

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.DEPOSIT,
            response_spec=response_spec
        ).post(deposit_request)

        AccountAssertions.assert_account_is_empty(
            api_manager,
            user_spec,
            account.id
        )

    def test_user_cannot_deposit_with_non_existing_account(
        self,
        api_manager,
        user_spec
    ):
        account = api_manager.account_steps.create_account(user_spec)

        non_existing_account_id = (
            RandomData.generate_non_existing_account_id_based(
                account.id
            )
        )

        deposit_request = DepositRequest(
            id=non_existing_account_id,
            balance=RandomData.generate_valid_deposit_amount()
        )

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.DEPOSIT,
            response_spec=ResponseSpecs.unauthorized_access_to_account()
        ).post(deposit_request)

        AccountAssertions.assert_account_is_empty(
            api_manager,
            user_spec,
            account.id
        )

    def test_user_cannot_deposit_to_another_user_account(
        self,
        api_manager,
        user_spec,
        second_user_spec
    ):
        account = api_manager.account_steps.create_account(
            second_user_spec
        )

        deposit_request = DepositRequest(
            id=account.id,
            balance=RandomData.generate_valid_deposit_amount()
        )

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.DEPOSIT,
            response_spec=ResponseSpecs.unauthorized_access_to_account()
        ).post(deposit_request)

        AccountAssertions.assert_account_is_empty(
            api_manager,
            second_user_spec,
            account.id
        )

    @pytest.mark.parametrize(
        "request_spec",
        [
            RequestSpecs.broken_auth_spec(),
            RequestSpecs.unauth_spec(),
        ],
        ids=[
            "wrong authorization token",
            "without authorization",
        ]
    )
    def test_user_cannot_deposit_without_valid_authorization(
        self,
        api_manager,
        user_spec,
        request_spec
    ):
        account = api_manager.account_steps.create_account(user_spec)

        deposit_request = DepositRequest(
            id=account.id,
            balance=RandomData.generate_valid_deposit_amount()
        )

        CrudRequester(
            request_spec=request_spec,
            endpoint=Endpoint.DEPOSIT,
            response_spec=ResponseSpecs.unauthorized()
        ).post(deposit_request)

        AccountAssertions.assert_account_is_empty(
            api_manager,
            user_spec,
            account.id
        )
