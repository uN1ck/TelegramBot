import json
import os

from bson import ObjectId

from commands.Command import Command


class CommandGetWorkReport(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        # users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        response = {'chat_id': message['chat']['id']}

        work = works_collection.find_one({"_id": ObjectId(arguments[0])})
        keyboard = {'inline_keyboard': [
            [{"text": "Меню", "callback_data": "/меню"}]
        ]}
        response['reply_markup'] = json.dumps(keyboard)
        response["text"] = "Работа по адерсу\n{}\nСообщения от бригады:\n{}".format(work['address'], "\n".join(work['messages']))
        return response
