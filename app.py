"""Главный модуль приложения

Данный модуль отвечает за обработку комманд, присланных пользователями телеграм-боту

"""
import os

import requests
from flask import Flask
from flask import request
from pymongo import MongoClient

from commands.CommandAcceptPhoto import CommandAcceptPhoto
from commands.CommandAcceptWorkName import CommandAcceptWorkName
from commands.CommandBrigade import CommandBrigade
from commands.CommandCreateWork import CommandCreateWork
from commands.CommandDefault import CommandDefault
from commands.CommandDeleteWork import CommandDeleteWork
from commands.CommandEditWork import CommandEditWork
from commands.CommandExit import CommandExit
from commands.CommandGetWorkReport import CommandGetWorkReport
from commands.CommandMaster import CommandMaster
from commands.CommandMenu import CommandMenu
from commands.CommandSubscribeWork import CommandSubscribeWork

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
    '/меню': CommandMenu(CLIENT, API),
}
PRIVATE_CMD = {
    'default': CommandDefault(CLIENT, API),

    'create_work': CommandCreateWork(CLIENT, API),
    'edit_work': CommandEditWork(CLIENT, API),
    'delete_work': CommandDeleteWork(CLIENT, API),

    'subscribe_work': CommandSubscribeWork(CLIENT, API),
    'finish_work': CommandDefault(CLIENT, API),  # fixme
    'get_work_report': CommandGetWorkReport(CLIENT, API),

    'accept_work_name': CommandAcceptWorkName(CLIENT, API),
    'accept_photo': CommandAcceptPhoto(CLIENT, API),

    'work_list': CommandDefault(CLIENT, API),  # fixme
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
    data = [line for line in data.split(':') if line.strip() != '']
    print("CALLBACK: {}".format(data))
    response = CMD.get(data[0], PRIVATE_CMD['default'])(data[1:], message)
    print("RESPONSE: {}".format(response))
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
            print(" --> Update JSON data:{}".format(update))
            if 'callback_query' in update:
                response = button_callback(update['callback_query']['data'], update['callback_query']['message'])
                send_reply(response)
            else:
                message = update['message']
                if 'text' in message:
                    text = message['text']
                    if text[0] == '/':
                        command, *arguments = text.split(" ", 1)
                        response = PUBLIC_CMD.get(command, PRIVATE_CMD['default'])(arguments, message)
                        send_reply(response)
                if 'photo' in message or 'text' in message:
                    database = CLIENT[os.environ.get('MONGO_DBNAME')]
                    users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
                    command = users_collection.find_one({'username': message['chat']['username']})['command']
                    if ':' in command:
                        command = command.split(':')
                    print("@COMMAND: {}".format(command))
                    response = CMD.get(command[0], PRIVATE_CMD['default'])(command[1:], message)
                    print("@RESPONSE: {}".format(response))
                    send_reply(response)
                # elif 'photo' in message:
                #     response = CommandAcceptPhoto(CLIENT, API)([], message)
                #     send_reply(response)

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
