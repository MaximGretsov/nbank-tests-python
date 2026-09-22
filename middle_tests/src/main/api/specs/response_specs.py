from typing import Callable
from http import HTTPStatus

from requests import Response
import pytest


class ResponseSpecs:
    DEPOSIT_AMOUNT_LESS_THAN_MIN = "Deposit amount must be at least 0.01"
    DEPOSIT_AMOUNT_MORE_THAN_MAX = "Deposit amount cannot exceed 5000"
    UNAUTHORIZED_ACCESS_TO_ACCOUNT = "Unauthorized access to account"

    INTERNAL_SERVER_ERROR_STATUS = 500
    INTERNAL_SERVER_ERROR_TEXT = "Internal Server Error"

    TRANSFER_AMOUNT_LESS_THAN_MIN = "Transfer amount must be at least 0.01"
    TRANSFER_AMOUNT_MORE_THAN_MAX = "Transfer amount cannot exceed 10000"
    INVALID_TRANSFER = "Invalid transfer: insufficient funds or invalid accounts"

    PROFILE_NAME_VALIDATION_MESSAGE = "Name must contain two words with letters only"

    TRANSFER_SUCCESS_MESSAGE = "Transfer successful"
    PROFILE_UPDATE_SUCCESS_MESSAGE = "Profile updated successfully"

    # возврат 200 OK
    @staticmethod
    def request_returns_ok() -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.OK, response.text

        return check

    # возврат 201
    @staticmethod
    def entity_was_created() -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.CREATED, response.text

        return check

    # возврат 204 или 200
    @staticmethod
    def entity_was_deleted() -> Callable:
        def check(response: Response):
            assert response.status_code in [
                HTTPStatus.NO_CONTENT,
                HTTPStatus.OK
            ], response.text

        return check

    # успешный депозит
    @staticmethod
    def success_deposit_response(
        account_id: int,
        expected_balance: float
    ) -> Callable:

        def check(response: Response):
            assert response.status_code == HTTPStatus.OK
            assert response.json().get('id') == account_id
            assert response.json().get('accountNumber') == f"ACC{account_id}"
            assert response.json().get('balance') == pytest.approx(expected_balance)
            assert response.json().get('transactions') is not None

        return check

    # успешный трансфер
    @staticmethod
    def success_transfer_response(
        expected_amount: float,
        sender_account_id: int,
        receiver_account_id: int
    ) -> Callable:

        def check(response: Response):
            assert response.status_code == HTTPStatus.OK
            assert response.json().get('amount') == pytest.approx(expected_amount)
            assert response.json().get('receiverAccountId') == receiver_account_id
            assert response.json().get('senderAccountId') == sender_account_id
            assert response.json().get('message') == ResponseSpecs.TRANSFER_SUCCESS_MESSAGE

        return check

    # успешное изменение профиля
    @staticmethod
    def success_profile_update_response(expected_name: str) -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.OK
            assert (
                response.json().get('message')
                == ResponseSpecs.PROFILE_UPDATE_SUCCESS_MESSAGE
            )
            assert response.json().get('customer').get('name') == expected_name

        return check

    # возврат 400 ошибки с ключом и текстом
    @staticmethod
    def request_returns_bad_request(
        error_key: str,
        error_value: str
    ) -> Callable:

        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, response.text

            errors = response.json().get(error_key)

            assert errors is not None
            assert error_value in errors

        return check

    # возврат 400 ошибки только с текстом
    @staticmethod
    def _request_returns_bad_request_with_text(error_text: str) -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
            assert response.text == error_text

        return check

    # возврат 403 ошибки
    @staticmethod
    def forbidden_with_text(error_text: str) -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.FORBIDDEN, response.text
            assert response.text == error_text

        return check

    # возврат 401 ошибки
    @staticmethod
    def unauthorized() -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.UNAUTHORIZED, response.text

        return check

    # возврат 500 ошибки
    @staticmethod
    def internal_server_error_for_path(path: str) -> Callable:
        def check(response: Response):
            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR, response.text
            assert (
                response.json().get('status')
                == ResponseSpecs.INTERNAL_SERVER_ERROR_STATUS
            )
            assert (
                response.json().get('error')
                == ResponseSpecs.INTERNAL_SERVER_ERROR_TEXT
            )
            assert response.json().get('path') == path

        return check

    # 400 при попытке отправить депозит меньше минимума
    @staticmethod
    def deposit_amount_less_than_min() -> Callable:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.DEPOSIT_AMOUNT_LESS_THAN_MIN
        )

    # 400 при попытке отправить депозит больше максимума
    @staticmethod
    def deposit_amount_more_than_max() -> Callable:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.DEPOSIT_AMOUNT_MORE_THAN_MAX
        )

    # 400 при попытке отправить трансфер меньше минимума
    @staticmethod
    def transfer_amount_less_than_min() -> Callable:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.TRANSFER_AMOUNT_LESS_THAN_MIN
        )

    # 400 при попытке отправить трансфер больше максимума
    @staticmethod
    def transfer_amount_more_than_max() -> Callable:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.TRANSFER_AMOUNT_MORE_THAN_MAX
        )

    # 400 при некорректном трансфере
    @staticmethod
    def invalid_transfer() -> Callable:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.INVALID_TRANSFER
        )

    # 400 при некорректном имени
    @staticmethod
    def profile_name_validation_error() -> Callable:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.PROFILE_NAME_VALIDATION_MESSAGE
        )

    # 403 ошибка при попытке работать с недоступным аккаунтом
    @staticmethod
    def unauthorized_access_to_account() -> Callable:
        return ResponseSpecs.forbidden_with_text(
            ResponseSpecs.UNAUTHORIZED_ACCESS_TO_ACCOUNT
        )