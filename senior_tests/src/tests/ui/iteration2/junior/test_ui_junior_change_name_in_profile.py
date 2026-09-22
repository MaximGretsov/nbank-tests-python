import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest

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
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: получаем токен пользователя через API
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

        # ШАГ 2: авторизуем пользователя на UI через localStorage
        page.goto(
            self.UI_BASE_URL,
            wait_until="domcontentloaded"
        )

        page.evaluate(
            "(token) => localStorage.setItem('authToken', token)",
            auth_token
        )

        # ШАГ 3: открываем dashboard
        page.goto(
            f"{self.UI_BASE_URL}/dashboard",
            wait_until="domcontentloaded"
        )

        # ШАГ 4: открываем профиль
        user_info = page.locator(".user-info")

        expect(user_info).to_be_visible()

        user_info.click()

        # ШАГ 5: вводим корректное новое имя
        correct_new_name = (
            RandomData.generate_valid_profile_name()
        )

        page.get_by_placeholder(
            "Enter new name"
        ).fill(correct_new_name)

        # ШАГ 6: сохраняем и ждём alert
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            page.get_by_role(
                "button",
                name="Save Changes"
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == "✅ Name updated successfully!"
        )

        # ШАГ 7: проверяем имя на UI
        page.get_by_role(
            "button",
            name="Home"
        ).click()

        expect(
            page.locator(".welcome-text span")
        ).to_have_text(correct_new_name)

        # ШАГ 8: проверяем имя через API
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
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: получаем токен пользователя через API
        login_response = api_manager.user_steps.login(
            user_request
        )

        auth_token = login_response.headers.get(
            "Authorization"
        )

        # ШАГ 2: авторизуем пользователя на UI через localStorage
        page.goto(
            self.UI_BASE_URL,
            wait_until="domcontentloaded"
        )

        page.evaluate(
            "(token) => localStorage.setItem('authToken', token)",
            auth_token
        )

        # ШАГ 3: открываем dashboard
        page.goto(
            f"{self.UI_BASE_URL}/dashboard",
            wait_until="domcontentloaded"
        )

        # ШАГ 4: открываем профиль
        user_info = page.locator(".user-info")

        expect(user_info).to_be_visible()

        user_info.click()

        # ШАГ 5: вводим невалидное имя
        incorrect_new_name = (
            RandomData.generate_single_word_profile_name()
        )

        page.get_by_placeholder(
            "Enter new name"
        ).fill(incorrect_new_name)

        # ШАГ 6: сохраняем и ждём alert
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            page.get_by_role(
                "button",
                name="Save Changes"
            ).click()

        dialog = dialog_info.value

        assert (
            dialog.message
            == "Name must contain two words with letters only"
        )

        # ШАГ 7: имя на UI не изменилось
        page.get_by_role(
            "button",
            name="Home"
        ).click()

        expect(
            page.locator(".welcome-text span")
        ).to_have_text("noname")

        # ШАГ 8: имя на API не изменилось
        ProfileAssertions.assert_profile_name(
            api_manager,
            user_spec,
            None
        )