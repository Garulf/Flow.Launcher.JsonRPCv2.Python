from plugin import Plugin


class Launcher:

    def __init__(self, plugin: Plugin):
        self._plugin = plugin

    async def fuzzy_search(self, search: str, title: str):
        return await self._plugin._client.request("FuzzySearch", [search, title])

    async def update_results(self, raw_query, results):
        await self._plugin._client.request("UpdateResults", [raw_query, results])
