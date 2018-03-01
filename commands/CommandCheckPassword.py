import os

from bson import ObjectId

from commands.Command import Command


class CommandCheckPassword(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]

        users_collection.find_one_and_update(
            {'username': message['chat']['username']},
            {"$set": {'command': 'default'}})

        work_password = works_collection.find_one({'_id': ObjectId(arguments[0])})['password']

        response = {'chat_id': message['chat']['id']}
        if message['text'] == work_password:
            user = users_collection.find_one_and_update({'username': message['chat']['username']},
                                                        {'$set': {'command': 'accept_photo:{}'.format(arguments[0])}})
            work = works_collection.find_one_and_update({'_id': ObjectId(arguments[0])},
                                                        {'$set': {'brigade': user['_id']}})

            response['text'] = 'Вы подписаны на работу по адресу:\n{}\nОтправляйте фотографии с объекта в чат:'.format(
                work['address'])
        else:
            response['text'] = 'Пароль не принят'


        return response
