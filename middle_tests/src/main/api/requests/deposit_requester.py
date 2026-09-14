import requests
from requests import Response

from middle_tests.src.main.api.requests.requester import Requester
from middle_tests.src.main.api.models.deposit_request import DepositRequest


class DepositRequester(Requester):
    def post(self, deposit_request: DepositRequest) -> Response:
        url = f'{self.base_url}/accounts/deposit'
        response = requests.post(
            url=url,
            json=deposit_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        return response