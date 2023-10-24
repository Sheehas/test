import os
from bs4 import BeautifulSoup
import telebot
import sqlite3
from telebot import types
from authorization import get_url_token
from pprint import pprint
from parser_1 import service, service_all
import time
import requests

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
bot = telebot.TeleBot('6068557359:AAEjIeHimnYh6F1fk0PetkxoCHTAjRVEiUE')

# Папка, содержащая .json файлы
json_folder = 'accounts'

service_data = {"service_1": [False,None],
                "service_2": [False,None],
                "service_3": [False,None],
                "service_4": [False,None],
                "service_5": [False,None],
                "service_6": [False,None],
                "service_7": [False,None],
                "service_8": [False,None],
                "service_all": False}

# Создаем или подключаемся к базе данных
conn = sqlite3.connect('user_database.db')
cursor = conn.cursor()

# Создаем таблицу для хранения информации о пользователях
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
        email TEXT,
        password TEXT,
        name TEXT,
        phone TEXT,
        path TEXT
    )
''')
conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    # Отправьте приветственное сообщение при команде /start
    bot.send_message(message.chat.id, "Привет! Я ваш бот. Для начала использования введите /help для получения справки.")

@bot.message_handler(commands=['help'])
def help(message):
    # Отправьте справочное сообщение при команде /help
    bot.send_message(message.chat.id, "Вы можете использовать следующие команды:\n"
                                      "/start - Начать общение с ботом\n"
                                      "/help - Получить справку о доступных командах\n"
                                      "/login email:password:name:phone - Зарегистрировать аккаунт\n"
                                      "/account - Просмотр доступных аккаунтов\n"
                                      "/service_all - Запустить мониторинг всех сервисов\n"
                                      "/stop_service_all - Остановить мониторинг всех сервисов\n"
                                      "/stop - Остановить конкретный сервис\n")

@bot.message_handler(commands=['service_all'])
def monitoring_all(message):
    service_data["service_all"] = True
    while service_data["service_all"]:
        text = service_all()
        bot.send_message(message.chat.id, f'Начал поиск, {text}')
        time.sleep(5)

@bot.message_handler(commands=['stop_service_all'])
def stop_service_all(message):
    service_data["service_all"] = False
    bot.send_message(message.chat.id, 'Перестаём мониторить "service_all"!')

@bot.message_handler(commands=['stop'])
def stop(message):
    true_services = [monitoring for monitoring, value in service_data.items() if isinstance(value, list) and value[0]]

    if true_services:
        keyboard = types.InlineKeyboardMarkup()
        for monitoring in true_services:
            service_name, account = monitoring, service_data[monitoring][1]
            text = f"{service_name.replace('service_','Сервис ')} | {account.replace('.json','')}"
            button = types.InlineKeyboardButton(text=text, callback_data='stop:' + service_name)
            keyboard.add(button)
        bot.send_message(message.chat.id, "Выберите сервис для остановки:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "На данный момент нет сервисов для остановки.")

# Обработчик обратного вызова для 'stop:xxx', где xxx - название сервиса
@bot.callback_query_handler(func=lambda call: call.data.startswith('stop:'))
def stop_account(call):
    service_name = call.data[5:]  # Извлечение названия сервиса
    if service_name in service_data:
        account = service_data[service_name][1]
        service_data[service_name] = [False, None]
        bot .send_message(call.message.chat.id, f"Сервис №'{service_name.replace('service_','')}' был остановлен.\nАккаунт {account.replace('.json','')}")
    else:
        bot.send_message(call.message.chat.id, f"Сервис №'{service_name.replace('service_','')}' не найден в данных.")

@bot.message_handler(commands=['login'])
def login(message):
    user_id = message.from_user.id

    if ':' in message.text:
        params = message.text.split(' ')
        if len(params) == 2:
            data = params[1].split(':')
            if len(data) == 2:
                email, password= data
                name = 'Хлюстина Ольга Владимировна'
                phone = '+79250423406'
                # Создаем новую базу данных и курсор внутри этой функции
                conn = sqlite3.connect('user_database.db')
                cursor = conn.cursor()
                try:
                    # Проверяем, существует ли уже такой email в базе данных
                    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                    existing_user = cursor.fetchone()
                    if existing_user:
                        # Если электронная почта уже зарегистрирована, отправьте сообщение и опцию для удаления аккаунта
                        markup = telebot.types.InlineKeyboardMarkup()
                        delete_button = telebot.types.InlineKeyboardButton("Удалить аккаунт", callback_data=f"delete:{email}")
                        markup.add(delete_button)
                        bot.reply_to(message, "Этот email уже зарегистрирован.", reply_markup=markup)
                    else:
                        # Электронная почта не зарегистрирована, продолжайте регистрацию
                        path = f'accounts/{email}.json'
                        cursor.execute(
                            "INSERT INTO users (id, email, password, name, phone, path) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, email, password, name, phone, path))
                        conn.commit()
                        conn.close()
                        get_url_token(path)
                        bot.reply_to(message, "Регистрация прошла успешно!")
                finally:
                    conn.close()
            else:
                bot.reply_to(message, "Неверное количество параметров. Используйте /login email:password")
        else:
            bot.reply_to(message, "Неверный формат. Используйте /login email:password")
    else:
        bot.reply_to(message, "Неверный формат. Используйте /login email:password")

# Обработчик удаления аккаунта
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete:'))
def delete_account(call):
    email = call.data.split(':')[1]
    # Создаем новое соединение с базой данных и курсор
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    try:
        # Удалить аккаунт на основе email
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        bot.send_message(call.message.chat.id, f"Аккаунт с email {email} удален.")
    finally:
        conn.close()

@bot.message_handler(commands=['account'])
def account(message):
    # Создаем инлайн-клавиатуру
    keyboard = telebot.types.InlineKeyboardMarkup()

    # Перебираем все файлы в папке
    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):

            button = telebot.types.InlineKeyboardButton(text=filename.replace(".json", ''), callback_data=filename)
            keyboard.add(button)

    if not keyboard.keyboard:
        # Если файлы не найдены, отправьте сообщение
        bot.send_message(message.chat.id, "Вы не добавили ни одного аккаунта!")
    else:
        # Если файлы найдены, отправьте клавиатуру для выбора файла
        bot.send_message(message.chat.id, "Выберите файл:", reply_markup=keyboard)

# Обработчик для обработки выбора пользователя сервиса
@bot.callback_query_handler(func=lambda call: call.data.startswith('rezerv_'))
def handle_service_selection(call):
    call_info = (call.data).replace('rezerv_','').replace('_accounts/',' ').split(' ')

    number, account = call_info
    service_data[f"service_{number}"][0] = True
    service_data[f"service_{number}"][1] = account
    pprint(service_data)
    
    bot.send_message(call.message.chat.id,f"Вы подключили средство мониторинга и записи на Сервис №{number}!\nАккаунт {account.replace('json','')}")
    
    while service_data[f"service_{number}"][0]:
        result = service(number, account)
        if result != None:
            bot.send_message(call.message.chat.id,f"Вы подключили средство мониторинга и записи на Сервис №{number}!\nНа данный момент {result} \nАккаунт {account.replace('json','')}")
        time.sleep(5)

def create_keyboard(filename):
    response = requests.get('https://ambasada-r-moldova-in-f-rusa.reservio.com/')
    soup = BeautifulSoup(response.text, 'lxml')
    elements = soup.find_all(class_='name-0-2-188')
    markup = types.InlineKeyboardMarkup()

    for index, element in enumerate(elements):
        button_id = f"rezerv_{index+1}"
        button_text = element.text
        button = types.InlineKeyboardButton(text=button_text, callback_data=f'{button_id}_{filename}')
        markup.add(button)

    return markup

@bot.callback_query_handler(func=lambda call: True)
def send_json_file(call):
    user_id = call.from_user.id
    filename = os.path.join(f'{json_folder}/{call.data}')  # Соединяем путь папки с именем файла

    if os.path.isfile(filename):
        markup = create_keyboard(filename)
        bot.send_message(call.message.chat.id, "Выберите элемент:", reply_markup=markup)

    else:
        bot.send_message(user_id, "Выбранный файл не существует. Пожалуйста, выберите действительный файл.")

# Запуск бота
bot.polling()
