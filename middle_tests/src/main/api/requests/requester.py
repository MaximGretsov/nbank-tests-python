from typing import Any, Callable
from abc import ABC

from requests import Response


class Requester(ABC):
    def __init__(
        self,
        request_spec: dict[str, Any],
        response_spec: Callable[[Response], None]
    ):
        self.headers = request_spec.get('headers')
        self.base_url = request_spec.get(
            'base_url',
            'http://localhost:4111/api/v1'
        )
        self.response_spec = response_spec
