from typing import Optional

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.validated_crud_requester import (
    ValidatedCrudRequester
)
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.steps.base_steps import BaseSteps
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


class AdminSteps(BaseSteps):

    def create_user(
        self,
        user_request: Optional[CreateUserRequest] = None
    ) -> CreateUserRequest:

        if user_request is None:
            user_request = RandomModelGenerator.generate(
                CreateUserRequest
            )

        user_response = ValidatedCrudRequester(
            request_spec=RequestSpecs.admin_auth_spec(),
            endpoint=Endpoint.ADMIN_CREATE_USER,
            response_spec=ResponseSpecs.entity_was_created()
        ).post(user_request)

        self.created_objects.append(user_response)

        return user_request

    def create_invalid_user(
        self,
        create_user_request: CreateUserRequest,
        error_key: str,
        error_value: str
    ):
        return CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_returns_bad_request(
                error_key,
                error_value
            )
        ).post(create_user_request)

    def login(
        self,
        login_user_request: LoginUserRequest = LoginUserRequest(
            username="admin",
            password="admin"
        )
    ):
        return ValidatedCrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.LOGIN_USER,
            ResponseSpecs.request_returns_ok()
        ).post(login_user_request)

    def get_all_users(self) -> list[CreateUserResponse]:
        return ValidatedCrudRequester(
            request_spec=RequestSpecs.admin_auth_spec(),
            endpoint=Endpoint.ADMIN_GET_ALL_USERS,
            response_spec=ResponseSpecs.request_returns_ok()
        ).get()

    def delete_user(self, id: int):
        return CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_DELETE_USER,
            ResponseSpecs.entity_was_deleted()
        ).delete(id)