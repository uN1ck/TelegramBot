import os

from commands.Command import Command


class CommandSubscribeWork(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]

        response = {'chat_id': message['chat']['id']}
        users_collection.find_one_and_update(
            {'username': message['chat']['username']},
            {"$set": {'command': 'check_password:{}'.format(arguments[0])}})

        response = {'chat_id': message['chat']['id'], 'text': 'Введите пароль:'}

        return response
