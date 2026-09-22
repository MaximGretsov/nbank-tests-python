from typing import List

from middle_tests.src.main.api.models.account_response import AccountResponse
from middle_tests.src.main.api.models.base_model import BaseModel
from middle_tests.src.main.api.models.user_role import UserRole

class CustomerProfileResponse(BaseModel):
    id:int
    username:str
    name:str | None
    password:str
    role:UserRole
    accounts:List[AccountResponse]