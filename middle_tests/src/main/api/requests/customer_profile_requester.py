import requests
from requests import Response

from middle_tests.src.main.api.requests.requester import Requester
from middle_tests.src.main.api.models.profile_update_request import ProfileUpdateRequest


class CustomerProfileRequester(Requester):
    def get(self) -> Response:
        url = f'{self.base_url}/customer/profile'
        response = requests.get(
            url=url,
            headers=self.headers
        )
        self.response_spec(response)
        return response

    def put(self, profile_update_request: ProfileUpdateRequest) -> Response:
        url = f'{self.base_url}/customer/profile'
        response = requests.put(
            url=url,
            json=profile_update_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        return response