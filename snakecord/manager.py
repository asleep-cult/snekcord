from .connections.rest import RestSession
from .states.channel import ChannelState, GuildChannelState
from .states.emoji import GuildEmojiState
from .states.guild import GuildState
from .states.member import GuildMemberState
from .states.message import ChannelMessageState
from .states.reaction import MessageReactionState
from .states.reaction import MessageReactionState
from .states.role import RoleState
from .states.user import UserState
from .utils.events import EventDispatcher


class BaseManager(EventDispatcher):
    __rest_session_class__ = RestSession
    __channel_state_class__ = ChannelState
    __guild_channel_state_class__ = GuildChannelState
    __guild_emoji_state_class__ = GuildEmojiState
    __guild_state_class__ = GuildState
    __guild_member_state_class__ = GuildMemberState
    __channel_message_state_class__ = ChannelMessageState
    __message_reaction_state_class__ = MessageReactionState
    __guild_role_state_class__ = RoleState
    __user_state_clsas__ = UserState

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = self.__user_state_clsas__(manager=self)
        self.rest = self.__rest_session_class__(manager=self)
        self.guilds = self.__guild_state_class__(manager=self)
        self.channels = self.__channel_state_class__(manager=self)

    @classmethod
    def set_rest_session_class(cls, klass) -> None:
        assert issubclass(klass, RestSession)
        cls.__rest_session_class__ = klass

    @classmethod
    def set_channel_state_class(cls, klass) -> None:
        assert issubclass(klass, ChannelState)
        cls.__channel_state_class__ = klass

    @classmethod
    def set_guild_channel_state_class(cls, klass) -> None:
        assert issubclass(klass, GuildChannelState)
        cls.__guild_channel_state_class__ = klass

    @classmethod
    def set_guild_emoji_state_class(cls, klass) -> None:
        assert issubclass(klass, GuildEmojiState)
        cls.__guild_emoji_state_class__ = klass

    @classmethod
    def set_guild_state_class(cls, klass) -> None:
        assert issubclass(klass, GuildState)
        cls.__guild_state_class__ = klass

    @classmethod
    def set_guild_member_state_class(cls, klass) -> None:
        assert issubclass(klass, GuildMemberState)
        cls.__guild_member_state_class__ = klass

    @classmethod
    def set_channel_message_state_class(cls, klass) -> None:
        assert issubclass(klass, ChannelMessageState)
        cls.__channel_message_state_class__ = klass

    @classmethod
    def set_message_reaction_state_class(cls, klass) -> None:
        assert issubclass(klass, MessageReactionState)
        cls.__message_reaction_state_class__ = klass

    @classmethod
    def set_guild_role_state_class(cls, klass) -> None:
        assert issubclass(klass, GuildRoleState)
        cls.__guild_role_state_class__ = klass

    @classmethod
    def set_user_state_class(cls, klass) -> None:
        assert issubclass(klass, UserState)
        cls.__user_state_clsas__ = klass
