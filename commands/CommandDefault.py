from commands.Command import Command


class CommandDefault(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        response = {'chat_id': message['chat']['id'],
                    'text': "К сожалению такой команды не существует (либо она не реализована) :( "}
        return response
