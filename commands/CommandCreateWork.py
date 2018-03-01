import os

from commands.Command import Command


class CommandCreateWork(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]

        work = {
            "master": message['chat']['username'],
            "address": None,
            "brigade": None,
            "photo_count": 0,
            "messages": [],
            "password": "password",
        }
        result = works_collection.insert_one(work)
        users_collection.find_one_and_update(
            {'username': message['chat']['username']},
            {"$set": {'command': 'accept_work_name:{}'.format(result.inserted_id)}})
        response = {
            'chat_id': message['chat']['id'],
            'text': 'Задайте адрес для работы и кодовое слово в формате "<название>!<кодовое слово>" ',
        }
        return response
