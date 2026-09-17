import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.testData.account_test_data import AccountTestData


class AccountAssertions:

    @staticmethod
    def assert_account_balance(
        api_manager: ApiManager,
        user_spec: dict,
        account_id: int,
        expected_balance: float
    ) -> None:
        account = api_manager.account_steps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account.balance == pytest.approx(
            expected_balance,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

    @staticmethod
    def assert_account_is_empty(
        api_manager: ApiManager,
        user_spec: dict,
        account_id: int
    ) -> None:
        account = api_manager.account_steps.get_account_by_id(
            user_spec,
            account_id
        )

        assert account.balance == pytest.approx(
            AccountTestData.EMPTY_ACCOUNT_BALANCE,
            abs=AccountTestData.FLOAT_ASSERTION_OFFSET
        )

        assert not account.transactions