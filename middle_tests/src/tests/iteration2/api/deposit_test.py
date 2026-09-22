import pytest

from middle_tests.src.main.api.generators.random_data import RandomData
from middle_tests.src.main.api.models.deposit_request import DepositRequest
from middle_tests.src.main.api.requests.deposit_requester import DepositRequester
from middle_tests.src.main.api.requests.steps.account_steps import AccountSteps
from middle_tests.src.main.api.requests.steps.admin_steps import AdminSteps
from middle_tests.src.main.api.requests.steps.user_steps import UserSteps
from middle_tests.src.main.api.specs.request_specs import RequestSpecs
from middle_tests.src.main.api.specs.response_specs import ResponseSpecs
from middle_tests.src.main.api.testData.account_test_data import AccountTestData


@pytest.mark.api
class TestDeposit:

    def test_user_can_deposit_with_random_correct_amount(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        amount = RandomData.generate_valid_deposit_amount()
        account_id = AccountSteps.create_account(user_spec)

        deposit_request = DepositRequest(
            id=account_id,
            balance=amount
        )

        DepositRequester(
            user_spec,
            ResponseSpecs.success_deposit_response(
                account_id,
                amount
            )
        ).post(deposit_request)

        account_after_deposit = AccountSteps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account_after_deposit.balance == pytest.approx(
            amount,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )
        assert account_after_deposit.transactions

        AdminSteps.delete_user(user_id)

    @pytest.mark.parametrize(
        "amount, expected_balance",
        [
            (0.01, 0.01),
            (4999.99, 4999.99),
            (5000.0, 5000.0)
        ],
        ids=[
            "min deposit",
            "below max deposit",
            "max deposit"
        ]
    )
    def test_user_can_deposit_with_boundary_correct_amount(
        self,
        amount,
        expected_balance
    ):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        account_id = AccountSteps.create_account(user_spec)

        deposit_request = DepositRequest(
            id=account_id,
            balance=amount
        )

        DepositRequester(
            user_spec,
            ResponseSpecs.success_deposit_response(
                account_id,
                expected_balance
            )
        ).post(deposit_request)

        account_after_deposit = AccountSteps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account_after_deposit.balance == pytest.approx(
            expected_balance,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )
        assert account_after_deposit.transactions

        AdminSteps.delete_user(user_id)

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
            )
        ],
        ids=[
            "zero deposit",
            "deposit above max"
        ]
    )
    def test_user_cannot_deposit_with_boundary_incorrect_amount(
        self,
        amount,
        response_spec
    ):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        account_id = AccountSteps.create_account(user_spec)

        deposit_request = DepositRequest(
            id=account_id,
            balance=amount
        )

        DepositRequester(
            user_spec,
            response_spec
        ).post(deposit_request)

        account_after_deposit = AccountSteps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account_after_deposit.balance == pytest.approx(
            AccountTestData.EMPTY_ACCOUNT_BALANCE,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )
        assert not account_after_deposit.transactions

        AdminSteps.delete_user(user_id)

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
            )
        ],
        ids=[
            "negative deposit",
            "random deposit above max"
        ]
    )
    def test_user_cannot_deposit_with_random_incorrect_amount(
        self,
        amount,
        response_spec
    ):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        account_id = AccountSteps.create_account(user_spec)

        deposit_request = DepositRequest(
            id=account_id,
            balance=amount
        )

        DepositRequester(
            user_spec,
            response_spec
        ).post(deposit_request)

        account_after_deposit = AccountSteps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account_after_deposit.balance == pytest.approx(
            AccountTestData.EMPTY_ACCOUNT_BALANCE,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )
        assert not account_after_deposit.transactions

        AdminSteps.delete_user(user_id)

    def test_user_cannot_deposit_with_non_existing_account(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        amount = RandomData.generate_valid_deposit_amount()
        account_id = AccountSteps.create_account(user_spec)

        non_existing_account_id = (
            RandomData.generate_non_existing_account_id_based(
                account_id
            )
        )

        deposit_request = DepositRequest(
            id=non_existing_account_id,
            balance=amount
        )

        DepositRequester(
            user_spec,
            ResponseSpecs.unauthorized_access_to_account()
        ).post(deposit_request)

        account_after_deposit = AccountSteps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account_after_deposit.balance == pytest.approx(
            AccountTestData.EMPTY_ACCOUNT_BALANCE,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )
        assert not account_after_deposit.transactions

        AdminSteps.delete_user(user_id)

    def test_user_cannot_deposit_to_another_user_account(self):
        user_id_1, user_spec_1 = UserSteps.create_user_and_get_auth_spec()
        user_id_2, user_spec_2 = UserSteps.create_user_and_get_auth_spec()

        amount = RandomData.generate_valid_deposit_amount()

        account_id_2 = AccountSteps.create_account(user_spec_2)

        deposit_request = DepositRequest(
            id=account_id_2,
            balance=amount
        )

        DepositRequester(
            user_spec_1,
            ResponseSpecs.unauthorized_access_to_account()
        ).post(deposit_request)

        account_after_deposit = AccountSteps.get_account_by_id(
            user_spec_2,
            account_id_2
        )

        assert account_after_deposit.balance == pytest.approx(
            AccountTestData.EMPTY_ACCOUNT_BALANCE,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )
        assert not account_after_deposit.transactions

        AdminSteps.delete_user(user_id_1)
        AdminSteps.delete_user(user_id_2)

    def test_user_cannot_deposit_with_wrong_authorization_token(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        amount = RandomData.generate_valid_deposit_amount()
        account_id = AccountSteps.create_account(user_spec)

        deposit_request = DepositRequest(
            id=account_id,
            balance=amount
        )

        DepositRequester(
            RequestSpecs.broken_auth_spec(),
            ResponseSpecs.unauthorized()
        ).post(deposit_request)

        account_after_deposit = AccountSteps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account_after_deposit.balance == pytest.approx(
            AccountTestData.EMPTY_ACCOUNT_BALANCE,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )
        assert not account_after_deposit.transactions

        AdminSteps.delete_user(user_id)

    def test_user_cannot_deposit_without_authorization(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        amount = RandomData.generate_valid_deposit_amount()
        account_id = AccountSteps.create_account(user_spec)

        deposit_request = DepositRequest(
            id=account_id,
            balance=amount
        )

        DepositRequester(
            RequestSpecs.unauth_spec(),
            ResponseSpecs.unauthorized()
        ).post(deposit_request)

        account_after_deposit = AccountSteps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account_after_deposit.balance == pytest.approx(
            AccountTestData.EMPTY_ACCOUNT_BALANCE,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )
        assert not account_after_deposit.transactions

        AdminSteps.delete_user(user_id)