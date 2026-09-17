from http import HTTPStatus
from typing import Callable

from requests import Response

import pytest


class ResponseSpecs:
    TRANSFER_SUCCESS_MESSAGE = "Transfer successful"
    PROFILE_UPDATE_SUCCESS_MESSAGE = "Profile updated successfully"

    DEPOSIT_AMOUNT_LESS_THAN_MIN = "Deposit amount must be at least 0.01"
    DEPOSIT_AMOUNT_MORE_THAN_MAX = "Deposit amount cannot exceed 5000"
    UNAUTHORIZED_ACCESS_TO_ACCOUNT = "Unauthorized access to account"

    INTERNAL_SERVER_ERROR_STATUS = 500
    INTERNAL_SERVER_ERROR_TEXT = "Internal Server Error"

    TRANSFER_AMOUNT_LESS_THAN_MIN = "Transfer amount must be at least 0.01"
    TRANSFER_AMOUNT_MORE_THAN_MAX = "Transfer amount cannot exceed 10000"
    INVALID_TRANSFER = "Invalid transfer: insufficient funds or invalid accounts"

    PROFILE_NAME_VALIDATION_MESSAGE = (
        "Name must contain two words with letters only"
    )

    @staticmethod
    def _make_status_checker(
        expected_statuses: list[HTTPStatus]
    ) -> Callable[[Response], None]:

        def check(response: Response):
            assert response.status_code in expected_statuses, (
                f"Expected status {expected_statuses}, "
                f"but got {response.status_code}. "
                f"Response body: {response.text}"
            )

        return check

    @staticmethod
    def request_returns_ok() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker(
            [HTTPStatus.OK]
        )

    @staticmethod
    def entity_was_created() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker(
            [HTTPStatus.CREATED]
        )

    @staticmethod
    def success_deposit_response(
        account_id: int,
        expected_balance: float
    ) -> Callable[[Response], None]:

        def check(response: Response):
            assert response.status_code == HTTPStatus.OK

            assert (
                response.json().get("accountNumber")
                == f"ACC{account_id}"
            )

            assert (
                response.json().get("balance")
                == pytest.approx(expected_balance)
            )

            assert response.json().get("transactions") is not None

        return check

    @staticmethod
    def entity_was_deleted() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker(
            [
                HTTPStatus.OK,
                HTTPStatus.NO_CONTENT
            ]
        )

    @staticmethod
    def success_transfer_response() -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code == HTTPStatus.OK
            assert (
                response.json().get("message")
                == ResponseSpecs.TRANSFER_SUCCESS_MESSAGE
            )

        return check

    @staticmethod
    def success_profile_update_response(
        expected_name: str
    ) -> Callable[[Response], None]:

        def check(response: Response):
            assert response.status_code == HTTPStatus.OK
            assert (
                response.json().get("message")
                == ResponseSpecs.PROFILE_UPDATE_SUCCESS_MESSAGE
            )
            assert (
                response.json().get("customer").get("name")
                == expected_name
            )

        return check

    @staticmethod
    def request_returns_bad_request(
        error_key: str,
        error_value: str
    ) -> Callable[[Response], None]:

        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"Expected 400 BAD_REQUEST, "
                f"got {response.status_code}. "
                f"Response: {response.text}"
            )

            actual_value = response.json().get(error_key)

            assert actual_value is not None, (
                f"Error field '{error_key}' not found. "
                f"Response: {response.text}"
            )

            assert error_value in actual_value, (
                f"Expected '{error_value}' "
                f"in field '{error_key}', "
                f"but got '{actual_value}'"
            )

        return check

    @staticmethod
    def _request_returns_bad_request_with_text(
        error_text: str
    ) -> Callable[[Response], None]:

        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                response.text
            )

            assert response.text == error_text

        return check

    @staticmethod
    def forbidden_with_text(
        error_text: str
    ) -> Callable[[Response], None]:

        def check(response: Response):
            assert response.status_code == HTTPStatus.FORBIDDEN, (
                response.text
            )

            assert response.text == error_text

        return check

    @staticmethod
    def unauthorized() -> Callable[[Response], None]:

        def check(response: Response):
            assert response.status_code == HTTPStatus.UNAUTHORIZED, (
                response.text
            )

        return check

    @staticmethod
    def internal_server_error_for_path(
        path: str
    ) -> Callable[[Response], None]:

        def check(response: Response):
            assert (
                response.status_code
                == HTTPStatus.INTERNAL_SERVER_ERROR
            ), response.text

            assert (
                response.json().get("status")
                == ResponseSpecs.INTERNAL_SERVER_ERROR_STATUS
            )

            assert (
                response.json().get("error")
                == ResponseSpecs.INTERNAL_SERVER_ERROR_TEXT
            )

            assert response.json().get("path") == path

        return check

    @staticmethod
    def deposit_amount_less_than_min() -> Callable[[Response], None]:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.DEPOSIT_AMOUNT_LESS_THAN_MIN
        )

    @staticmethod
    def deposit_amount_more_than_max() -> Callable[[Response], None]:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.DEPOSIT_AMOUNT_MORE_THAN_MAX
        )

    @staticmethod
    def transfer_amount_less_than_min() -> Callable[[Response], None]:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.TRANSFER_AMOUNT_LESS_THAN_MIN
        )

    @staticmethod
    def transfer_amount_more_than_max() -> Callable[[Response], None]:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.TRANSFER_AMOUNT_MORE_THAN_MAX
        )

    @staticmethod
    def invalid_transfer() -> Callable[[Response], None]:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.INVALID_TRANSFER
        )

    @staticmethod
    def profile_name_validation_error() -> Callable[[Response], None]:
        return ResponseSpecs._request_returns_bad_request_with_text(
            ResponseSpecs.PROFILE_NAME_VALIDATION_MESSAGE
        )

    @staticmethod
    def unauthorized_access_to_account() -> Callable[[Response], None]:
        return ResponseSpecs.forbidden_with_text(
            ResponseSpecs.UNAUTHORIZED_ACCESS_TO_ACCOUNT
        )