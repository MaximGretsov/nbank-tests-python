from playwright.sync_api import Page

from src.main.api.configs.config import Config
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.models.create_user_request import CreateUserRequest


class BaseUITest:
    UI_BASE_URL = Config.get("UI_BASE_URL","http://localhost:3000")

    def auth_as_user(self, page: Page, user_request: CreateUserRequest) -> None:
        auth_token = RequestSpecs.auth_as_user(user_request.username,user_request.password).get("Authorization")

        page.set_viewport_size({"width": 1920,"height": 1080})

        page.goto(self.UI_BASE_URL, wait_until="domcontentloaded")

        page.evaluate('token => localStorage.setItem("authToken", token)', auth_token)