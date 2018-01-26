from enum import Enum


class USER_TYPE(Enum):
    TEAM = 0
    MASTER = 1


class WorkModel:
    def __init__(self, master: str, address: str, brigade: str = None):
        self.master = master
        self.address = address
        self.brigade = brigade


class UserModel:
    def __init__(self, id: str, user_type: USER_TYPE):
        self.id = id
        self.user_type = user_type
