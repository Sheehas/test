import requests
import json
from authorization import open_token_json
from authorization import get_url_token
from manifest import manifest
from datetime import date
from datetime import time
import datetime
from manifest import values
import configparser
import sqlite3


# Получаем новый токен для регистрации даты на сервис
def register_service(time_start, service_id, account):
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()

    query = "SELECT id, name, phone FROM accounts WHERE path = ?"

    path= f'accounts/{account}'

    cursor.execute(query, (path,))

    results = cursor.fetchall()

    email, name, phone = results

    get_url_token(path)
    token = open_token_json(path)
    access_token = token['access_token']

    dt_now = datetime.datetime.utcnow()
    server_date = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    dt_string = server_date.strftime("%Y-%m-%dT%H:%M:%S+01:00") #Для запроса на свободную дату
    # print(access_token)
    data=manifest(time_start, dt_string, email, name, phone, service_id)
    # print(data)
    # Делаем запрос с заголовком и токеном и отправляем манифест для регистрации
    headers = {"Accept":"application/vnd.api+json","Accept-Encoding": "gzip, deflate, br", "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive", "Content-Length": "1100", "content-type": "application/vnd.api+json", "User-Agent": "Booking Page 3.11.2", "Authorization": f"Bearer {access_token}"}

    url3 = 'https://ambasada-r-moldova-in-f-rusa.reservio.com/api/marketplace/booking-form/submit?include=bookingRequests,bookingRequests.booking,payment,user'
    session = requests.Session()
    post_request = session.post(url3, data=data, headers=headers)
    status = post_request.status_code
    # text = post_request.text
    token_json = post_request.text
    # # print(x)
    print(status)
    print(token_json)
    print("Регистрация окончена")
