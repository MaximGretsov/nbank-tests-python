import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models.profile_update_request import ProfileUpdateRequest
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.testData.profile_test_data import ProfileTestData

from src.tests.api.iteration2.assertions.profile_assertions import ProfileAssertions


@pytest.mark.api
class TestChangeNameInProfile:

    def test_user_can_change_name(
        self,
        api_manager,
        user_spec
    ):
        profile_update_request = ProfileUpdateRequest(
            name=RandomData.generate_valid_profile_name()
        )

        api_manager.profile_steps.update_profile(
            user_spec,
            profile_update_request
        )

        ProfileAssertions.assert_profile_name(
            api_manager,
            user_spec,
            profile_update_request.name
        )

    @pytest.mark.parametrize(
        "invalid_name",
        [
            RandomData.generate_single_word_profile_name(),
            RandomData.generate_three_word_profile_name(),
            RandomData.generate_empty_profile_name(),
            RandomData.generate_profile_name_with_leading_space(),
            RandomData.generate_profile_name_with_trailing_space(),
            RandomData.generate_only_spaces_profile_name(),
            RandomData.generate_profile_name_with_special_character(),
            RandomData.generate_profile_name_with_digit(),
            RandomData.generate_profile_name_with_hyphen(),
            RandomData.generate_profile_name_with_double_space(),
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
            "double space",
        ]
    )
    def test_user_cannot_change_name_with_wrong_data(
        self,
        api_manager,
        user_spec,
        invalid_name
    ):
        profile_update_request = ProfileUpdateRequest(
            name=invalid_name
        )

        CrudRequester(
            request_spec=user_spec,
            endpoint=Endpoint.UPDATE_CUSTOMER_PROFILE,
            response_spec=ResponseSpecs.profile_name_validation_error()
        ).update(profile_update_request)

        ProfileAssertions.assert_profile_name(
            api_manager,
            user_spec,
            ProfileTestData.DEFAULT_PROFILE_NAME
        )

    def test_user_cannot_change_name_with_wrong_authorization_token(
        self,
        api_manager,
        user_spec
    ):
        profile_update_request = ProfileUpdateRequest(
            name=RandomData.generate_valid_profile_name()
        )

        CrudRequester(
            request_spec=RequestSpecs.broken_auth_spec(),
            endpoint=Endpoint.UPDATE_CUSTOMER_PROFILE,
            response_spec=ResponseSpecs.unauthorized()
        ).update(profile_update_request)

        ProfileAssertions.assert_profile_name(
            api_manager,
            user_spec,
            ProfileTestData.DEFAULT_PROFILE_NAME
        )

    def test_user_cannot_change_name_without_authorization(
        self,
        api_manager,
        user_spec
    ):
        profile_update_request = ProfileUpdateRequest(
            name=RandomData.generate_valid_profile_name()
        )

        CrudRequester(
            request_spec=RequestSpecs.unauth_spec(),
            endpoint=Endpoint.UPDATE_CUSTOMER_PROFILE,
            response_spec=ResponseSpecs.unauthorized()
        ).update(profile_update_request)

        ProfileAssertions.assert_profile_name(
            api_manager,
            user_spec,
            ProfileTestData.DEFAULT_PROFILE_NAME
        )
