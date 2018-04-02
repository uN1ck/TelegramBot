import os
from datetime import datetime

import yadisk
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
                    if not self._save_photo(message, work['address'], response, arguments):
                        response["text"] = "Не удалось сохранить фото, попробуйте еще раз"
                    else:
                        works_collection.find_one_and_update({"_id": ObjectId(arguments[0])},
                                                             {'$set': {'photo_count': work['photo_count'] + 1}})
                if 'text' in message:
                    works_collection.find_one_and_update({"_id": ObjectId(arguments[0])},
                                                         {'$set': {'messages': work['messages'] +
                                                                               ["{} -> {}".format(
                                                                                   datetime.now().strftime("%Y-%m-%d %H:%I:%S"),
                                                                                   message['text'])]}})
                if 'debug' not in response:
                    response["text"] = "Принято по дате {}".format(datetime.now().date())
            else:
                response['debug'] = [user['user_type'], USER_TYPE.MASTER.value]
                response["text"] = "Вам не положено присылать фотографии"
        else:
            response["text"] = "Вам не положено присылать фотографии"
        return response

    def _save_photo(self, message, work_name, response, arguments):
        try:
            file = message['photo'][3]
            file_response = self.api.post(os.environ.get('URL') + "getFile",
                                          data={'file_id': file['file_id']}).json()
            response['debug'] = {'arguments': arguments, 'response': file_response['result']}
            download_link = "https://api.telegram.org/file/bot{}/{}".format(os.environ.get('BOT_TOKEN'),
                                                                            file_response['result']['file_path'])
            database = self.client[os.environ.get('MONGO_DBNAME')]
            works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]

            works_collection.find_one_and_update({"_id": ObjectId(arguments[0])},
                                                 {'$push': {'photo_dates': file_response['result']['file_path']}})

            yd = yadisk.YaDisk(os.environ.get('YA_ID'), os.environ.get('YA_SECRET'), os.environ.get('YA_TOKEN'))
            if not yd.exists('/{}'.format(work_name)):
                yd.mkdir('/{}'.format(work_name))
            date_now = str(datetime.now().date())
            if not yd.exists('/{}/{}/'.format(work_name, date_now)):
                yd.mkdir('/{}/{}/'.format(work_name, date_now))

            filename = "{}.{}".format(datetime.now().strftime('%H %M %S'), file_response['result']['file_path'].split('.')[-1])
            yd.upload_url(download_link, '/{}/{}/{}'.format(work_name, date_now, filename))
        except Exception as ex:
            return False
        return True
