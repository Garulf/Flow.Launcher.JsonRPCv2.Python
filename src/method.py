from __future__ import annotations
from abc import ABC, abstractmethod

from plugin import Plugin
from result import Result


class Method(ABC):

    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self._results: list[Result] = []

    async def __call__(self, arg: dict[str, object]):
        await self.call(arg)

    def add_result(self, result: Result):
        self._results.append(result)

    def add_results(self, results: list[Result]):
        self._results.extend(results)

    def clear_results(self):
        self._results.clear()

    @abstractmethod
    async def call(self, arg: dict[str, object]):
        pass
