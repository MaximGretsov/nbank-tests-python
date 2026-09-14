import requests
import logging
from middle_tests.src.main.api.configs.config import Config


class RequestSpecs:
    @staticmethod
    def default_req_headers():
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @staticmethod
    def unauth_spec():
        return {
            "base_url": Config.get("backendUrl"),
            "headers": RequestSpecs.default_req_headers()
        }
    
    @staticmethod
    def broken_auth_spec():
        headers = RequestSpecs.default_req_headers()
        headers["Authorization"] = "brokenToken"

        return {
            "base_url": Config.get("backendUrl"),
            "headers": headers
        }

    @staticmethod
    def admin_auth_spec():
        headers = RequestSpecs.default_req_headers()
        headers["Authorization"] = Config.get("ADMIN_AUTH_HEADER", "Basic YWRtaW46YWRtaW4=")
        return {
            "base_url": Config.get("backendUrl"),
            "headers": headers
        }

    @staticmethod
    def auth_as_user(username, password):
        auth_url = f"{Config.get('backendUrl')}/auth/login"
        response = requests.post(auth_url, json={"username": username, "password": password})
        
        if response.status_code == 200:
            auth_header = response.headers.get("Authorization")
            headers = RequestSpecs.default_req_headers()
            headers["Authorization"] = auth_header
            return {
                "base_url": Config.get("backendUrl"),
                "headers": headers
            }
        else:
            logging.error(f"Authentication failed for {username} with status {response.status_code}")
            raise Exception("Failed to authenticate user")