from ..utils import JsonField, JsonTemplate


WebSocketResponse = JsonTemplate(
    opcode=JsonField('op'),
    sequence=JsonField('s'),
    name=JsonField('t'),
    data=JsonField('d'),
).default_object('WebSocketResponse')
