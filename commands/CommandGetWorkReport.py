import os

from bson import ObjectId

from commands.Command import Command


class CommandGetWorkReport(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        # users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        response = {'chat_id': message['chat']['id']}

        work = works_collection.find_one({"_id": ObjectId(arguments[0])})

        # TODO: Upload file logs
        response["text"] = "Работа по адерсу\n{}\nСообщения от бригады:".format(work.address)

        return response
