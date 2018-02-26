import os
from datetime import datetime

from PIL import Image
from bson import ObjectId

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
        work = works_collection.find_one({"_id": ObjectId(arguments[0])})

        if user is not None:
            if user['user_type'] == USER_TYPE.TEAM.value:

                if 'photo' in message:
                    response['debug'] = self._save_photo(message)  # fixme implement

                    works_collection.find_one_and_update({"_id": ObjectId(arguments[0])},
                                                         {'$set': {'photo_count': work['photo_count'] + 1}})
                elif 'text' in message:
                    works_collection.find_one_and_update({"_id": ObjectId(arguments[0])},
                                                         {'$set': {'messages': work['messages'] + [message['text']]}})
                response["text"] = "Принято по дате {}".format(datetime.now().date())
            else:
                response['debug'] = [user['user_type'], USER_TYPE.MASTER.value]
                response["text"] = "Вам не положено присылать фотографии"
        else:
            response["text"] = "Вам не положено присылать фотографии"
        return response

    def _save_photo(self, message):
        file = message['photo'][3]
        file_response = self.api.post(os.environ.get('URL') + "getFile",
                                      data={'file_id': file['file_id']}).json()
        img = self.api.get(
            "https://api.telegram.org/file/bot{}/{}".format(os.environ.get('BOT_TOKEN'), file_response['result']['file_path']),
            stream=True)

        img.raw.decode_content = True
        im = Image.open(img.raw)
        q = None
        try:

            def _send_request(type, addUrl="/", addHeaders={}, data=None):
                headers = {"Accept": "*/*"}
                headers.update(addHeaders)
                url = "https://webdav.yandex.ru/" + addUrl
                from requests import request
                return request(type, url, headers=headers, auth=(os.environ.get('YA_LOGIN'), os.environ.get('YA_PASSWORD')),
                               data=data)

            q = _send_request("PUT", '/', data=img)
        except Exception as ex:
            q = ex
        resp = [im.format, im.mode, im.size, q]
        return resp
