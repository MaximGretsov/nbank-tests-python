import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.user_dashboard import UserDashboard
from src.main.ui.pages.bank_alert import BankAlert


@pytest.mark.ui
class TestCreateAccount:

    @pytest.mark.user_session(10)
    def test_user_can_create_account(
        self,
        api_manager: ApiManager,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict
    ):
        dashboard_page = UserDashboard(page).open()
        expect(dashboard_page.welcome_text).to_be_visible()

        dashboard_page.perform_action_and_check_alert(
            dashboard_page.create_new_account,
            BankAlert.NEW_ACCOUNT_CREATED.value
        )

        user_accounts = api_manager.account_steps.get_accounts(user_spec)

        assert len(user_accounts) == 1
        assert user_accounts[0].balance == 0