from typing import Any, Dict, Optional, List

from middle_tests.src.main.api.models.account_response import AccountResponse
from middle_tests.src.main.api.models.base_model import BaseModel
from middle_tests.src.main.api.models.user_role import UserRole

class CreateUserResponse(BaseModel):
    id:int
    username:str
    password:str
    name:Optional[str]
    role:UserRole
    accounts:List[AccountResponse]
    