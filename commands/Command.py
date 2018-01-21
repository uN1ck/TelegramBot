from abc import abstractmethod


class Command:
    @abstractmethod
    def __call__(self, arguments: list, message: dict) -> dict:
        pass
