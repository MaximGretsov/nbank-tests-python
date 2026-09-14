import pytest

from middle_tests.src.main.api.requests.steps.account_steps import AccountSteps
from middle_tests.src.main.api.testData.account_test_data import AccountTestData


class AccountAssertions:
    @staticmethod
    def assert_account_balance(
        user_spec: dict,
        account_id: int,
        expected_balance: float
    ) -> None:
        account = AccountSteps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account.balance == pytest.approx(
            expected_balance,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        ), (
            f"Unexpected balance for account {account_id}: "
            f"expected {expected_balance}, got {account.balance}"
        )