import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.admin_panel import AdminPanel
from src.main.ui.pages.bank_alert import BankAlert


@pytest.mark.ui
class TestCreateUser:

    @pytest.mark.admin_session
    def test_admin_can_create_user(
        self,
        page: Page,
        api_manager: ApiManager,
        created_objects: list
    ):
        new_user_request = RandomModelGenerator.generate(CreateUserRequest)

        admin_page = AdminPanel(page).open()
        expect(admin_page.admin_panel_text).to_be_visible()

        admin_page.perform_action_and_check_alert(
            lambda: admin_page.create_user(
                new_user_request.username,
                new_user_request.password
            ),
            BankAlert.USER_CREATED_SUCCESSFULLY.value
        )

        admin_page.wait_for_username(new_user_request.username)

        created_user = next(
            user
            for user in api_manager.admin_steps.get_all_users()
            if user.username == new_user_request.username
        )

        created_objects.append(created_user)

        ModelAssertions(
            new_user_request,
            created_user
        ).match()

    @pytest.mark.admin_session
    @pytest.mark.parametrize(
        "new_user_request",
        [RandomModelGenerator.generate(CreateUserRequest)]
    )
    def test_admin_cannot_create_user_with_invalid_data(
        self,
        page: Page,
        api_manager: ApiManager,
        new_user_request: CreateUserRequest
    ):
        new_user_request.username = "a"

        admin_page = AdminPanel(page).open()
        expect(admin_page.admin_panel_text).to_be_visible()

        admin_page.perform_action_and_check_alert(
            lambda: admin_page.create_user(
                new_user_request.username,
                new_user_request.password
            ),
            BankAlert.USERNAME_MUST_BE_BETWEEN_3_AND_15_CHARACTERS.value
        )

        assert not any(
            user.username == new_user_request.username
            for user in admin_page.get_all_users()
        )

        assert not any(
            user.username == new_user_request.username
            for user in api_manager.admin_steps.get_all_users()
        )