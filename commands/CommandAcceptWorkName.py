import os

from bson import ObjectId

from commands.Command import Command


class CommandAcceptWorkName(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]

        users_collection.find_one_and_update(
            {'username': message['chat']['username']},
            {"$set": {'command': 'accept_password:{}'.format(arguments[0])}})

        work = works_collection.update_one({'_id': ObjectId(arguments[0])},
                                           {'$set': {'address': message['text']}}).raw_result

        response = {'chat_id': message['chat']['id'], 'text': 'Адрес работы задан, введите пароль:'}
        return response
