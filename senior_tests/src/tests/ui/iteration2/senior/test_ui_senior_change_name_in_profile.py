import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.user_dashboard import UserDashboard

from src.tests.api.iteration2.assertions.profile_assertions import ProfileAssertions


@pytest.mark.ui
@pytest.mark.user_session(1)
class TestChangeNameInProfile:

    def test_user_can_change_name_with_correct_data(
        self,
        page: Page,
        user_spec: dict,
        api_manager: ApiManager
    ):
        correct_new_name = RandomData.generate_valid_profile_name()

        edit_profile_page = (
            UserDashboard(page)
            .open()
            .open_edit_profile()
        )

        edit_profile_page.perform_action_and_check_alert(
            lambda: edit_profile_page.change_name(correct_new_name),
            BankAlert.PROFILE_UPDATED_SUCCESSFULLY.value
        )

        (
            edit_profile_page
            .open_user_dashboard()
            .check_displayed_name(correct_new_name)
        )

        ProfileAssertions.assert_profile_name(
            api_manager,
            user_spec,
            correct_new_name
        )

    def test_user_cannot_change_name_with_incorrect_data(
        self,
        page: Page,
        user_spec: dict,
        api_manager: ApiManager
    ):
        incorrect_new_name = RandomData.generate_single_word_profile_name()

        edit_profile_page = (
            UserDashboard(page)
            .open()
            .open_edit_profile()
        )

        edit_profile_page.perform_action_and_check_alert(
            lambda: edit_profile_page.change_name(incorrect_new_name),
            BankAlert.ENTER_VALID_NAME.value
        )

        (
            edit_profile_page
            .open_user_dashboard()
            .check_displayed_name(UserDashboard.DEFAULT_PROFILE_NAME)
        )

        ProfileAssertions.assert_profile_name(
            api_manager,
            user_spec,
            None
        )