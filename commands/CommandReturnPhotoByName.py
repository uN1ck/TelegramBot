import os

from bson import ObjectId

from commands.Command import Command


class CommandReturnPhotoByName(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        response = {'chat_id': message['chat']['id']}

        work_id = arguments[1]
        work = works_collection.find_one({'_id': ObjectId(work_id)})

        works_list = [item.split('|') for item in work['photo_dates'] if item.split('|')[0] == arguments[0]]
        response['series'] = [{'method': 'sendPhoto', 'photo_id':item} for item in works_list]

        return response
