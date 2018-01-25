import os
from datetime import datetime
from urllib import request

from commands.Command import Command
from util import USER_TYPE


class CommandAcceptPhoto(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        response = {'chat_id': message['chat']['id']}

        user = users_collection.find_one({"username": message['chat']['username']})
        if user is None:
            if user['user_type'] == USER_TYPE.MASTER.value:
                # TODO: Писать по адресу с работкой
                for file in message['file']:
                    file_path = self.api.post(os.environ.get('URL') + "getFile", data=file['file_id'])
                    url = "https://api.telegram.org/file/bot{}/<file_path>".format(os.environ.get('BOT_TOKEN'), file_path)
                    response = request.urlretrieve(url, file_path)
                response["text"] = "Принято по дате {}".format(datetime.now())
            else:
                response["text"] = "Вам не положено присылать фотографии"
        else:
            response["text"] = "Вам не положено присылать фотографии"
        return response
