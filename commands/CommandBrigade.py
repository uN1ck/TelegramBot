import json
import os

from commands.Command import Command
from util import USER_TYPE


class CommandBrigade(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        response = {'chat_id': message['chat']['id']}

        user = users_collection.find_one({"username": message['chat']['username']})
        if user is None:
            user = {
                "username": message['chat']['username'],
                "user_type": USER_TYPE.TEAM.value,
                "chat_id": message['chat']['id'],
                "command": "default"
            }
            users_collection.insert(user)
            response['text'] = "Здравствуйте, {}! Вы зарегистрировались как Бригада. Выберите объект для работы:".format(
                message["from"].get("first_name"))

            works = list(works_collection.find({}))

            keyboard = {'inline_keyboard': [
                [{"text": work['address'], "callback_data": "subscribe_work:{}".format(work['_id'])}] for work in works if
                work['address'] is not None
            ]}
            response['reply_markup'] = json.dumps(keyboard)
        else:
            response["text"] = "Вы уже зарегистрирвоаны, требуется перерегистрация"

        return response
