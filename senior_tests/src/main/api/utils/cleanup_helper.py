import logging
from typing import Any, List

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.classes.api_manager import ApiManager


def cleanup_objects(objects: List[Any]):
    api_manager = ApiManager(objects)
    for obj in objects:
        if isinstance(obj, CreateUserRequest):
            user_profile = api_manager.user_steps.get_profile(obj)
            api_manager.admin_steps.delete_user(user_profile.id)
        elif isinstance(obj, CreateUserResponse):
            api_manager.admin_steps.delete_user(obj.id)
        else:
            logging.warning(f'Object type: {type(obj)} is not deleted')