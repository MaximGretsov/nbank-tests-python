import re

import pytest
from playwright.sync_api import Page, Dialog, expect

from src.main.api.models.create_user_request import CreateUserRequest
from src.tests.ui.base_ui_test import BaseUITest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.comparison.model_assertions import ModelAssertions

@pytest.mark.ui
class TestCreateUser(BaseUITest):
    def test_admin_can_create_user(
        self,
        page: Page,
        admin_user_request: CreateUserRequest,
        api_manager: ApiManager
    ):
        page.set_viewport_size({"width": 1920, "height": 1080})

        page.goto(
            f"{self.UI_BASE_URL}/login",
            wait_until="domcontentloaded"
        )

        page.get_by_placeholder("Username").fill(admin_user_request.username)
        page.get_by_placeholder("Password").fill(admin_user_request.password)
        page.get_by_role("button", name="Login").click()

        expect(page.get_by_text("Admin Panel")).to_be_visible()

        new_user_request: CreateUserRequest = RandomModelGenerator.generate(
            CreateUserRequest
        )

        page.get_by_placeholder("Username").fill(new_user_request.username)
        page.get_by_placeholder("Password").fill(new_user_request.password)

        def handle_create_user_dialog(dialog: Dialog):
            assert dialog.message == "✅ User created successfully!"
            dialog.accept()

        page.on(
            "dialog",
            lambda dialog: handle_create_user_dialog(dialog)
        )

        page.get_by_role("button", name="Add User").click()

        items = page.locator(
            "xpath=//*[text()='All Users']/..//li"
        )

        target = items.filter(
            has_text=re.compile(
                rf"^{re.escape(new_user_request.username)}(\s+|.*)USER$",
                re.IGNORECASE
            )
        )

        expect(target).to_be_visible()

        users = api_manager.admin_steps.get_all_users()

        created = [
        user
        for user in users
        if user.username == new_user_request.username
        ]

        assert len(created) == 1, (
            "Ожидался ровно один созданный пользователь в API"
        )

        ModelAssertions(
            new_user_request,
            created[0]
        ).match()

    def test_admin_cannot_create_user_with_invalid_data(
        self,
        page: Page,
        admin_user_request: CreateUserRequest,
        api_manager: ApiManager
    ):
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: админ логинится
        page.goto(
            f"{self.UI_BASE_URL}/login",
            wait_until="domcontentloaded"
        )

        page.get_by_placeholder("Username").fill(
            admin_user_request.username
        )
        page.get_by_placeholder("Password").fill(
            admin_user_request.password
        )
        page.get_by_role("button", name="Login").click()

        expect(
            page.get_by_text("Admin Panel")
        ).to_be_visible()

        # ШАГ 2: пытаемся создать пользователя
        # с невалидным username
        new_user_request: CreateUserRequest = (
            RandomModelGenerator.generate(CreateUserRequest)
        )

        new_user_request.username = "a"

        page.get_by_placeholder("Username").fill(
            new_user_request.username
        )
        page.get_by_placeholder("Password").fill(
            new_user_request.password
        )

        # ШАГ 3: проверяем alert
        def handle_create_invalid_user_dialog(dialog: Dialog):
            assert (
                "Username must be between 3 and 15 characters"
                in dialog.message
            )
            dialog.accept()

        page.on(
            "dialog",
            lambda dialog: handle_create_invalid_user_dialog(dialog)
        )

        page.get_by_role(
            "button",
            name="Add User"
        ).click()

        # ШАГ 4: пользователя не должно быть на UI
        items = page.locator(
            "xpath=//*[text()='All Users']/..//li"
        )

        target = items.filter(
            has_text=re.compile(
                rf"^{re.escape(new_user_request.username)}"
                rf"\s+USER$",
                re.IGNORECASE
            )
        )

        expect(target).to_have_count(0)

        # ШАГ 5: пользователя не должно быть в API
        users = api_manager.admin_steps.get_all_users()

        assert not any(
            user.username == new_user_request.username
            for user in users
        )