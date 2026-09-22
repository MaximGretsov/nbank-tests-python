import pytest

from middle_tests.src.main.api.generators.random_data import RandomData
from middle_tests.src.main.api.models.profile_update_request import ProfileUpdateRequest
from middle_tests.src.main.api.requests.customer_profile_requester import CustomerProfileRequester
from middle_tests.src.main.api.requests.steps.admin_steps import AdminSteps
from middle_tests.src.main.api.requests.steps.user_steps import UserSteps
from middle_tests.src.main.api.specs.request_specs import RequestSpecs
from middle_tests.src.main.api.specs.response_specs import ResponseSpecs
from middle_tests.src.main.api.testData.profile_test_data import ProfileTestData

from middle_tests.src.tests.iteration2.assertions.profile_assertions import ProfileAssertions


@pytest.mark.api
class TestChangeNameInProfile:

    def test_user_can_update_name_with_two_words_and_letters_only(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        new_name = RandomData.generate_valid_profile_name()

        profile_update_request = ProfileUpdateRequest(
            name=new_name
        )

        CustomerProfileRequester(
            user_spec,
            ResponseSpecs.success_profile_update_response(new_name)
        ).put(profile_update_request)

        ProfileAssertions.assert_profile_name(
            user_spec,
            new_name
        )

        AdminSteps.delete_user(user_id)

    @pytest.mark.parametrize(
        "new_name",
        [
            RandomData.generate_single_word_profile_name(),
            RandomData.generate_three_word_profile_name(),
            "",
            RandomData.generate_profile_name_with_leading_space(),
            RandomData.generate_profile_name_with_trailing_space(),
            RandomData.generate_only_spaces_profile_name(),
            RandomData.generate_profile_name_with_special_character(),
            RandomData.generate_profile_name_with_digit(),
            RandomData.generate_profile_name_with_hyphen(),
            RandomData.generate_profile_name_with_double_space()
        ],
        ids=[
            "one word",
            "three words",
            "empty name",
            "leading space",
            "trailing space",
            "only spaces",
            "special character",
            "digit",
            "hyphen",
            "double space"
        ]
    )
    def test_user_cannot_change_name_with_wrong_data(
        self,
        new_name
    ):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        profile_update_request = ProfileUpdateRequest(
            name=new_name
        )

        CustomerProfileRequester(
            user_spec,
            ResponseSpecs.profile_name_validation_error()
        ).put(profile_update_request)

        ProfileAssertions.assert_profile_name(
            user_spec,
            ProfileTestData.DEFAULT_PROFILE_NAME
        )

        AdminSteps.delete_user(user_id)

    def test_user_cannot_change_name_with_wrong_authorization_token(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        new_name = RandomData.generate_valid_profile_name()

        profile_update_request = ProfileUpdateRequest(
            name=new_name
        )

        CustomerProfileRequester(
            RequestSpecs.broken_auth_spec(),
            ResponseSpecs.unauthorized()
        ).put(profile_update_request)

        ProfileAssertions.assert_profile_name(
            user_spec,
            ProfileTestData.DEFAULT_PROFILE_NAME
        )

        AdminSteps.delete_user(user_id)

    def test_user_cannot_change_name_without_authorization(self):
        user_id, user_spec = UserSteps.create_user_and_get_auth_spec()

        new_name = RandomData.generate_valid_profile_name()

        profile_update_request = ProfileUpdateRequest(
            name=new_name
        )

        CustomerProfileRequester(
            RequestSpecs.unauth_spec(),
            ResponseSpecs.unauthorized()
        ).put(profile_update_request)

        ProfileAssertions.assert_profile_name(
            user_spec,
            ProfileTestData.DEFAULT_PROFILE_NAME
        )

        AdminSteps.delete_user(user_id)