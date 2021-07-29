from urllib.parse import urlencode

from . import rest

VALID_SIZES = tuple(sqrt ** 2 for sqrt in range(4, 65))
VALID_FORMATS = ('png', 'jpg', 'jpeg', 'webp', 'gif')


def _validate_size(size):
    if size not in VALID_SIZES:
        raise ValueError(
            f'{size!r} is not a valid size (sizes must be a power of 2 between 16 and 4096)'
        )


def _validate_format(format):
    if format not in VALID_FORMATS:
        raise ValueError(
            f'{format!r} is not a valid format (should be one of {", ".join(VALID_FORMATS)}'
        )


class Fetchable:
    def __init__(self, rest):
        self.rest = rest

    def __str__(self):
        return self.url()

    def _form_url(self, **kwargs):
        # This is very... very... lazy :)
        keywords = {}

        for keyword in self.ENDPOINT.keywords:
            try:
                keywords[keyword] = kwargs.pop(keyword)
            except KeyError:
                keywords[keyword] = getattr(self, keyword)

        url = self.ENDPOINT.url.format(**keywords)

        params = {k: v for k, v in kwargs.items() if v is not None}

        if params:
            url += f'?{urlencode(params)}'

        return url

    def url(self):
        raise NotImplementedError

    def fetch(self, **kwargs):
        return self.rest.request('GET', self.url(**kwargs))


class GuildIcon(Fetchable):
    ENDPOINT = rest.get_guild_icon

    def __init__(self, rest, guild_id, guild_icon):
        super().__init__(rest)

        self.guild_id = guild_id
        self.guild_icon = guild_icon

    @property
    def animated(self):
        return self.guild_icon.startswith('a_')

    def url(self, *, format=None, size=None):
        if size is not None:
            _validate_size(size)

        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            if self.animated:
                format = 'gif'
            else:
                format = 'png'

        return self._form_url(format=format, size=size)


class GuildSplash(Fetchable):
    ENDPOINT = rest.get_guild_splash

    def __init__(self, rest, guild_id, guild_splash):
        super().__init__(rest)

        self.guild_id = guild_id
        self.guild_splash = guild_splash

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if size is not None:
            _validate_size(size)

        return self._form_url(format=format, size=size)


class GuildDiscoverySplash(Fetchable):
    ENDPOINT = rest.get_guild_discovery_splash

    def __init__(self, rest, guild_id, guild_discovery_splash):
        super().__init__(rest)

        self.guild_id = guild_id
        self.guild_discovery_splash = guild_discovery_splash

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if size is not None:
            _validate_size(size)

        return self._form_url(format=format, size=size)


class GuildBanner(Fetchable):
    ENDPOINT = rest.get_guild_banner

    def __init__(self, rest, guild_id, guild_banner):
        super().__init__(rest)

        self.guild_id = guild_id
        self.guild_banner = guild_banner

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if size is not None:
            _validate_size(size)

        return self._form_url(format=format, size=size)


class DefaultUserAvatar(Fetchable):
    ENDPOINT = rest.get_default_user_avatar

    def __init__(self, rest, user_discriminator):
        super().__init__(rest)

        self.user_discriminator = user_discriminator

    def url(self, format=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        return self._form_url(user_discriminator=self.user_discriminator % 5)


class UserAvatar(Fetchable):
    ENDPOINT = rest.get_user_avatar

    def __init__(self, rest, user_id, user_avatar):
        super().__init__(rest)

        self.user_id = user_id
        self.user_avatar = user_avatar

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if size is not None:
            _validate_size(size)

        return self._form_url(format=format, size=size)


class ApplicationIcon(Fetchable):
    ENDPOINT = rest.get_application_icon

    def __init__(self, rest, application_id, application_icon):
        super().__init__(rest)

        self.application_id = application_id
        self.application_icon = application_icon

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if size is not None:
            _validate_size(size)

        return self._form_url(format=format, size=size)


class ApplicationCover(Fetchable):
    ENDPOINT = rest.get_application_cover

    def __init__(self, rest, application_id, application_cover_image):
        super().__init__(rest)

        self.application_id = application_id
        self.application_cover_image = application_cover_image

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if size is not None:
            _validate_size(size)

        return self._form_url(format=format, size=size)


class ApplicationAsset(Fetchable):
    ENDPOINT = rest.get_application_asset

    def __init__(self, rest, application_id, application_asset):
        super().__init__(rest)

        self.application_id = application_id
        self.application_asset = application_asset

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if size is not None:
            _validate_size(size)

        return self._form_url(format=format, size=size)


class AchievementIcon(Fetchable):
    ENDPOINT = rest.get_achievement_icon

    def __init__(self, rest, application_id, achievement_id, achievement_icon):
        super().__init__(rest)

        self.application_id = application_id
        self.achievement_id = achievement_id
        self.achievement_icon = achievement_icon

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if size is not None:
            _validate_size(size)

        return self._form_url(format=format, size=size)


class TeamIcon(Fetchable):
    ENDPOINT = rest.get_team_icon

    def __init__(self, rest, team_id, team_icon):
        super().__init__(rest)

        self.team_id = team_id
        self.team_icon = team_icon

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if size is not None:
            _validate_size(size)

        return self._form_url(format=format, size=size)


class GuildWidgetImage(Fetchable):
    ENDPOINT = rest.get_guild_widget_image

    def __init__(self, rest, guild_id):
        super().__init__(rest)

        self.guild_id = guild_id

    def url(self, *, format=None, style=None):
        if format is not None:
            format = format.lower()
            _validate_format(format)
        else:
            format = 'png'

        if style is not None:
            style = style.lower()

            if style not in ('shield', 'banner1', 'banner2', 'banner3', 'banner4'):
                raise ValueError(f'{style!r} is not a valid guild widget image style')

        return self._form_url(format=format, style=style)
