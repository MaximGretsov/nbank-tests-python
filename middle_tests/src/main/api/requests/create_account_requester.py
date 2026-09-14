import requests
from requests import Response

from middle_tests.src.main.api.requests.requester import Requester


class CreateAccountRequester(Requester):
    def post(self) -> Response:
        url = f'{self.base_url}/accounts'
        response = requests.post(url=url, headers=self.headers)
        self.response_spec(response)
        return response