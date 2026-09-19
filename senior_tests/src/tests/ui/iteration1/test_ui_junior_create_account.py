import re

import pytest
from playwright.sync_api import Page, expect

from src.main.api.models.account_response import AccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.validated_crud_requester import (
    ValidatedCrudRequester
)
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.tests.ui.base_ui_test import BaseUITest


@pytest.mark.ui
class TestCreateAccount(BaseUITest):

    def test_user_can_create_account(
        self,
        page: Page,
        user_request: CreateUserRequest
    ):
        page.set_viewport_size({"width": 1920, "height": 1080})

        # ШАГ 1: пользователь логинится
        page.goto(
            f"{self.UI_BASE_URL}/login",
            wait_until="domcontentloaded"
        )

        page.get_by_placeholder("Username").fill(
            user_request.username
        )

        page.get_by_placeholder("Password").fill(
            user_request.password
        )

        page.get_by_role(
            "button",
            name="Login"
        ).click()

        expect(
            page.get_by_text("User Dashboard")
        ).to_be_visible()

        # ШАГ 2: создаём счёт и ждём dialog
        page.on(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with page.expect_event("dialog") as dialog_info:
            page.get_by_role(
                "button",
                name="➕ Create New Account"
            ).click()

        dialog = dialog_info.value

        # ШАГ 3: проверяем dialog
        assert (
            "✅ New Account Created! Account Number:"
            in dialog.message
        )

        matcher = re.search(
            r"Account Number: (\w+)",
            dialog.message
        )

        assert matcher is not None

        created_account_number = matcher.group(1)

        # ШАГ 4: проверяем созданный счёт через API
        user_accounts: list[AccountResponse] = ValidatedCrudRequester(
            request_spec=RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password
            ),
            endpoint=Endpoint.GET_CUSTOMER_ACCOUNTS,
            response_spec=ResponseSpecs.request_returns_ok()
        ).get()

        created_account = next(
            (
                account
                for account in user_accounts
                if account.accountNumber == created_account_number
            ),
            None
        )

        assert created_account is not None
        assert created_account.balance == 0