from .base import BaseState, SnowflakeMapping
from ..objects.user import User

class UserState(BaseState):
    __container__ = SnowflakeMapping
    __user_class__ = User

    @classmethod
    def set_user_class(cls, class_: type) -> None:
        cls.__user_class__ = class_

    def append(self, data: dict, *args, **kwargs) -> User:
        user = self.get(data['id'])
        if user is not None:
            user._update(data)
        else:
            user = self.__user_class__.unmarshal(data, state=self, *args, **kwargs)
            self[user.id] = user

        return user
