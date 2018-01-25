import json
import os

from commands.Command import Command


class CommandAcceptWorkName(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        # users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]

        work = works_collection.find_one_and_update({"_id": arguments[0]},
                                                    {"$set": {"address": message['text']}})

        response = {'chat_id': message['chat']['id'], "text": "Адрес работы задан"}
        works = list(works_collection.find({}))

        keyboard = {'inline_keyboard': [
            [{"text": "Добавить объект", "callback_data": "create_work"}]
        ]}
        for work in works:
            keyboard['inline_keyboard'].append([{"text": work['address'],
                                                 "callback_data": "edit_work:{}".format(work['_id'])}
                                                ])
        response['reply_markup'] = json.dumps(keyboard)

        return response
