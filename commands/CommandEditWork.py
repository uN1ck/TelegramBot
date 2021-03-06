import json
import os
from datetime import datetime

from bson import ObjectId

from commands.Command import Command
from commands.CommandMenu import CommandMenu


class CommandEditWork(Command):
    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]

        work_id = arguments[0]
        work = works_collection.find_one({'_id': ObjectId(work_id)})

        if work is None:
            response = CommandMenu(self.client, self.api)(arguments, message)
        else:
            response = {'chat_id': message['chat']['id']}
            works_list = [datetime.strptime(item.split('|')[0], '%Y-%m-%d') for item in work['photo_dates']]
            works_set = set(works_list)

            keyboard = {'inline_keyboard': None}
            response['debug'] = keyboard
            try:
                keyboard['inline_keyboard'] = [
                    *[[{"text": item.strftime('%Y-%m-%d'),
                        "callback_data": "return_photo_by_date:{}:{}".format(item.strftime('%Y-%m-%d'), arguments[0])}]
                      for item in works_set],
                    [{"text": "Отчет", "callback_data": "get_work_report:{}".format(work_id)}],
                    [{"text": "Удалить", "callback_data": "delete_work:{}".format(work_id)}]
                ]

                response['reply_markup'] = json.dumps(keyboard)
            except Exception as ex:
                response['debug_ex'] = {'ex': ex}
            response['text'] = "Работа по адресу:\n{}\nФотографий: {}".format(work['address'], work['photo_count']),

        return response
