from dataclasses import dataclass
from enum import Enum
from typing import List

from src.main.api.models.account_response import AccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.models.profile_update_request import ProfileUpdateRequest
from src.main.api.models.customer_profile_response import CustomerProfileResponse
from src.main.api.models.base_model import BaseModel


@dataclass(frozen=True)
class EndpointConfig:
    url: str
    request_model: BaseModel
    response_model: BaseModel


class Endpoint(Enum):
    ADMIN_CREATE_USER = EndpointConfig(
        url='/admin/users',
        request_model=CreateUserRequest,
        response_model=CreateUserResponse
    )
    
    ADMIN_DELETE_USER = EndpointConfig(
        url='/admin/users',
        request_model=None,
        response_model=None
    )
    
    ADMIN_GET_ALL_USERS = EndpointConfig(
        url='/admin/users',
        request_model=None,
        response_model=List[CreateUserRequest]
    )
    
    LOGIN_USER = EndpointConfig(
        url='/auth/login',
        request_model=LoginUserRequest,
        response_model=LoginUserResponse
    )
    
    CREATE_ACCOUNT = EndpointConfig(
        url='/accounts',
        request_model=None,
        response_model=AccountResponse
    )

    GET_CUSTOMER_ACCOUNTS = EndpointConfig(
        url='/customer/accounts',
        request_model=None,
        response_model=List[AccountResponse]
    )

    DEPOSIT = EndpointConfig(
        url='/accounts/deposit',
        request_model=DepositRequest,
        response_model=AccountResponse
    )

    TRANSFER = EndpointConfig(
        url='/accounts/transfer',
        request_model=TransferRequest,
        response_model=TransferResponse
    )

    GET_CUSTOMER_PROFILE = EndpointConfig(
        url='/customer/profile',
        request_model=None,
        response_model=CustomerProfileResponse
    )

    UPDATE_CUSTOMER_PROFILE = EndpointConfig(
        url='/customer/profile',
        request_model=ProfileUpdateRequest,
        response_model=CustomerProfileResponse
    )