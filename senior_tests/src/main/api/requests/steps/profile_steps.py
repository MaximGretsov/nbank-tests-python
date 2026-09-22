from src.main.api.models.customer_profile_response import CustomerProfileResponse
from src.main.api.models.profile_update_request import ProfileUpdateRequest
from src.main.api.models.comparison.model_assertions import ModelAssertions

from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.validated_crud_requester import (
    ValidatedCrudRequester
)
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.steps.base_steps import BaseSteps

from src.main.api.specs.response_specs import ResponseSpecs


class ProfileSteps(BaseSteps):

    def get_profile(
        self,
        user_spec: dict
    ) -> CustomerProfileResponse:
        return ValidatedCrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.GET_CUSTOMER_PROFILE,
            response_spec=ResponseSpecs.request_returns_ok()
        ).get()

    def update_profile(
        self,
        user_spec: dict,
        profile_update_request: ProfileUpdateRequest
    ) -> CustomerProfileResponse:

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.UPDATE_CUSTOMER_PROFILE,
            response_spec=ResponseSpecs.success_profile_update_response(
                profile_update_request.name
            )
        ).update(profile_update_request)

        profile_response = self.get_profile(user_spec)

        ModelAssertions(
            profile_update_request,
            profile_response
        ).match()

        return profile_response