import os

from commands.CommandDefault import CommandDefault
from models.UserModel import UserModel


class CommandRouter:
    commands = {}
    default_commands = {}

    def __init__(self, client, api, commands: dict, default_commands: dict):
        self.client = client
        self.api = api
        self.commands = commands
        self.default_commands = default_commands
        self.commands.update(default_commands)

        self._default_command = CommandDefault(client, api)

    def route(self, update):
        # fixme accept state, not tuple
        allowed_commands, context_command = self._get_allowed_commands(update['chat']['username'])

        if 'callback_query' in update:
            data = update['callback_query']['data']
            data = [line for line in data.split(':') if line.strip() != '']
            message = update['callback_query']['message']
        else:
            message = update['message']
            data = message['text'].split(" ")
            if context_command is None:

                response = context_command(data[1:], message)

        response = allowed_commands.get(data[0], self._default_command)(data[1:], message)
        return response

    def _get_allowed_commands(self, username: str) -> tuple:  # fixme return object, not tuple!
        database = self.client[os.environ.get('MONGO_DBNAME')]
        users_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]

        user = UserModel.from_dict(users_collection.find_one({'username': username}))
        allowed_commands = self.default_commands.copy()
        if user is not None:
            for command in user.context_command:
                allowed_commands[command] = self.commands[command]

        return allowed_commands, self.commands.get(user.context_command, None)
