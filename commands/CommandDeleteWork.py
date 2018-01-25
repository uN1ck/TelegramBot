import os

from commands.Command import Command


class CommandDeleteWork(Command):
    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]

        work_id = arguments[0]
        work = works_collection.find_one_and_delete(work_id)

        if work is not None:
            response = {
                'chat_id': message['chat']['id'],
                'text': "Работа по адресу:\n{}\n Успешно удалена".format(work['address']),
            }
        else:
            response = {
                'chat_id': message['chat']['id'],
                'text': "Работа не найдена",
            }
        return response
