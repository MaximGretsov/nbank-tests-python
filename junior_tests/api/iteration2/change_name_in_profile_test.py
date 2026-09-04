import pytest
import requests
import time

class TestChangeNameInProfile:
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

    # Тест на успешное изменение имени в профиле с корректными значениями
    def test_correct_change_name_in_profile(self):
        username = self.generate_unique_username()
        
        # create user
        self.create_user(username)   

        #login user
        auth_token = self.login_user(username)

        new_name = 'New name'

        change_name_response = requests.put(
            url = 'http://localhost:4111/api/v1/customer/profile',
            json = {
                "name": new_name
            },
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )

        assert change_name_response.status_code == 200
        assert change_name_response.json().get('customer').get('name') == new_name
        assert change_name_response.json().get('message') == 'Profile updated successfully'

    # Тест на неудачное изменение имени в профиле с некорректными значениями
    @pytest.mark.parametrize(
        'new_incorrect_name',
        [# одно слово в поле name
        ('Name'),
        # три слова в поле name
        ('Three word name'),
        # пробел перед двумя словами в имени
        (' New Name'),
        # пробел после двух слов в имени
        ('New Name '),
        # имя из пробелов
        ('   '),
        # имя из двух слов со специальными знаками
        ('New Nam?e'),
        # имя из двух слов с цифрами
        ('New Na1me'),
        # имя из двух слов с дефисом
        ('New John-Doe'),
        # имя из двух слов с двумя пробелами между словами
        ('New  Name')
        ]
    )   

    def test_incorrect_change_name_in_profile(self, new_incorrect_name):
        username = self.generate_unique_username()
               
        # create user
        self.create_user(username)   
       
        #login user
        auth_token = self.login_user(username)
        
        change_name_response = requests.put(
            url = 'http://localhost:4111/api/v1/customer/profile',
            json = {
                "name": new_incorrect_name
            },
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )
        
        assert change_name_response.status_code == 400
        assert change_name_response.text == 'Name must contain two words with letters only'

    # Тест на изменение имени в профиле без авторизации
    def test_change_name_in_profile_without_authorization(self):
        username = self.generate_unique_username()
                       
        # create user
        self.create_user(username)   

        change_name_response = requests.put(
            url = 'http://localhost:4111/api/v1/customer/profile',
            json = {
                "name": 'New Name'
            },
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
            
        assert change_name_response.status_code == 401

    # Тест на изменение имени в профиле с некорректным токеном авторизации
    def test_change_name_in_profile_with_incorrect_authorization(self):
        username = self.generate_unique_username()
                       
        # create user
        self.create_user(username)   
               
        #login user
        auth_token = self.login_user(username)[:-5]
        
        change_name_response = requests.put(
            url = 'http://localhost:4111/api/v1/customer/profile',
            json = {
                "name": 'New Name'
            },
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token
            }
        )
            
        assert change_name_response.status_code == 401