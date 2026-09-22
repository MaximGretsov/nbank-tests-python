import pytest

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.specs.request_specs import RequestSpecs


@pytest.fixture(scope='function')
def user_request(api_manager: ApiManager):
    user_data: CreateUserRequest = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_data)
    return user_data


@pytest.fixture
def admin_user_request():
    return CreateUserRequest(username='admin', password='admin', role='ADMIN')

@pytest.fixture
def user_spec(user_request):
    return RequestSpecs.auth_as_user(
        user_request.username,
        user_request.password
    )

@pytest.fixture
def second_user_request(api_manager: ApiManager):
    user_data: CreateUserRequest = RandomModelGenerator.generate(
        CreateUserRequest
    )

    api_manager.admin_steps.create_user(user_data)

    return user_data


@pytest.fixture
def second_user_spec(second_user_request):
    return RequestSpecs.auth_as_user(
        second_user_request.username,
        second_user_request.password
    )