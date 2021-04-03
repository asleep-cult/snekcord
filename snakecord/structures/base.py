from ..utils import JsonField, JsonStructure, Snowflake


class BaseObject(JsonStructure):
    __json_fields__ = {
        'id': JsonField('id', Snowflake, str)
    }

    id: Snowflake

    def __eq__(self, other: 'BaseObject') -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return other.id == self.id

    def __hash__(self) -> int:
        return self.id
