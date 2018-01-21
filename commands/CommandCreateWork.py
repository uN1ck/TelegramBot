from commands.Command import Command


class CommandCreateWork(Command):
    def __call__(self, arguments: list, message: dict) -> dict:
        # TODO: Set state for user? to new work to be created?
        response = {
            'method': 'editMessageText',
            'inline_message_id': arguments[0],
            'text': "Задайте адрес для работы:",
        }
        return response
