import os
from abc import abstractmethod


class Command:
    def __init__(self, client, api):
        self.client = client
        self.api = api

    @abstractmethod
    def __call__(self, arguments: list, message: dict) -> dict:
        pass

    def command_lasts_instance(self, user_id) -> None:
        """ Свойсвто для получения инстанца следующей комманды.

        Используется для того, чтобы была возможнсоть у клиента отвечать на вопросы сервера.
        Возвращает инстанс комманды обязательной к выполеннию после завершения выполнения текущей.

        Если текущая комманда не подразумаевает обязательного выполнения комманды после себя

        :return: None
        """
        database = self.client[os.environ.get('MONGO_DBNAME')]
        states_collection = database[os.environ.get('MONGO_COLLECTION_USERS')]
        states_collection.insert({"username": user_id, "command": "/default"})
