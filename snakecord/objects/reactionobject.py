from ..utils import JsonField, JsonTemplate

__all__ = ()

ReactionTemplate = JsonTemplate(
    count=JsonField('count'),
    me=JsonField('me'),
    emoji=JsonField('emoji')
)
