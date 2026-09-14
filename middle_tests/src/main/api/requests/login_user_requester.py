import requests
from requests import Response

from middle_tests.src.main.api.requests.requester import Requester
from middle_tests.src.main.api.models.login_user_request import LoginUserRequest


class LoginUserRequester(Requester):
    def post(self, login_user_request: LoginUserRequest) -> Response:
        url = f'{self.base_url}/auth/login'
        response = requests.post(
            url=url,
            json=login_user_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        return response