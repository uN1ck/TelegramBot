import os

from bson import ObjectId

from commands.Command import Command


class CommandSubscribeWork(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]

        response = {'chat_id': message['chat']['id']}

        user = users_collection.update_one({"username": message['chat']['username']},
                                           {{"$set": {'command': 'accept_photo:{}'.format(arguments[0])}}})
        work = works_collection.update_one({"_id": ObjectId(arguments[0])},
                                           {"brigade": user['_id']})
        response["text"] = "Вы подписаны на работу по адресу:\n{}\nОтправляйте фотографии с объекта в чат:".format(
            work['address'])

        return response
