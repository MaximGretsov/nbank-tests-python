import pytest
import requests
import time

class TestDeposit:
    # Получение уникального имени пользователя
    def generate_unique_username(self):
        timestamp = int(time.time() * 1000) % 100_000_000
        return f"user_{timestamp:08d}"

    # Создание пользователя с уникальным именем
    def create_user(self, username: str):
        create_user_response = requests.post(
            url='http://localhost:4111/api/v1/admin/users',
            json={
                "username": username,
                "password": 'verysTRongPassword33$',
                "role": 'USER'
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Basic YWRtaW46YWRtaW4='
            }
        )

        assert create_user_response.status_code == 201

    # Получение токена авторизации для пользователя
    def login_user(self, username: str):
        login_response = requests.post(
            url = 'http://localhost:4111/api/v1/auth/login',
            json = {
                "username": username,
                "password": 'verysTRongPassword33$'
            },
            headers ={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

        assert login_response.status_code == 200
        assert login_response.headers.get('authorization')

        return login_response.headers.get('authorization')

    # Создание account для пользователя
    def create_account(self, auth_token: str):
        create_account_response = requests.post(
            url='http://localhost:4111/api/v1/accounts',
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )

        assert create_account_response.status_code == 201
        return create_account_response.json().get('id')

    @pytest.mark.parametrize(
        'amount, new_balance',
        [(100, 100), (0.01, 0.01), (4999.99, 4999.99), (5000, 5000)]
    )

    # Тест на успешный депозит с валидными суммами
    def test_user_candeposit_with_valid_amount(self, amount: float, new_balance: float):
        username = self.generate_unique_username()
        
        # create user
        self.create_user(username)   

        #login user
        auth_token = self.login_user(username)

        # create account
        account_id = self.create_account(auth_token)

        # deposit money
        deposit_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/deposit',
            json={
                "id":account_id,
                "balance": amount
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )

        assert deposit_response.status_code == 200
        assert deposit_response.json().get('id') == account_id
        assert deposit_response.json().get('balance') == new_balance
        assert deposit_response.json().get('transactions') is not None

    # Тест на неудачный депозит с невалидными суммами
    @pytest.mark.parametrize(
        'amount, error_message',
        [(-100, "Deposit amount must be at least 0.01"), 
         (0, "Deposit amount must be at least 0.01"), 
         (5000.01, "Deposit amount cannot exceed 5000")]
    )

    def test_user_cannot_deposit_with_invalid_amount(self, amount: float, error_message: str):
        username = self.generate_unique_username()
                
        # create user
        self.create_user(username)   

        #login user
        auth_token = self.login_user(username)

        # create account
        account_id = self.create_account(auth_token)

        # deposit money
        deposit_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/deposit',
            json={
                "id":account_id,
                "balance": amount
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )

        assert deposit_response.status_code == 400
        assert deposit_response.text == error_message

    # Тест на неудачный депозит на несуществующий account
    def test_user_cannot_deposit_to_nonexistent_account(self):
        username = self.generate_unique_username()
                
        # create user
        self.create_user(username)   

        #login user
        auth_token = self.login_user(username)

        # create account
        account_id = self.create_account(auth_token)

        # create a non-existent account id
        non_existent_account_id = account_id + 1000000

        # deposit money to non-existent account
        deposit_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/deposit',
            json={
                "id": non_existent_account_id,
                "balance": 100
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )

        assert deposit_response.status_code == 403
        assert deposit_response.text == 'Unauthorized access to account'

    # Тест на неудачный депозит с невалидным токеном авторизации
    def test_user_cannot_deposit_with_invalid_auth_token(self):
        username = self.generate_unique_username()
                
        # create user
        self.create_user(username)   

        #login user
        auth_token = self.login_user(username)

        # create account
        account_id = self.create_account(auth_token)

        # create an invalid auth token
        invalid_auth_token = auth_token[:-5]

        # deposit money with invalid auth token
        deposit_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/deposit',
            json={
                "id": account_id,
                "balance": 100
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': invalid_auth_token
            }
        )

        assert deposit_response.status_code == 401

    # Тест на неудачный депозит с отсутствующим токеном авторизации
    def test_user_cannot_deposit_without_auth_token(self):
        username = self.generate_unique_username()
                
        # create user
        self.create_user(username)   

        #login user
        auth_token = self.login_user(username)

        # create account
        account_id = self.create_account(auth_token)

        # deposit money without auth token
        deposit_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/deposit',
            json={
                "id": account_id,
                "balance": 100
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

        assert deposit_response.status_code == 401