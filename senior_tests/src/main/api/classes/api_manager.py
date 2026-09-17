from typing import Any, List

from src.main.api.requests.steps.admin_steps import AdminSteps
from src.main.api.requests.steps.user_steps import UserSteps
from src.main.api.requests.steps.account_steps import AccountSteps
from src.main.api.requests.steps.profile_steps import ProfileSteps


class ApiManager:
    def __init__(self, created_objects: List[Any]):
        self.admin_steps = AdminSteps(created_objects)
        self.user_steps = UserSteps(created_objects)
        self.account_steps = AccountSteps(created_objects)
        self.profile_steps = ProfileSteps(created_objects)