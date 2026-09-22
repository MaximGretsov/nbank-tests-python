from middle_tests.src.main.api.requests.steps.profile_steps import ProfileSteps


class ProfileAssertions:
    @staticmethod
    def assert_profile_name(
        user_spec: dict,
        expected_name: str | None
    ) -> None:
        profile = ProfileSteps.get_profile(user_spec)

        assert profile.name == expected_name, (
            f"Expected profile name '{expected_name}', "
            f"but got '{profile.name}'"
        )