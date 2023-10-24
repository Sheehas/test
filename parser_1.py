from bs4 import BeautifulSoup
import requests
import datetime
from datetime import date
from datetime import time
import json
import sched, time
from data_json import info_date_json
from data_json import info_time_json
from register_to_date import register_service
# Переменная для повтора
s = sched.scheduler(time.time, time.sleep)

# Словарь сервисов
service_bd = {'service_1': '63fe0e8c-b127-43e3-874a-bac9c660045b',
              'service_2': 'acc4f784-7535-4220-ae06-6e3648a8e829',
              'service_3': '038869df-58b5-437e-b3cf-60c5419ab053',
              'service_4': '429622e5-fac8-47fc-8f64-486810761984',
              'service_5': 'c048e779-64e5-46a4-b0f6-db26dd16ed51',
              'service_6': '96a60481-29f2-49e7-b986-5ad24c46f890',
              'service_7': '59c845fa-48c9-4f79-b7b2-1d07f895f2e6',
              'service_8': 'f8c23fdc-e908-47a5-80f7-a1b43732cf26'}

# Функция запрос под свободную дату и время для сервиса
def get_service(service_id,account):
    # Данные для запроса (дата и время по зулу)
    current_date = date.today()
    dt_now = datetime.datetime.utcnow()
    future_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    dt_string = dt_now.strftime("%Y-%m-%dT%H:%M:%S.%fZ") #Для запроса на свободную дату
    dt_string_future = future_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ") #Для запроса на свободную дату

    url_date = f"https://api.reservio.com/v2/businesses/09250556-2450-437f-aede-82e78712f114/availability/booking-days?page[limit]=50&page[offset]=0&filter[from]={dt_string}&filter[resourceId]=&filter[serviceId]={service_id}&filter[to]={dt_string_future}"
   
    # print(url_date)
    # Обращаемся к АПИ сайта и берем JSON файлы из сервиса на свободную дату
    HEADERS =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
    responce = requests.get(url_date, headers = HEADERS)
    todos = json.loads(responce.text)
    date_info = info_date_json(todos)
    # Делаем проверку на истинность данных
    if date_info[0] == 0:
        return date_info
    else:
        time_info = info_time_json(date_info, service_id)
        time_start = time_info[0]
        print(type(time_start), time_start)
        register_service(time_start, service_id,account)
        return date_info

# Функия опроса всех сервисов
def service_all(): # type: ignore
    print('Начало работа ALLService')
    # s.enter(5,1,service_all)
    tg_str = ""
    for key, value in service_bd.items():
        result = get_service(value) # type: ignore
        # Условия для списка с открытой датой и закрытой
        if result[0] == 0:
            print("нет мест на всех сервисах")
            continue
        else:
            text = (f"Для сервиса {key} есть свободное время на данные даты: {result}")
            tg_str+=f"{text}\n"
        
    # print(tg_str)
    return tg_str

# Только на мониторинг
def get_service_monitoring(service_id):
    # Данные для запроса (дата и время по зулу)
    current_date = date.today()
    dt_now = datetime.datetime.utcnow()
    future_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    dt_string = dt_now.strftime("%Y-%m-%dT%H:%M:%S.%fZ") #Для запроса на свободную дату
    dt_string_future = future_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ") #Для запроса на свободную дату

    url_date = f"https://api.reservio.com/v2/businesses/09250556-2450-437f-aede-82e78712f114/availability/booking-days?page[limit]=50&page[offset]=0&filter[from]={dt_string}&filter[resourceId]=&filter[serviceId]={service_id}&filter[to]={dt_string_future}"
   
    # Обращаемся к АПИ сайта и берем JSON файлы из сервиса на свободную дату
    HEADERS =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
    responce = requests.get(url_date, headers = HEADERS)
    todos = json.loads(responce.text)
    date_info = info_date_json(todos)
    # Делаем проверку на истинность данных
    if date_info[0] == 0:
        return date_info
    else:

        return date_info    

# Функия опроса всех сервисов
def service_all():
    print('Начало работа ALLService')
    # s.enter(5,1,service_all)
    tg_str = ""
    for key, value in service_bd.items():
        result = get_service_monitoring(value)
        # Условия для списка с открытой датой и закрытой
        if result[0] == 0:
            print("нет мест на всех сервисах")
            
            # text = (f"Для сервиса {key} нет свободных дат! Все даты заняты до: {result[1]}")
            tg_str = "нет мест на всех сервисах"
        else:
            text = (f"Для сервиса {key} есть свободное время на данные даты: {result}")
            tg_str+=f"{text}\n"
        
    # print(tg_str)
    return tg_str
# Функция для одного сервиса
def service(service_id,account):
    service_id = f'service_{service_id}'
    result = get_service(service_bd[service_id],account)
    if result[0] == 0:
        return None
    else:
        text = (f"есть свободное время на данные даты: {result}\nАккаунт: {account.replace('.json','')}")
    return text


# def service(service_id):
#     while True:
#         time.sleep(5)
#         text = service_one(service_id)
#         return text
# s.run()
