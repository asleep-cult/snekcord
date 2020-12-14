
class User:
    def __init__(self, data : dict):
        self.data = data

        self.id = data['id']
        self.username = data['username']
        self.discriminator = data['discriminator']
        self.verified = data['verified']
        self.email = data['email']
        self.premium_type = data['premium_type']
        self.flags = data['flags']
        self.bot = data['bot']
        self.mfa_enabled = data['mfa_enabled']
        self.public_flags = data['public_flags']

    def __str__(self):
        return '{0}#{1}'.format(self.username, self.discriminator)

    @property
    def mention(self):
        return '<@{0}>'.format(self.id)

