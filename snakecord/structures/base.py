from ..utils import JsonField, JsonStructure, Snowflake


class BaseObject(JsonStructure):
    __json_fields__ = {
        'id': JsonField('id', Snowflake, str)
    }

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.id == self.id
