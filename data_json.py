import json
import requests


HEADERS =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
# Запись истории дат (чтобы не всплывали сообщения с датами которые и так уже известны)
def uniqe_value(open_date):
    text = 'start'
    with open("unique_keys", "a") as file:
        for  line in open_date:
            text += f'{line},'
        file.write(f'{text}\n')

# Функция для поиска свободной даты в ответе сервиса
def info_date_json(todos):
    print("Начало работа парсера JSON")
    data_todo = todos['data']
    len_list = len(data_todo)
    # print(len_list)
    open_date = []
    close_date = []
    for i in range(len_list):
        one_data = data_todo[i]
        attributes_one_data = one_data['attributes']
        close_date.append(attributes_one_data["date"])
        if attributes_one_data['isAvailable']:
            try:
                # print("Есть свободные даты")
                open_date.append(attributes_one_data['date'])
            except:
                
                print('Нет свободных дат!')
    # print(close_date)            
    if len(open_date) == 0:
        # print('1')
        log = close_date
        log.append(0)
        log.reverse()
        result = log
        # print(result)
        # print(f'Даты которые уже заняты: {result}')
    else:
        uniqe_value(open_date)
        result = open_date
        print(result)
    return result


def info_time_json(open_date, service_id):
    open_date_time = {}
    start_attributes_one_data = []
    service_id_1=service_id
    print(service_id_1)
    for day in open_date:
        url_2 = f"https://api.reservio.com/v2/businesses/09250556-2450-437f-aede-82e78712f114/availability/booking-slots?page[limit]=50&page[offset]=0&filter[from]={day}&filter[resourceId]=&filter[serviceId]={service_id_1}&filter[to]={day}&include=undefined"
        responce_2 = requests.get(url_2, headers = HEADERS)
        print(responce_2.text)
        todos_2 = json.loads(responce_2.text)
        print(todos_2)
        data_todo_2 = todos_2['data']
        print(data_todo_2)
        len_list_2 = len(data_todo_2)
        # print(len_list_2)
        
        for i in range(len_list_2):
            one_data = data_todo_2[i]
            attributes_one_data_1 = one_data['attributes']
            # start_attributes_one_data = attributes_one_data['start']
            open_date_time[day + f'#:{i}']= attributes_one_data_1
        
        one_data = data_todo_2[0]
        attributes_one_data = one_data['attributes']
        start_attributes_one_data.append(attributes_one_data['start'])
        print(start_attributes_one_data)
    return start_attributes_one_data
