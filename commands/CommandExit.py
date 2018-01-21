import os

from app import CLIENT
from commands.Command import Command


class CommandExit(Command):
    def __call__(self, arguments: list, message: dict) -> dict:
        database = CLIENT[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        users_collection.delete_many({"username": message['chat']['username']})

        response = {'chat_id': message['chat']['id'], 'text': "До свидания, {}!".format(message["from"].get("first_name"))}
        return response
