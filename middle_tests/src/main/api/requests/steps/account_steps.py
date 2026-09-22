from middle_tests.src.main.api.models.account_response import AccountResponse
from middle_tests.src.main.api.models.deposit_request import DepositRequest
from middle_tests.src.main.api.requests.create_account_requester import CreateAccountRequester
from middle_tests.src.main.api.requests.customer_accounts_requester import CustomerAccountsRequester
from middle_tests.src.main.api.requests.deposit_requester import DepositRequester
from middle_tests.src.main.api.specs.response_specs import ResponseSpecs

from middle_tests.src.main.api.testData.account_test_data import AccountTestData


class AccountSteps:

    @staticmethod
    def create_account(user_spec: dict) -> int:
        response = CreateAccountRequester(
            user_spec,
            ResponseSpecs.entity_was_created()
        ).post()

        return response.json()["id"]

    @staticmethod
    def get_accounts(user_spec: dict) -> list[AccountResponse]:
        response = CustomerAccountsRequester(
            user_spec,
            ResponseSpecs.request_returns_ok()
        ).get()

        return [
            AccountResponse(**account)
            for account in response.json()
        ]

    @staticmethod
    def get_account_by_id(
        user_spec: dict,
        account_id: int
    ) -> AccountResponse:
        accounts = AccountSteps.get_accounts(user_spec)

        for account in accounts:
            if account.id == account_id:
                return account

        raise AssertionError(
            f"Account with id {account_id} was not found"
        )

    @staticmethod
    def deposit_money_on_account(
        user_spec: dict,
        account_id: int,
        deposit_amount: float,
        expected_balance_after_deposit: float
    ) -> None:
        deposit_request = DepositRequest(
            id=account_id,
            balance=deposit_amount
        )

        DepositRequester(
            user_spec,
            ResponseSpecs.success_deposit_response(
                account_id,
                expected_balance_after_deposit
            )
        ).post(deposit_request)

    @staticmethod
    def prepare_account_for_transfer(
        user_spec: dict,
        account_id: int
    ) -> None:
        expected_balance = AccountTestData.EMPTY_ACCOUNT_BALANCE

        while expected_balance < AccountTestData.PREPARED_SENDER_BALANCE:
            expected_balance += AccountTestData.SMALL_SENDER_BALANCE

            AccountSteps.deposit_money_on_account(
                user_spec,
                account_id,
                AccountTestData.SMALL_SENDER_BALANCE,
                expected_balance
            )

    @staticmethod
    def prepare_account_with_small_balance(
        user_spec: dict,
        account_id: int
    ) -> None:
        AccountSteps.deposit_money_on_account(
            user_spec,
            account_id,
            AccountTestData.SMALL_SENDER_BALANCE,
            AccountTestData.SMALL_SENDER_BALANCE
        )