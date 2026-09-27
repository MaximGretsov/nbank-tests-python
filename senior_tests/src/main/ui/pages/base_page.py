from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, List, Type, TypeVar

from playwright.sync_api import Dialog, Locator, Page

from src.main.api.configs.config import Config
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs


T = TypeVar("T", bound="BasePage")
E = TypeVar("E")


class BasePage(ABC):
    def __init__(self, page: Page):
        self.page = page
        self.base_url = str(Config.get("UI_BASE_URL", "http://localhost:3000")).rstrip("/")

    @property
    def username_input(self):
        return self.page.get_by_placeholder("Username")

    @property
    def password_input(self):
        return self.page.get_by_placeholder("Password")

    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    def open(self: T) -> T:
        target = self.url()

        if self.base_url and target.startswith("/"):
            target = f"{self.base_url}{target}"

        self.page.goto(target, wait_until="domcontentloaded")
        return self

    def get_page(self, page_cls: Type[T]) -> T:
        return page_cls(self.page)

    def check_alert_message_and_accept(self: T, expected_text: str) -> T:
        def _handler(dialog: Dialog) -> None:
            assert expected_text in dialog.message, f"Alert text mismatch: {dialog.message!r}"
            dialog.accept()

        self.page.once("dialog", _handler)
        return self

    def perform_action_and_check_alert(
        self: T,
        action: Callable[[], object],
        expected_text: str
    ) -> T:
        self.page.once("dialog", lambda dialog: dialog.accept())

        with self.page.expect_event("dialog") as dialog_info:
            action()

        dialog = dialog_info.value

        assert expected_text in dialog.message, f"Alert text mismatch: {dialog.message!r}"
        return self

    def auth_as_user(self: T, user_request: CreateUserRequest) -> None:
        auth_token = RequestSpecs.auth_as_user(
            user_request.username,
            user_request.password
        ).get("Authorization")

        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        self.page.evaluate(
            'token => localStorage.setItem("authToken", token)',
            auth_token
        )

    def _generate_page_elements(
        self,
        elements: Locator,
        constructor: Callable[[Locator], E]
    ) -> List[E]:
        elements.first.wait_for(state="attached", timeout=10_000)

        return [
            constructor(elements.nth(i))
            for i in range(elements.count())
        ]