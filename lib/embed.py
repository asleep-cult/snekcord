   
class Embed:
    def __init__(self, color, *, title, description, url, timestamp):
        self.color = color
        self.title = title
        self.description = description
        self.url = url
        self.timestamp = timestamp

        self._footer = {}
        self._image = {}
        self._author = {}
        self._thumbnail = {}
        self._fields = []

    def footer(self, *, text, icon_url):
        self._footer = {
            'text': str(text),
            'icon_url': str(icon_url)
        }

    def image(self, *, url):
        self._image = {
            'url': str(url)
        }

    def thumbnail(self, *, url):
        self._thumbnail = {
            'url': str(url)
        }

    def author(self, *, name, icon_url):
        self._author = {
            'name': str(name),
            'icon_url': str(icon_url)
        }

    def add_field(self, *, name, value, inline=False):
        data = {
            'inline': inline,
            'name': str(name),
            'value': str(value)
        }
        self._fields.append(data)
