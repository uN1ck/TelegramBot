import os

from commands.Command import Command


class CommandExit(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        users_collection.delete_many({"username": message['chat']['username']})

        response = {'chat_id': message['chat']['id'], 'text': "До свидания, {}!".format(message["from"].get("first_name"))}
        return response
