from __future__ import annotations
import aioconsole

from dataclasses import dataclass, field
import dataclasses
import json
import os
import sys
import io
import traceback
from typing import Union
from pathlib import Path
import logging

from result import Result, JsonRPCAction


plugindir = Path.absolute(Path(__file__).parent)
paths = (".", "lib", "plugin")
sys.path = [str(plugindir / p) for p in paths] + sys.path


LOG_FILENAME = "debug.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", "%H:%M:%S")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger



def write_line_to(file, msg):
    with open(file, "+a") as f:
        f.write(msg + "\n")


def clear_file(file):
    with open(file, "w"):
        pass







class Plugin(JsonRPCClient):
    async def initialize(self, arg: dict[str, object]):
        resultlogger.info(f"initialize: {json.dumps(arg)}")
        return JsonRPCExecuteResponse(hide=False)

    async def store(self, res):
        resultlogger.info(f"store: {json.dumps(res)}")
        return JsonRPCExecuteResponse(hide=False)

    async def query(self, arg: dict[str, object]):
        with open("test.log", "a+") as f:
            f.write(json.dumps(arg))

        result1 = await self.request("FuzzySearch", [arg["Search"], "hello"])
        result2 = await self.request("FuzzySearch", [arg["Search"], "world"])

        debuglogger.debug(result1)

        res = JsonRPCQueryResponse(
            [
                Result(
                    f"SomeFile1.mp3",
                    subtitle="Download at 30%",
                    jsonRPCAction=JsonRPCAction(
                        id=0, method="store", parameters=["SomeFile.mp3"]
                    )
                ),
                Result(
                    f"SomeFile2.mp3",
                    subtitle="Download at 10%",
                    jsonRPCAction=JsonRPCAction(
                        id=0, method="store", parameters=["SomeFile.mp3"]
                    )
                ),
            ]
        )
        for result in res.result:
            match = await self.request("FuzzySearch", [arg["Search"], result.title])
            result.score = match.result['Score']
            result.titleHighlightData = match.result.get("MatchData", list())
        while True:
            for result in res.result:
                perc = result.subtitle.split(" ")[2][:-1]
                i = int(perc) + 1
                result.subtitle = f"Download at {i}%"
            await self.request("UpdateResults", [arg["RawQuery"], res])

            await asyncio.sleep(0.5)

        return res


async def main():
    # loop = asyncio.get_event_loop()
    # reader = asyncio.StreamReader()
    # protocol = asyncio.StreamReaderProtocol(reader)
    # await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    # w_transport, w_protocol = await loop.connect_write_pipe(FlowControlMixin, sys.stdout)
    # writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)

    

    client = Plugin()
    await client.start_listening(reader, writer)


if __name__ == "__main__":
    clear_file("cancel.log")
    clear_file("debug.log")
    clear_file("query.log")
    clear_file("test.log")
    clear_file("err.log")

    querylogger = setup_logger('querylogger', 'query.log', level=logging.DEBUG)
    cancellogger = setup_logger(
        'cancellogger', 'cancel.log', level=logging.DEBUG)
    debuglogger = setup_logger('debuglogger', 'debug.log', level=logging.DEBUG)
    errlogger = setup_logger('errlogger', 'err.log', level=logging.ERROR)
    resultlogger = setup_logger(
        'resultlogger', 'result.log', level=logging.DEBUG)

    asyncio.run(main())
