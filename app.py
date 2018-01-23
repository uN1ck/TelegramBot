"""Главный модуль приложения

Данный модуль отвечает за обработку комманд, присланных пользователями телеграм-боту

"""
import os

import requests
from flask import Flask
from flask import request
from pymongo import MongoClient

from commands.CommandBrigade import CommandBrigade
from commands.CommandCreateWork import CommandCreateWork
from commands.CommandDefault import CommandDefault
from commands.CommandEditWork import CommandEditWork
from commands.CommandExit import CommandExit
from commands.CommandMaster import CommandMaster

API = requests.Session()
APP = Flask(__name__)
CLIENT = MongoClient(os.environ.get('MONGODB_URI'))

"""
Возможные комманды бота
"""

PUBLIC_CMD = {
    '/управление': CommandMaster(CLIENT, API),
    '/бригада': CommandBrigade(CLIENT, API),
    '/выход': CommandExit(CLIENT, API),
}
PRIVATE_CMD = {
    'default': CommandDefault(CLIENT, API),

    'create_work': CommandCreateWork(CLIENT, API),
    'edit_work': CommandEditWork(CLIENT, API),  # fixme
    'delete_work': CommandDefault(CLIENT, API),  # fixme

    'subscribe_work': CommandDefault(CLIENT, API),  # fixme
    'finish_work': CommandDefault(CLIENT, API),  # fixme
    'get_work_report': CommandDefault(CLIENT, API),  # fixme
}

CMD = PRIVATE_CMD.copy()
CMD.update(PRIVATE_CMD)


def send_reply(response):
    """
    Функция отправки сообщения ботом пользователю
        :param response: сформированный объект ответа бота для API телеграмма
    """
    if 'method' in response:
        API.post(os.environ.get('URL') + response['method'], data=response)
    elif 'text' in response:
        API.post(os.environ.get('URL') + "sendMessage", data=response)


def button_callback(data, message):
    """
    Обработчик всех кнопок бота
        :param data: data вернувшаяся с кнопки (callback_data)
        :param message: Объект полученного сообщения от пользователя
    """
    response = {'chat_id': message['chat']['id']}
    data = [line for line in data.split(':') if line.strip() != '']
    response = CMD.get(data[0], PRIVATE_CMD['default'])(data[1:], message)
    return response


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
                    response = PUBLIC_CMD.get(command, PRIVATE_CMD['default'])(arguments, message)
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
