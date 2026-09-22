from src.main.ui.pages.base_page import BasePage


class EditProfilePage(BasePage):

    @property
    def new_name_input(self):
        return self.page.get_by_placeholder(
            "Enter new name"
        )

    @property
    def save_changes_button(self):
        return self.page.get_by_role(
            "button",
            name="Save Changes"
        )

    @property
    def home_button(self):
        return self.page.get_by_role(
            "button",
            name="Home"
        )

    def url(self) -> str:
        return "/edit-profile"

    def change_name(
        self,
        new_name: str
    ):
        self.new_name_input.fill(new_name)
        self.save_changes_button.click()

        return self

    def open_user_dashboard(self):
        from src.main.ui.pages.user_dashboard import (
            UserDashboard
        )

        self.home_button.click()

        return UserDashboard(self.page)