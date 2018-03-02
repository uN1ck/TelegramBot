from commands.Command import Command


class CommandStart(Command):
    def __init__(self, client, api):
        super().__init__(client, api)

    def __call__(self, arguments: list, message: dict) -> dict:
        response = {'chat_id': message['chat']['id'],
                    'text': "Добро пожаловать!\nДоступные комманды: "
                            "\n1) /manage <секретный ключ> - войти как управляющий "
                            "\n2) /brigade - войти как бригада "
                            "\n3) /exit - выйти из текущей сессии "
                            "\n4) /menu - меню выбора объектов"}
        return response
