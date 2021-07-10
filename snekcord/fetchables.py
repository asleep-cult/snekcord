BASE_CDN_URL = 'https://cdn.discordapp.com'

VALID_SIZES = tuple(sqrt ** 2 for sqrt in range(4, 64))


def _get_size(size):
    if size not in VALID_SIZES:
        raise ValueError(
            f'{size!r} is not a valid size (sizes must be a power of 2 between 16 and 4096)'
        )

    return size


def _get_url(url, format, size):
    url += f'.{format}'

    if size is not None:
        url += f'?size={_get_size(size)}'

    return url


class Fetchable:
    def __init__(self, *, rest):
        self.rest = rest

    def __str__(self):
        return self.url()

    def url(self):
        raise NotImplementedError

    def fetch(self, **kwargs):
        return self.rest.request(self.url(**kwargs))


class GuildIcon(Fetchable):
    def __init__(self, *, rest, guild_id, guild_icon):
        super().__init__(rest=rest)
        self.guild_id = guild_id
        self.guild_icon = guild_icon

    def url(self, *, format=None, size=None):
        if size is not None:
            size = _get_size(size)

        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp', 'gif'):
                raise ValueError(f'{format!r} is not a valid guild icon format')
        else:
            if self.hash.startswith('a_'):
                format = 'gif'
            else:
                format = 'png'

        return _get_url(f'{BASE_CDN_URL}/icons/{self.guild_id}/{self.guild_icon}', format, size)


class GuildSplash(Fetchable):
    def __init__(self, *, rest, guild_id, guild_splash):
        super().__init__(rest=rest)
        self.guild_id = guild_id
        self.guild_splash = guild_splash

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp'):
                raise ValueError(f'{format!r} is not a valid guild splash format')
        else:
            format = 'png'

        return _get_url(
            f'{BASE_CDN_URL}/splashes/{self.guild_id}/{self.guild_splash}', format, size
        )


class GuildDiscoverySplash(Fetchable):
    def __init__(self, *, rest, guild_id, guild_discovery_splash):
        super().__init__(rest=rest)
        self.guild_id = guild_id
        self.guild_discovery_splash = guild_discovery_splash

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp'):
                raise ValueError(f'{format!r} is not a valid guild discovery splash format')
        else:
            format = 'png'

        return _get_url(
            f'{BASE_CDN_URL}/discovery-splashes/{self.guild_id}/{self.guild_discovery_splash}',
            format, size
        )


class GuildBanner(Fetchable):
    def __init__(self, *, rest, guild_id, guild_banner):
        super().__init__(rest=rest)
        self.guild_id = guild_id
        self.guild_banner = guild_banner

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp'):
                raise ValueError(f'{format!r} is not a valid guild banner format')
        else:
            format = 'png'

        return _get_url(f'{BASE_CDN_URL}/banners/{self.guild_id}/{self.guild_banner}', format, size)


class DefaultUserAvatar(Fetchable):
    def __init__(self, *, rest, user_discriminator):
        super().__init__(rest=rest)
        self.user_discriminator = user_discriminator

    def url(self):
        return _get_url(f'{BASE_CDN_URL}/embed/avatars/{self.user_discriminator % 5}', 'png', None)


class UserAvatar(Fetchable):
    def __init__(self, *, rest, user_id, user_avatar):
        super().__init__(rest=rest)
        self.user_id = user_id
        self.user_avatar = user_avatar

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp'):
                raise ValueError(f'{format!r} is not a valid user avatar format')
        else:
            format = 'png'

        return _get_url(f'{BASE_CDN_URL}/avatars/{self.user_id}/{self.user_avatar}', format, size)


class ApplicationIcon(Fetchable):
    def __init__(self, *, rest, application_id, application_icon):
        super().__init__(rest=rest)
        self.application_id = application_id
        self.application_icon = application_icon

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp'):
                raise ValueError(f'{format!r} is not a valid application icon format')
        else:
            format = 'png'

        return _get_url(
            f'{BASE_CDN_URL}/app-icons/{self.application_id}/{self.application_icon}', format, size
        )


class ApplicationCover(Fetchable):
    def __init__(self, *, rest, application_id, application_cover_image):
        super().__init__(rest=rest)
        self.application_id = application_id
        self.application_cover_image = application_cover_image

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp'):
                raise ValueError(f'{format!r} is not a valid application cover format')
        else:
            format = 'png'

        return _get_url(
            f'{BASE_CDN_URL}/app-icons/{self.application_id}/{self.application_cover_image}',
            format, size
        )


class ApplicationAsset(Fetchable):
    def __init__(self, *, rest, application_id, application_asset):
        super().__init__(rest=rest)
        self.application_id = application_id
        self.application_asset = application_asset

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp'):
                raise ValueError(f'{format!r} is not a valid application asset format')
        else:
            format = 'png'

        return _get_url(
            f'{BASE_CDN_URL}/app-icons/{self.application_id}/{self.application_asset}',
            format, size
        )


class AchievementIcon(Fetchable):
    def __init__(self, *, rest, application_id, achievement_id, achievement_icon):
        super().__init__(rest=rest)
        self.application_id = application_id
        self.achievement_id = achievement_id
        self.achievement_icon = achievement_icon

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp'):
                raise ValueError(f'{format!r} is not a valid achievement icon format')
        else:
            format = 'png'

        return _get_url(
            f'{BASE_CDN_URL}/app-icons/{self.application_id}/achievements/'
            f'{self.achievement_id}/icons/{self.achievement_icon}',
            format, size
        )


class TeamIcon(Fetchable):
    def __init__(self, *, rest, team_id, team_icon):
        super().__init__(rest=rest)
        self.team_id = team_id
        self.team_icon = team_icon

    def url(self, *, format=None, size=None):
        if format is not None:
            format = format.lower()

            if format not in ('png', 'jpg', 'jpeg', 'webp'):
                raise ValueError(f'{format!r} is not a valid team icon format')
        else:
            format = 'png'

        return _get_url(f'{BASE_CDN_URL}/team-icons/{self.team_id}/{self.team_icon}', format, size)
