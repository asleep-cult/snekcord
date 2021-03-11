class InvalidPusherHandler(Exception):
    def __init__(self, pusher, name):
        super().__init__(
            'EventPusher "{.__class__.__name__}" has no handler "{}"'.format(pusher, name)
        )
