import json
import os

from commands.Command import Command


class CommandGetWorkReport(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        response = {'chat_id': message['chat']['id']}

        user = users_collection.find_one({"username": message['chat']['username']})
        work = works_collection.find_one_and_update({"_id": arguments[0]}, {"brigade": user._id})
        response["text"] = "Вы подписаны на работу по адресу:\n{}\nОтправляйте фотографии с объекта в чат:".format(work.address)

        keyboard = {'inline_keyboard': [
            [{"text": "Добавить объект",
              "callback_data": "work_list:{}".format(user['_id'])}  # fixme
             ]]
        }
        response['reply_markup'] = json.dumps(keyboard)

        return response
