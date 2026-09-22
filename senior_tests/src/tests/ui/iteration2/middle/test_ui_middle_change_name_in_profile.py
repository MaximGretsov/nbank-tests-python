import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest

from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.user_dashboard import UserDashboard

from src.tests.api.iteration2.assertions.profile_assertions import (
    ProfileAssertions
)
from src.tests.ui.base_ui_test import BaseUITest


@pytest.mark.ui
class TestChangeNameInProfile(BaseUITest):

    def test_user_can_change_name_with_correct_data(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        correct_new_name = (
            RandomData.generate_valid_profile_name()
        )

        # ШАГ 1: авторизуем пользователя
        self.auth_as_user(
            page,
            user_request
        )

        # ШАГ 2: открываем редактирование профиля
        edit_profile_page = (
            UserDashboard(page)
            .open()
            .open_edit_profile()
        )

        # ШАГ 3: заранее подписываемся на alert
        edit_profile_page.check_alert_message_and_accept(
            BankAlert.PROFILE_UPDATED_SUCCESSFULLY.value
        )

        # ШАГ 4: меняем имя
        edit_profile_page.change_name(
            correct_new_name
        )

        # ШАГ 5: проверяем имя на UI
        (
            edit_profile_page
            .open_user_dashboard()
            .check_displayed_name(
                correct_new_name
            )
        )

        # ШАГ 6: проверяем имя через API
        ProfileAssertions.assert_profile_name(
            api_manager,
            user_spec,
            correct_new_name
        )

    def test_user_cannot_change_name_with_incorrect_data(
        self,
        page: Page,
        user_request: CreateUserRequest,
        user_spec: dict,
        api_manager: ApiManager
    ):
        incorrect_new_name = (
            RandomData.generate_single_word_profile_name()
        )

        # ШАГ 1: авторизуем пользователя
        self.auth_as_user(
            page,
            user_request
        )

        # ШАГ 2: открываем редактирование профиля
        edit_profile_page = (
            UserDashboard(page)
            .open()
            .open_edit_profile()
        )

        # ШАГ 3: заранее подписываемся на alert
        edit_profile_page.check_alert_message_and_accept(
            BankAlert.ENTER_VALID_NAME.value
        )

        # ШАГ 4: пытаемся изменить имя
        edit_profile_page.change_name(
            incorrect_new_name
        )

        # ШАГ 5: имя на UI не изменилось
        (
            edit_profile_page
            .open_user_dashboard()
            .check_displayed_name(
                UserDashboard.DEFAULT_PROFILE_NAME
            )
        )

        # ШАГ 6: имя в API не изменилось
        ProfileAssertions.assert_profile_name(
            api_manager,
            user_spec,
            None
        )