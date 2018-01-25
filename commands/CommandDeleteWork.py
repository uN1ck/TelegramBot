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

        keyboard = {'inline_keyboard': [
            [{"text": "Отчет", "callback_data": "get_report:{}".format(work_id)},
             {"text": "Удалить", "callback_data": "delete_work:{}".format(work_id)}]
        ]}

        if work is not None:
            response = {
                'reply_markup': json.dumps(keyboard),
                'chat_id': message['chat']['id'],
                'text': "Работа по адресу:\n{}\n Успешно удалена".format(work['address']),
            }
        else:
            response = {
                'reply_markup': json.dumps(keyboard),
                'chat_id': message['chat']['id'],
                'text': "Работа не найдена",
            }
        return response
