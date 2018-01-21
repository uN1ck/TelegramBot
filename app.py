"""Главный модуль приложения

Данный модуль отвечает за обработку комманд, присланных пользователями телеграм-боту

"""
import json
import os
from enum import Enum

import requests
from flask import Flask
from flask import request
from pymongo import MongoClient

API = requests.Session()
APP = Flask(__name__)
CLIENT = MongoClient(os.environ.get('MONGODB_URI'))


class USER_TYPE(Enum):
    TEAM = 0,
    MASTER = 1,


def send_reply(response):
    """
    Функция отправки сообщения ботом пользователю
        :param response: сформированный объект ответа бота для API телеграмма
    """
    if 'text' in response:
        API.post(os.environ.get('URL') + "sendMessage", data=response)


def command_help(arguments, message):
    """
    Функция определяющая ответ на команду /help
        :param arguments: Аргументы команды (/command argument1 argument2 ...)
        :param message: Объект полученного сообщения от пользователя
    """
    response = {'chat_id': message['chat']['id']}
    result = ["Здравствуйте, {}!\nЯ бот и умею выполнять следующие команды:".format(message["from"].get("first_name"))]
    for command in CMD:
        result.append(command)
    response['text'] = "\n\t".join(result)
    return response


def command_team(arguments, message):
    database = CLIENT[os.environ.get('MONGO_DBNAME')]
    users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
    works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
    response = {'chat_id': message['chat']['id']}

    user = users_collection.find_one({"username": message['chat']['username']})
    if user is None:
        user = {
            "username": message['chat']['username'],
            "user_type": int(USER_TYPE.TEAM.value),
            "chat_id": message['chat']['id']
        }
        users_collection.insert(user)
        response['text'] = "Здравствуйте, {}! Вы  зарегистрировались как Бригада.".format(message["from"].get("first_name"))
        works = works_collection.find({})
        keyboard = {'inline_keyboard':
                        [[{"text": work['address'],
                           "callback_data": {"data": "addobject", "message": "edit_work:" + work['_id']}}] for work in works]
                    }
        response['reply_markup'] = json.dumps(keyboard)
    else:
        response["text"] = "Вы уже зарегистрирвоаны, требуется перерегистрация"

    return response


def command_master(arguments, message):
    database = CLIENT[os.environ.get('MONGO_DBNAME')]
    users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
    works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
    response = {'chat_id': message['chat']['id']}

    user = users_collection.find_one({"username": message['chat']['username']})
    if user is None:
        user = {
            "username": message['chat']['username'],
            "user_type": int(USER_TYPE.MASTER.value),
            "chat_id": message['chat']['id']
        }
        users_collection.insert(user)
        response['text'] = "Здравствуйте, {}! Вы  зарегистрировались как Управляющий.".format(message["from"].get("first_name"))

        works = works_collection.find({})
        keyboard = {
            'inline_keyboard': [[{"text": "Добавить объект", "callback_data": {"data": "addobject", "message": "add_object"}}]]}
        for work in works:
            keyboard['inline_keyboard'] += [
                {"text": work['address'], "callback_data": {"data": "www", "message": "edit_work " + work['_id']}}]
        response['reply_markup'] = json.dumps(keyboard)
    else:
        response["text"] = "Вы уже зарегистрирвоаны, требуется перерегистрация"

    return response


def command_stop(arguments, message):
    """
       Функция определяющая ответ на команду /stop. надо удалить chat_id в монго
           :param arguments: Аргументы команды (/command argument1 argument2 ...)
           :param message: Объект полученного сообщения от пользователя
       """
    database = CLIENT[os.environ.get('MONGO_DBNAME')]
    users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
    users_collection.delete_many({"username": message['chat']['username']})

    response = {'chat_id': message['chat']['id'], 'text': "До свидания, {}!".format(message["from"].get("first_name"))}
    return response


def command_not_found(arguments, message):
    """
    Функция, отвечающая пользователю в случае введения неизвестной команды
        :param arguments: Аргументы команды (/command argument1 argument2 ...)
        :param message: Объект полученного сообщения от пользователя
    """
    response = {'chat_id': message['chat']['id']}
    response['text'] = "Данная команда для меня неизвестна. Введите /help для получения информации"
    return response


def button_callback(data, message):
    """
    Обработчик всех кнопок бота
        :param data: data вернувшаяся с кнопки (callback_data)
        :param message: Объект полученного сообщения от пользователя
    """
    response = {'chat_id': message['chat']['id']}
    calc_data = [line for line in data.split('+') if line.strip() != '']
    current_command = calc_data[-1][:-1]
    last_data = '+'.join(calc_data) + '+'
    print(current_command, message, last_data)
    response = CMD.get(current_command, command_not_found)(message, last_data)
    return response


CMD = {
    '/помощь': command_help,
    '/управление': command_master,
    '/бригада': command_team,
    '/выйти': command_stop,
}

"""
Сервер-апи бота
"""


@APP.route('/' + os.environ.get('BOT_TOKEN'), methods=['POST'])
def webhook_handler():
    """
    Главный путь приема запросов для бота
    """
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = request.get_json()
        print(update)

        if 'callback_query' in update:
            response = button_callback(update['callback_query']['data'], update['callback_query']['message'])
            send_reply(response)
        else:
            message = update['message']
            text = message['text']
            if text[0] == '/':
                command, *arguments = text.split(" ", 1)
                response = CMD.get(command, command_not_found)(arguments, message)
                send_reply(response)
    return 'OK'


@APP.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    """
    Путь для установки вебхука на MyURL/BOT_TOKEN
    """
    # fixme закрыть от внешних доступов?
    set_hook = API.get(os.environ.get('URL') \
                       + "setWebhook?url=%s" % os.environ.get('MyURL') \
                       + os.environ.get('BOT_TOKEN'))
    if set_hook.status_code == 200:
        return "Webhook setup success" \
               + (os.environ.get('URL') \
                  + "setWebhook?url=%s" % os.environ.get('MyURL') \
                  + os.environ.get('BOT_TOKEN'))
    return "Webhook setup failed"


@APP.route('/')
def index():
    """
    Главный роут приложения
    """
    # fixme закрыть от внешних доступов?
    return 'КАМОН, оно завелось кек!'
