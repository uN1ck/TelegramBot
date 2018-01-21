from abc import abstractmethod


class Command:
    def __init__(self, client, api):
        self.client = client
        self.api = api

    @abstractmethod
    def __call__(self, arguments: list, message: dict) -> dict:
        pass
