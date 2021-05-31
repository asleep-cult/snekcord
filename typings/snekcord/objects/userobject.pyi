from .baseobject import BaseObject
from ..utils import JsonTemplate, Snowflake

UserTemplate: JsonTemplate = ...

class User(BaseObject[Snowflake]):
    @property
    def mention(self) -> str: ...
