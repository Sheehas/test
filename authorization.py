from pprint import pprint
from bs4 import BeautifulSoup
import requests
import json
import sqlite3

def save_token_json(token_json,login):
    # Функция сохранения токена в json
    json_obj = json.loads(token_json)
    with open(f'accounts/{login}.json', 'w') as file:
        json.dump(json_obj, file, indent=2)

def open_token_json(path):
    # Функция открытия токена в json
    with open(path, 'r') as file:
        data = file.read()
        json_data = json.loads(data)
    return json_data

def get_url_token(path):
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()

    # Execute the SQL query
    cursor.execute("SELECT email, password FROM users WHERE path = ?", (path,))
    result = cursor.fetchone()  # Get the first record that matches the condition
    if result is not None:
        email, password = result
        # Авторизация и получение токена
        url = 'https://app.reservio.com/api/oauth2/token/'
        session = requests.Session()

        post_request = session.post(url, data={ # type: ignore
            'grant_type': "password",
            'password': f'{password}',
            'username': f'{email}'})
        status = post_request.status_code
        # text = post_request.text
        token_json = post_request.text
        if status == 200:
            save_token_json(token_json,email)
            return ('Авторизация успешна! Токен получен и записан в папку!')
        else:

            return ('Ошибка авторизации! Проверьте логин и пароль!')

def get_info_user():
    token = open_token_json() # type: ignore
    access_token = token['access_token']
    data = {"operationName":"LoggedUser","variables":{},"query":"query LoggedUser {\n  loggedUser {\n    email\n    id\n    language\n    name\n    phone\n    __typename\n  }\n}\n"}


    y = {"Authorization": f"Bearer {access_token}"}
    # Авторизация и получение токена
    url = 'https://app.reservio.com/api/graphql/business'
    url2 = "https://app.reservio.com/api/v2/users/me?include=undefined"
    session = requests.Session()
    post_request = session.post(url, data=data, headers={"Accept":"application/vnd.api+json", "User-Agent": "Business Web 1.53.0", "content-type": "application/json", "Authorization": f"Bearer {access_token}",
                                        "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3", "Content-Length": "170", "Connection": "keep-alive"})
    status = post_request.status_code
    # text = post_request.text
    data_info_user = post_request.text
    print(data_info_user)
    if status == 200:
        # save_token_json(token_json)
        return print('Данные по пользователю получены!')
    else:

        return print('Ошибка авторизации! Проверьте логин и пароль!')
