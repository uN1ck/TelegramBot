"""Главный модуль приложения

Данный модуль отвечает за обработку комманд, присланных пользователями телеграм-боту

"""
import os
from enum import Enum

import requests
from flask import Flask
from flask import request
from pymongo import MongoClient

from commands.CommandBrigade import CommandBrigade
from commands.CommandExit import CommandExit
from commands.CommandMaster import CommandMaster

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
    data = [line for line in data.split(':') if line.strip() != '']
    response = CMD.get(data[0], command_not_found)(data[1:], message)
    return response


PUBLIC_CMD = {
    '/управление': CommandMaster(),
    '/бригада': CommandBrigade(),
    '/выход': CommandExit(),
}
PRIVATE_CMD = {
    'create_work': None,
    'edit_work': None,
    'delete_work': None,

    'subscribe_work': None,
    'finish_work': None,
    'get_work_info': None,
    'get_work_report': None
}

CMD = PRIVATE_CMD.copy()
CMD.update(PRIVATE_CMD)

"""
Сервер-апи бота
"""


@APP.route('/' + os.environ.get('BOT_TOKEN'), methods=['POST'])
def webhook_handler():
    """
    Главный путь приема запросов для бота
    """
    if request.method == "POST":
        update = request.get_json()
        try:
            # retrieve the message in JSON and then transform it to Telegram object
            print("Update JSON data:{}".format(update))
            if 'callback_query' in update:
                response = button_callback(update['callback_query']['data'], update['callback_query']['message'])
                send_reply(response)
            else:
                message = update['message']
                text = message['text']
                if text[0] == '/':
                    command, *arguments = text.split(" ", 1)
                    response = PUBLIC_CMD.get(command, command_not_found)(arguments, message)
                    send_reply(response)
        except Exception as ex:
            print(ex)
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
