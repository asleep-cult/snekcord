class BadWsHttpResponse(Exception):
    def __init__(self, tp, expected, got):
        super().__init__(
            "Expected {} {}, got {}".format(tp, expected, got)
        )
