from middle_tests.src.main.api.requests.steps.admin_steps import AdminSteps
from middle_tests.src.main.api.specs.request_specs import RequestSpecs


class UserSteps:
    @staticmethod
    def create_user_and_get_auth_spec() -> tuple[int, dict]:
        user_request, user_id = AdminSteps.create_user()

        user_spec = RequestSpecs.auth_as_user(
            user_request.username,
            user_request.password
        )

        return user_id, user_spec