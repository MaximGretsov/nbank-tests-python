from middle_tests.src.main.api.generators.random_data import RandomData
from middle_tests.src.main.api.models.create_user_request import CreateUserRequest
from middle_tests.src.main.api.models.user_role import UserRole
from middle_tests.src.main.api.requests.admin_user_requester import AdminUserRequester
from middle_tests.src.main.api.specs.request_specs import RequestSpecs
from middle_tests.src.main.api.specs.response_specs import ResponseSpecs


class AdminSteps:
    @staticmethod
    def create_user() -> tuple[CreateUserRequest, int]:
        user_request = CreateUserRequest(
            username=RandomData.generate_username(),
            password=RandomData.generate_password(),
            role=UserRole.USER
        )

        response = AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.entity_was_created()
        ).post(user_request)

        user_id = response.json()["id"]

        return user_request, user_id

    @staticmethod
    def delete_user(user_id: int) -> None:
        AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.entity_was_deleted()
        ).delete(user_id)