import pytest
import requests
import time

class TestTransfer:
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

    # Депозит на аккаунт, чтобы была возможность делать перевод денег(сразу 5к)
    def deposit_to_account(self, auth_token: str, account_id: int):
        deposit_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/deposit',
            json={
                "id": account_id,
                "balance": 5000
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )

        assert deposit_response.status_code == 200

    # Позитивные тесты на трансфер на чужой аккаунт
    @pytest.mark.parametrize(
        'amount, expected_amount',
        [(100, 100), 
        (0.01, 0.01), 
        (9999.99, 9999.99), 
        (10000, 10000)]
    )
    def test_user_can_transfer_to_another_account(self, amount, expected_amount):
        username_sender = self.generate_unique_username()

        # create sender user
        self.create_user(username_sender)

        # login sender user
        auth_token_sender = self.login_user(username_sender)

        # create sender account
        account_id_sender = self.create_account(auth_token_sender)

        # deposit to sender account
        self.deposit_to_account(auth_token_sender, account_id_sender)
        self.deposit_to_account(auth_token_sender, account_id_sender)
        self.deposit_to_account(auth_token_sender, account_id_sender)

        sender_balance_before_transfer = 15000

        username_receiver = self.generate_unique_username()

        # create receiver user
        self.create_user(username_receiver)

        # login receiver user
        auth_token_receiver = self.login_user(username_receiver)

        # create receiver account
        account_id_receiver = self.create_account(auth_token_receiver)

        transfer_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/transfer',
            json={
                "senderAccountId": account_id_sender,
                "receiverAccountId": account_id_receiver,
                "amount": amount
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token_sender
            }
        )

        assert transfer_response.status_code == 200
        assert transfer_response.json().get('amount') == expected_amount
        assert transfer_response.json().get('receiverAccountId') == account_id_receiver
        assert transfer_response.json().get('senderAccountId') == account_id_sender

        # Проверяем баланс оправителя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token_sender
            }
        )
        
        assert get_user_profile_response.status_code == 200
        
        accounts = get_user_profile_response.json().get('accounts')
        
        sender_account = None
        
        for current_account in accounts:
            if current_account.get('id') == account_id_sender:
                sender_account = current_account
                break
        
        assert sender_account is not None
        assert sender_account.get('balance') == pytest.approx(sender_balance_before_transfer - amount)

        # Проверяем баланс получателя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token_receiver
            }
        )
                
        assert get_user_profile_response.status_code == 200
                
        accounts = get_user_profile_response.json().get('accounts')
                
        receiver_account = None
                
        for current_account in accounts:
            if current_account.get('id') == account_id_receiver:
                receiver_account = current_account
                break
                
        assert receiver_account is not None
        assert receiver_account.get('balance') == pytest.approx(amount)

    # Позитивный тест на трансфер между своими аккаунтами
    def test_user_can_transfer_between_own_accounts(self):
        username = self.generate_unique_username()

        # create user
        self.create_user(username)

        # login user
        auth_token = self.login_user(username)

        # create sender account
        account_id_sender = self.create_account(auth_token)
        # create receiver account
        account_id_receiver = self.create_account(auth_token)

        # deposit to sender account
        self.deposit_to_account(auth_token, account_id_sender)
        self.deposit_to_account(auth_token, account_id_sender)
        self.deposit_to_account(auth_token, account_id_sender)

        sender_balance_before_transfer = 15000

        transfer_amount = 100
        expected_amount = 100

        transfer_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/transfer',
            json={   
                "senderAccountId": account_id_sender,
                "receiverAccountId": account_id_receiver,
                "amount": transfer_amount
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )

        assert transfer_response.status_code == 200
        assert transfer_response.json().get('amount') == expected_amount
        assert transfer_response.json().get('receiverAccountId') == account_id_receiver
        assert transfer_response.json().get('senderAccountId') == account_id_sender

        # Проверяем баланс оправителя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )
                
        assert get_user_profile_response.status_code == 200
                
        accounts = get_user_profile_response.json().get('accounts')
                
        sender_account = None
                
        for current_account in accounts:
            if current_account.get('id') == account_id_sender:
                sender_account = current_account
                break
                
        assert sender_account is not None
        assert sender_account.get('balance') == pytest.approx(sender_balance_before_transfer - expected_amount)

        # Проверяем баланс получателя после трансфера
        receiver_account = None

        for current_account in accounts:
            if current_account.get('id') == account_id_receiver:
                receiver_account = current_account
                break

        assert receiver_account is not None
        assert receiver_account.get('balance') == pytest.approx(expected_amount)

    # Негативный тест c невалидной суммой трансфера
    @pytest.mark.parametrize(
        'amount, error_message',
        [(-100, "Transfer amount must be at least 0.01"), 
         (0, "Transfer amount must be at least 0.01"), 
         (10000.01, "Transfer amount cannot exceed 10000"),
         (7500, "Invalid transfer: insufficient funds or invalid accounts")]
    )

    def test_user_cannot_transfer_with_invalid_transfer_conditions(self, amount: float, error_message: str):
        username_sender = self.generate_unique_username()

        # create sender user
        self.create_user(username_sender)

        # login sender user
        auth_token_sender = self.login_user(username_sender)

        # create sender account
        account_id_sender = self.create_account(auth_token_sender)
        # create receiver account
        account_id_receiver = self.create_account(auth_token_sender)

        # deposit to sender account
        self.deposit_to_account(auth_token_sender, account_id_sender)

        sender_balance_before_transfer = 5000

        transfer_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/transfer',
            json={
                "senderAccountId": account_id_sender,
                "receiverAccountId": account_id_receiver,
                "amount": amount
            }, 
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token_sender
            }
        )   

        assert transfer_response.status_code == 400
        assert transfer_response.text == error_message

        # Проверяем баланс оправителя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token_sender
            }
        )
                
        assert get_user_profile_response.status_code == 200
                
        accounts = get_user_profile_response.json().get('accounts')
                
        sender_account = None
                
        for current_account in accounts:
            if current_account.get('id') == account_id_sender:
                sender_account = current_account
                break
                
        assert sender_account is not None
        assert sender_account.get('balance') == pytest.approx(sender_balance_before_transfer)

        # Проверяем баланс получателя после трансфера
        receiver_account = None

        for current_account in accounts:
            if current_account.get('id') == account_id_receiver:
                receiver_account = current_account
                break

        assert receiver_account is not None
        assert receiver_account.get('balance') == 0
        
    # Негативный тест: трансфер на несуществующий аккаунт
    def test_user_cannot_transfer_to_nonexistent_account(self):
        username_sender = self.generate_unique_username()

        # create sender user
        self.create_user(username_sender)

        # login sender user
        auth_token_sender = self.login_user(username_sender)

        # create sender account
        account_id_sender = self.create_account(auth_token_sender)

        # deposit to sender account
        self.deposit_to_account(auth_token_sender, account_id_sender)

        sender_balance_before_transfer = 5000

        # create a non-existent account id
        non_existent_account_id = account_id_sender + 1000000

        transfer_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/transfer',
            json={
                "senderAccountId": account_id_sender,
                "receiverAccountId": non_existent_account_id,
                "amount": 100
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token_sender
            }
        )

        assert transfer_response.status_code == 400
        assert transfer_response.text == "Invalid transfer: insufficient funds or invalid accounts"

        # Проверяем баланс оправителя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token_sender
            }
        )
                
        assert get_user_profile_response.status_code == 200
                
        accounts = get_user_profile_response.json().get('accounts')
                
        sender_account = None
                
        for current_account in accounts:
            if current_account.get('id') == account_id_sender:
                sender_account = current_account
                break
                
        assert sender_account is not None
        assert sender_account.get('balance') == pytest.approx(sender_balance_before_transfer)

    # Негативный тест: трансфер с несуществующего аккаунта
    def test_user_cannot_transfer_from_nonexistent_account(self):
        username_receiver = self.generate_unique_username()

        # create receiver user
        self.create_user(username_receiver)

        # login receiver user
        auth_token_receiver = self.login_user(username_receiver)

        # create receiver account
        account_id_receiver = self.create_account(auth_token_receiver)

        # create a non-existent account id
        non_existent_account_id = account_id_receiver + 1000000

        transfer_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/transfer',
            json={
                "senderAccountId": non_existent_account_id,
                "receiverAccountId": account_id_receiver,
                "amount": 100
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token_receiver
            }
        )

        assert transfer_response.status_code == 403
        assert transfer_response.text == "Unauthorized access to account"

        # Проверяем баланс получателя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token_receiver
            }
        )
                
        assert get_user_profile_response.status_code == 200
                
        accounts = get_user_profile_response.json().get('accounts')
                
        receiver_account = None
                
        for current_account in accounts:
            if current_account.get('id') == account_id_receiver:
                receiver_account = current_account
                break
                
        assert receiver_account is not None
        assert receiver_account.get('balance') == 0

    # Негативный тест: трансфер с чужого аккаунта
    def test_user_cannot_transfer_from_another_users_account(self):
        username_sender = self.generate_unique_username()

        # create sender user
        self.create_user(username_sender)

        # login sender user
        auth_token_sender = self.login_user(username_sender)

        # create sender account
        account_id_sender = self.create_account(auth_token_sender)

        # deposit to sender account
        self.deposit_to_account(auth_token_sender, account_id_sender)

        sender_balance_before_transfer = 5000

        username_receiver = self.generate_unique_username()

        # create receiver user
        self.create_user(username_receiver)

        # login receiver user
        auth_token_receiver = self.login_user(username_receiver)

        # create receiver account
        account_id_receiver = self.create_account(auth_token_receiver)

        transfer_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/transfer',
            json={
                "senderAccountId": account_id_sender,
                "receiverAccountId": account_id_receiver,
                "amount": 100
            },  
            headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': auth_token_receiver
            }
        )

        assert transfer_response.status_code == 403
        assert transfer_response.text == "Unauthorized access to account"

        # Проверяем баланс оправителя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token_sender
            }
        )
                
        assert get_user_profile_response.status_code == 200
                
        accounts = get_user_profile_response.json().get('accounts')
                
        sender_account = None
                
        for current_account in accounts:
            if current_account.get('id') == account_id_sender:
                sender_account = current_account
                break
                
        assert sender_account is not None
        assert sender_account.get('balance') == pytest.approx(sender_balance_before_transfer)

         # Проверяем баланс получателя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token_receiver
            }
        )
                
        assert get_user_profile_response.status_code == 200
                
        accounts = get_user_profile_response.json().get('accounts')
                
        receiver_account = None
                
        for current_account in accounts:
            if current_account.get('id') == account_id_receiver:
                receiver_account = current_account
                break
                
        assert receiver_account is not None
        assert receiver_account.get('balance') == 0
        
    # Негативный тест: трансфер с некорректным токеном авторизации
    def test_user_cannot_transfer_with_invalid_authorization(self):
        username_sender = self.generate_unique_username()
        
        # create sender user
        self.create_user(username_sender)

        # login sender user
        auth_token_sender = self.login_user(username_sender)

        # create sender account
        account_id_sender = self.create_account(auth_token_sender)
        # create receiver account
        account_id_receiver = self.create_account(auth_token_sender)

        # deposit to sender account
        self.deposit_to_account(auth_token_sender, account_id_sender)

        sender_balance_before_transfer = 5000

        # create an invalid auth token
        invalid_auth_token = auth_token_sender[:-5]

        transfer_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/transfer',
            json={
                "senderAccountId": account_id_sender,
                "receiverAccountId": account_id_receiver,
                "amount": 100
            },
            headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': invalid_auth_token
            }
        )

        assert transfer_response.status_code == 401

         # Проверяем баланс оправителя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token_sender
            }
        )
                
        assert get_user_profile_response.status_code == 200
                
        accounts = get_user_profile_response.json().get('accounts')
                
        sender_account = None
                
        for current_account in accounts:
            if current_account.get('id') == account_id_sender:
                sender_account = current_account
                break
                
        assert sender_account is not None
        assert sender_account.get('balance') == pytest.approx(sender_balance_before_transfer)

        # Проверяем баланс получателя после трансфера
        receiver_account = None

        for current_account in accounts:
            if current_account.get('id') == account_id_receiver:
                receiver_account = current_account
                break

        assert receiver_account is not None
        assert receiver_account.get('balance') == 0
    
    # Негативный тест: трансфер без токена авторизации
    def test_user_cannot_transfer_without_authorization(self):
        username_sender = self.generate_unique_username()
        
        # create sender user
        self.create_user(username_sender)

        # login sender user
        auth_token_sender = self.login_user(username_sender)

        # create sender account
        account_id_sender = self.create_account(auth_token_sender)
        # create receiver account
        account_id_receiver = self.create_account(auth_token_sender)

        # deposit to sender account
        self.deposit_to_account(auth_token_sender, account_id_sender)

        sender_balance_before_transfer = 5000

        transfer_response = requests.post(
            url='http://localhost:4111/api/v1/accounts/transfer',
            json={
                "senderAccountId": account_id_sender,
                "receiverAccountId": account_id_receiver,
                "amount": 100
            },  
            headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
            }
        )

        assert transfer_response.status_code == 401

         # Проверяем баланс оправителя после трансфера
        get_user_profile_response = requests.get(
            url='http://localhost:4111/api/v1/customer/profile',
            headers={
                'Accept': 'application/json',
                'Authorization': auth_token_sender
            }
        )
                
        assert get_user_profile_response.status_code == 200
                
        accounts = get_user_profile_response.json().get('accounts')
                
        sender_account = None
                
        for current_account in accounts:
            if current_account.get('id') == account_id_sender:
                sender_account = current_account
                break
                
        assert sender_account is not None
        assert sender_account.get('balance') == pytest.approx(sender_balance_before_transfer)

        # Проверяем баланс получателя после трансфера
        receiver_account = None

        for current_account in accounts:
            if current_account.get('id') == account_id_receiver:
                receiver_account = current_account
                break

        assert receiver_account is not None
        assert receiver_account.get('balance') == 0