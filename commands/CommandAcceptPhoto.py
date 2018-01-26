import os
from datetime import datetime
from urllib import request

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
                photo_count = 0
                for file in message['photo']:
                    file_path = self.api.post(os.environ.get('URL') + "getFile", data=file['file_id'])
                    url = "https://api.telegram.org/file/bot{}/{}".format(os.environ.get('BOT_TOKEN'), file_path)

                    current_directory = os.getcwd()
                    final_directory = os.path.join(current_directory, r'photo_{}_{}'.format(datetime.now(), work['address']))
                    if not os.path.exists(final_directory):
                        os.makedirs(final_directory)
                        response['debug'] = [current_directory, "dir_created"]
                    response['debug'] = [current_directory]

                    try:
                        response['debug'] += [request.urlretrieve(url, file_path)]
                    except Exception as ex:
                        response['debug'] += [ex]

                works_collection.find_one_and_update({"_id": ObjectId(arguments[0])},
                                                     {'$set': {'photo_count': work['photo_count'] + photo_count}})

                response["text"] = "Принято по дате {}".format(datetime.now())
            else:
                response['debug'] = [user['user_type'], USER_TYPE.MASTER.value]
                response["text"] = "Вам не положено присылать фотографии"
        else:
            response["text"] = "Вам не положено присылать фотографии"
        return response
