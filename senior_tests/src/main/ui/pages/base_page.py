from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Type, TypeVar

from playwright.sync_api import Dialog, Page

from src.main.api.configs.config import Config


T = TypeVar("T", bound="BasePage")


class BasePage(ABC):

    def __init__(self, page: Page):
        self.page = page
        self.base_url = str(
            Config.get(
                "UI_BASE_URL",
                "http://localhost:3000"
            )
        ).rstrip("/")

    @property
    def username_input(self):
        return self.page.get_by_placeholder(
            "Username"
        )

    @property
    def password_input(self):
        return self.page.get_by_placeholder(
            "Password"
        )

    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    def open(self: T) -> T:
        target = self.url()

        if self.base_url and target.startswith("/"):
            target = f"{self.base_url}{target}"

        self.page.goto(
            target,
            wait_until="domcontentloaded"
        )

        return self

    def get_page(
        self,
        page_cls: Type[T]
    ) -> T:
        return page_cls(self.page)

    def check_alert_message_and_accept(
        self: T,
        expected_text: str
    ) -> T:

        def _handler(dialog: Dialog) -> None:
            assert expected_text in dialog.message, (
                f"Alert text mismatch: "
                f"{dialog.message!r}"
            )

            dialog.accept()

        self.page.once(
            "dialog",
            _handler
        )

        return self

    def perform_action_and_check_alert(
        self: T,
        action: Callable[[], object],
        expected_text: str
    ) -> T:

        self.page.once(
            "dialog",
            lambda dialog: dialog.accept()
        )

        with self.page.expect_event(
            "dialog"
        ) as dialog_info:
            action()

        dialog = dialog_info.value

        assert expected_text in dialog.message, (
            f"Alert text mismatch: "
            f"{dialog.message!r}"
        )

        return self