import json
import os

from commands.Command import Command
from util import USER_TYPE


class CommandMenu(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        works_collection = database[os.environ.get('MONGO_COLLECTION_WORKS')]

        response = {'chat_id': message['chat']['id'], 'text': ''}
        works = list(works_collection.find({}))
        user = users_collection.find_one({'username': message['chat']['username']})
        if user['user_type'] == USER_TYPE.MASTER.value:
            keyboard = {'inline_keyboard': [[{'text': 'Добавить объект', 'callback_data': 'create_work'}]]}
            for work in works:
                if work['address'] is not None:
                    keyboard['inline_keyboard'].append(
                        [{'text': work['address'], 'callback_data': 'edit_work:{}'.format(work['_id'])}])
            response['reply_markup'] = json.dumps(keyboard)
        elif user['user_type'] == USER_TYPE.TEAM.value:

            keyboard = {'inline_keyboard': [
                [{'text': work['address'], 'callback_data': 'subscribe_work:{}]'.format(work['_id'])}] for work in works
            ]}
            response['reply_markup'] = json.dumps(keyboard)
        else:
            response['text'] = 'Нельзя использовать эту комманду'

        return response
