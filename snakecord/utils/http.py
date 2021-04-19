from typing import Tuple


class HttpEndpoint:
    def __init__(self, method: str, path: str, *,
                 params: Tuple[str] = (),
                 json: Tuple[str] = ()) -> None:
        self.method = method
        self.path = path
        self.params = params
        self.json = json

    def request(self, *, session, params=None, json=None):
        if params is not None:
            params = {k: v for k, v in params.items() if k in self.params}

        if json is not None:
            json = {k: v for k, v in json.items() if k in self.json}

        return session.request(self.method, self.path, params=params,
                               json=json)
