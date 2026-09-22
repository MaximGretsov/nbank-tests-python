from src.main.api.models.account_response import AccountResponse
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.models.comparison.model_assertions import ModelAssertions

from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.validated_crud_requester import (
    ValidatedCrudRequester
)
from src.main.api.requests.steps.base_steps import BaseSteps

from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.testData.account_test_data import AccountTestData


class AccountSteps(BaseSteps):

    def create_account(
        self,
        user_spec: dict
    ) -> AccountResponse:
        return ValidatedCrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.CREATE_ACCOUNT,
            response_spec=ResponseSpecs.entity_was_created()
        ).post()

    def get_accounts(
        self,
        user_spec: dict
    ) -> list[AccountResponse]:
        return ValidatedCrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.GET_CUSTOMER_ACCOUNTS,
            response_spec=ResponseSpecs.request_returns_ok()
        ).get()

    def get_account_by_id(
        self,
        user_spec: dict,
        account_id: int
    ) -> AccountResponse:
        accounts = self.get_accounts(user_spec)

        for account in accounts:
            if account.id == account_id:
                return account

        raise AssertionError(
            f"Account with id {account_id} was not found"
        )

    def deposit_money_on_account(
        self,
        user_spec: dict,
        account_id: int,
        deposit_amount: float,
        expected_balance_after_deposit: float
    ) -> AccountResponse:

        deposit_request = DepositRequest(
            id=account_id,
            balance=deposit_amount
        )

        account_response = ValidatedCrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.DEPOSIT,
            response_spec=ResponseSpecs.success_deposit_response(
                account_id,
                expected_balance_after_deposit
            )
        ).post(deposit_request)

        ModelAssertions(
            deposit_request,
            account_response
        ).match()

        return account_response

    def transfer_money(
        self,
        user_spec: dict,
        transfer_request: TransferRequest
    ) -> TransferResponse:

        transfer_response = ValidatedCrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.TRANSFER,
            response_spec=ResponseSpecs.success_transfer_response()
        ).post(transfer_request)

        ModelAssertions(
            transfer_request,
            transfer_response
        ).match()

        return transfer_response

    def prepare_account_for_transfer(
        self,
        user_spec: dict,
        account_id: int
    ) -> None:
        expected_balance = AccountTestData.EMPTY_ACCOUNT_BALANCE

        while (
            expected_balance
            < AccountTestData.PREPARED_SENDER_BALANCE
        ):
            expected_balance += AccountTestData.SMALL_SENDER_BALANCE

            self.deposit_money_on_account(
                user_spec,
                account_id,
                AccountTestData.SMALL_SENDER_BALANCE,
                expected_balance
            )

    def prepare_account_with_small_balance(
        self,
        user_spec: dict,
        account_id: int
    ) -> None:
        self.deposit_money_on_account(
            user_spec,
            account_id,
            AccountTestData.SMALL_SENDER_BALANCE,
            AccountTestData.SMALL_SENDER_BALANCE
        )