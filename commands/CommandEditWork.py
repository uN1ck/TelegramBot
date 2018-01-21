import json
import os

from commands.Command import Command


class CommandEditWork(Command):
    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]

        work_id = arguments[0]
        work = works_collection.find({'_id': work_id})

        keyboard = {'inline_keyboard':
            [
                [{"text": "Отчет", "callback_data": "get_report:{}".format(work_id)}],
                [{"text": "Удалить", "callback_data": "delete_work:{}".format(work_id)}]
            ]}
        response = {'chat_id': message['chat']['id'], 'text': "{}".format(work['address']), 'reply_markup': json.dumps(keyboard)}
        return response
