import os

from commands.Command import Command


class CommandAcceptWorkName(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        work = works_collection.find_one_and_update({"master": message['chat']['username']},
                                                    {"$set": {"address": message['text']}})
        users_collection.find_one_and_update({'username': message['chat']['username']},
                                             {"$set": {'command': 'accept_photo:{}'.format(work['_id'])}})
        response = {'chat_id': message['chat']['id'],
                    "text": "Вы подписаны на работу по адресу:\n{}\nОтправляйте фотографии с объекта в чат:".format(
                        work['address'])}

        return response
