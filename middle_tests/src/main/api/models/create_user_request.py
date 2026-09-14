from middle_tests.src.main.api.models.base_model import BaseModel

from middle_tests.src.main.api.models.user_role import UserRole

class CreateUserRequest(BaseModel):
    username:str
    password:str
    role:UserRole