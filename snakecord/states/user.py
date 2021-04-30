from .base import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from ..objects.user import User


class UserState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __user_class__ = User

    @classmethod
    def set_user_class(cls, klass: type) -> None:
        cls.__user_class__ = klass

    def append(self, data: dict, *args, **kwargs) -> User:
        user = self.get(data['id'])
        if user is not None:
            user._update(data)
        else:
            user = self.__user_class__.unmarshal(
                data, state=self, *args, **kwargs)
            user.cache()

        return user
