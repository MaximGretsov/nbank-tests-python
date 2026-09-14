import requests
from requests import Response

from middle_tests.src.main.api.requests.requester import Requester
from middle_tests.src.main.api.models.transfer_request import TransferRequest


class TransferRequester(Requester):
    def post(self, transfer_request: TransferRequest) -> Response:
        url = f'{self.base_url}/accounts/transfer'
        response = requests.post(
            url=url,
            json=transfer_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        return response