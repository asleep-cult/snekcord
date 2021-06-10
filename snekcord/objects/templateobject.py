from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .. import rest
from ..utils import JsonField, JsonTemplate, Snowflake, _validate_keys

__all__ = ('GuildTemplate',)

if t.TYPE_CHECKING:
    from .guildobject import Guild
    from .userobject import User
    from ..typing import Json

GuildTemplateTemplate = JsonTemplate(
    id=JsonField('code'),
    name=JsonField('name'),
    description=JsonField('description'),
    usage_count=JsonField('usage_count'),
    creator_id=JsonField('creator_id', Snowflake, str),
    created_at=JsonField(
        'created_at',
        datetime.fromisoformat,
        datetime.isoformat
    ),
    updated_at=JsonField(
        'updated_at',
        datetime.fromisoformat,
        datetime.isoformat
    ),
    source_guild_id=JsonField('source_guild_id', Snowflake, str),
    serialized_source_guild=JsonField('serialized_source_guild'),
    # if someone actually needs this field to be more user friendly...
    # ever... make an issue https://github.com/asleep-cult/snekcord/issues
    is_dirty=JsonField('is_dirty'),
)


class GuildTemplate(BaseObject, template=GuildTemplateTemplate):
    if t.TYPE_CHECKING:
        id: str  # type: ignore
        name: str
        description: t.Optional[str]
        usage_count: int
        creator_id: Snowflake
        created_at: datetime
        updated_at: datetime
        source_guild_id: Snowflake
        serialized_source_guild: Json
        is_dirty: t.Optional[bool]

    @property
    def code(self) -> str:
        return self.id

    @property
    def creator(self) -> t.Optional[User]:
        return self.state.client.users.get(self.creator_id)

    @property
    def source_guild(self) -> t.Optional[Guild]:
        return self.state.client.guilds.get(self.source_guild_id)

    async def fetch(self) -> GuildTemplate:
        data = await rest.get_template.request(
            session=self.state.client.rest,
            fmt=dict(code=self.code))

        self.update(data)

        return self

    async def create_guild(self, **kwargs: t.Any) -> Guild:
        _validate_keys(  # type: ignore
            f'{self.__class__.__name__}.create_guild',
            kwargs, ('name',),
            rest.create_guild_from_template.json
        )

        data = await rest.create_guild_from_template.request(
            session=self.state.client.rest,
            fmt=dict(template_code=self.code),
            json=kwargs)

        return self.state.client.guilds.upsert(data)

    async def sync(self):
        data = await rest.sync_guild_template.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.source_guild_id,
                     template_code=self.code))

        self.update(data)

        return self

    async def modify(self, **kwargs: t.Any) -> GuildTemplate:
        _validate_keys(f'{self.__class__.__name__}.modify',  # type: ignore
                       kwargs, (), rest.modify_guild_template.json)

        data = await rest.modify_guild_template.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.source_guild_id,
                     template_code=self.code),
            json=kwargs)

        self.update(data)

        return self

    async def delete(self) -> None:
        await rest.delete_guild_template.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.source_guild_id,
                     template_code=self.code))

    def update(  # type: ignore
        self, data: Json,
        *args: t.Any, **kwargs: t.Any
    ) -> None:
        super().update(data, *args, **kwargs)

        creator = data.get('creator')
        if creator is not None:
            self.state.client.users.upsert(creator)
