import json
import os

from bson import ObjectId

from commands.Command import Command


class CommandDeleteWork(Command):
    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]

        work_id = arguments[0]
        work = works_collection.find_one_and_delete({'_id': ObjectId(work_id)})

        response = {'chat_id': message['chat']['id']}
        works = list(works_collection.find({}))
        keyboard = {'inline_keyboard': [[{"text": "Добавить объект", "callback_data": "create_work"}]]}
        for work in works:
            if work['address'] is not None:
                keyboard['inline_keyboard'].append([
                    {"text": work['address'],
                     "callback_data": "edit_work:{}".format(work['_id'])}
                ])
        response['reply_markup'] = json.dumps(keyboard)

        if work is not None:
            response['text'] = "Работа по адресу:\n{}\nУспешно удалена".format(work['address'])
        else:
            response['text'] = "Работа не найдена"
        return response
