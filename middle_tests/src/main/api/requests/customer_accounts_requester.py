import requests
from requests import Response

from middle_tests.src.main.api.requests.requester import Requester


class CustomerAccountsRequester(Requester):
    def get(self) -> Response:
        url = f'{self.base_url}/customer/accounts'
        response = requests.get(url=url, headers=self.headers)
        self.response_spec(response)
        return response