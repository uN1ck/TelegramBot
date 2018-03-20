import os

from app import CLIENT, API
from util import USER_TYPE


def notify():
    database = CLIENT[os.environ.get('MONGO_DBNAME')]
    users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]

    users = list(users_collection.find({"user_type": USER_TYPE.TEAM.value}))

    for item in users:
        response = {
            'chat_id': item["chat_id"],
            'text': "Не забудьте выставить фотографии!"
        }
        API.post(os.environ.get('URL') + "sendMessage", data=response)

notify()