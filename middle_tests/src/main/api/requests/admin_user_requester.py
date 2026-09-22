import requests
from requests import Response

from middle_tests.src.main.api.requests.requester import Requester
from middle_tests.src.main.api.models.create_user_request import CreateUserRequest


class AdminUserRequester(Requester):
    def post(self, create_user_request: CreateUserRequest) -> Response:
        url = f'{self.base_url}/admin/users'
        response = requests.post(
            url=url,
            json=create_user_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        return response

    def delete(self, user_id: int) -> Response:
        url = f'{self.base_url}/admin/users/{user_id}'
        response = requests.delete(url=url, headers=self.headers)
        self.response_spec(response)
        return response