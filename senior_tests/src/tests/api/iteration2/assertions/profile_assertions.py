import pytest

from src.main.api.classes.api_manager import ApiManager


class ProfileAssertions:

    @staticmethod
    def assert_profile_name(
        api_manager: ApiManager,
        user_spec: dict,
        expected_name: str | None
    ) -> None:
        profile = api_manager.profile_steps.get_profile(user_spec)

        assert profile.name == expected_name, (
            f"Expected profile name: {expected_name}, "
            f"but actual name: {profile.name}"
        )