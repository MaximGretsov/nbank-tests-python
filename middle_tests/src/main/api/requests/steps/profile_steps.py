from middle_tests.src.main.api.models.customer_profile_response import CustomerProfileResponse
from middle_tests.src.main.api.requests.customer_profile_requester import CustomerProfileRequester
from middle_tests.src.main.api.specs.response_specs import ResponseSpecs


class ProfileSteps:
    @staticmethod
    def get_profile(user_spec: dict) -> CustomerProfileResponse:
        response = CustomerProfileRequester(
            user_spec,
            ResponseSpecs.request_returns_ok()
        ).get()

        return CustomerProfileResponse(**response.json())