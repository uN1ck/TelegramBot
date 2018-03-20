import os

from app import CLIENT, API


def notify():
    database = CLIENT[os.environ.get('MONGO_DBNAME')]
    users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]

    users = list(users_collection.find({}))

    for item in users:
        response = {
            'chat_id': item["chat_id"],
            'text': "Не забудьте выставить фотографии!"
        }
        API.post(os.environ.get('URL') + "sendMessage", data=response)

notify()