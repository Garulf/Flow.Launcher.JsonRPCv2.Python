from __future__ import annotations
from typing import Callable, Dict, List
from functools import wraps

import aioconsole


from jsonrpc import JsonRPCClient
from result import Result


Method = Callable[[Dict[str, object]], List[Result]]


class Plugin:

    def __init__(self, methods: list[Method] | None = None) -> None:
        self._client = JsonRPCClient()
        self._methods: dict[str, Method] = {}
        if methods:
            self.add_methods(methods)

    def add_method(self, method: Method):
        self._methods[method.__class__.__name__] = method

    def add_methods(self, methods: list[Method]):
        for method in methods:
            self.add_method(method)

    def on(self) -> Callable:
        @wraps(self.on)
        def wrapper(method: Method):
            self.add_method(method)
            return method
        return wrapper

    async def run(self):
        reader, writer = await aioconsole.get_standard_streams()
        await self._client.start_listening(self._methods, reader, writer)
