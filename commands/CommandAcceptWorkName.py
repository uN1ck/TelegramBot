import os

from commands.Command import Command


class CommandAcceptWorkName(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]

        if works_collection.find({'address': message['text']}) is None:

            work = {
                "master": message['chat']['username'],
                "address": message['text'],
                "brigade": None,
                "photo_count": 0,
                "messages": [],
                "password": "password",
            }
            result = works_collection.insert_one(work)

            users_collection.find_one_and_update(
                {'username': message['chat']['username']},
                {"$set": {'command': 'accept_password:{}'.format(result)}})
            response = {'chat_id': message['chat']['id'], 'text': 'Адрес работы задан, введите пароль:'}
        else:

            response = {'chat_id': message['chat']['id'], 'text': 'Такой адрес уже существует, введите другой'}
        return response
