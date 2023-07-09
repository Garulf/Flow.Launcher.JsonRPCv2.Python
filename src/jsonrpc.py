from __future__ import annotations
import asyncio
import json
import sys
import logging
from dataclasses import dataclass, asdict, field
from asyncio.streams import StreamReader, StreamWriter

import aioconsole

from result import Result
from method import Method


logger = logging.getLogger(__name__)


@dataclass
class JsonRPCError:
    code: int
    message: str
    data: object = None


@dataclass
class JsonRPCQueryResponse:
    result: list[Result] = field(default_factory=list)
    settingsChanges: dict[str, object] = field(default_factory=dict)
    debugMessage: str = ""


@dataclass
class JsonRPCRequest:
    method: str
    id: int
    params: list[object] | None = None
    jsonrpc: str = "2.0"


@dataclass
class JsonRPCResult:
    id: int
    result: object
    jsonrpc: str = "2.0"


@dataclass
class JsonRPCExecuteResponse:
    hide: bool = True


def encode_error(id: int, error: JsonRPCError):
    return (
        json.dumps(
            {
                "jsonrpc": "2.0",
                "error": asdict(error),
                "id": id,
            }
        )
        + "\r\n"
    ).encode("utf-8")


def encode_result(id: int, response: JsonRPCQueryResponse):
    return (
        json.dumps(
            {
                "jsonrpc": "2.0",
                "result": asdict(response),
                "id": id,
            }
        )
        + "\r\n"
    ).encode("utf-8")


class JsonRPCClient:
    def __init__(self) -> None:
        self._methods: dict = {}
        self.tasks: dict[int, asyncio.Task] = {}
        self.requests: dict[int,
                            asyncio.Future[JsonRPCResult | JsonRPCError]] = {}
        self.request_id = 1

    async def __handle_cancellation(self, id: int):
        with open("cancel.log", "+a") as f:
            if id in self.tasks:
                f.write(
                    f"cancel {id}, success: {self.tasks.pop(id).cancel()}\n")
            else:
                f.write(f"try cancel but no {id}\n")

    async def request(
        self, method: str, params: list[object] = []
    ) -> JsonRPCResult | JsonRPCError:
        waiter: asyncio.Future[JsonRPCResult | JsonRPCError] = asyncio.Future()
        self.request_id += 1
        self.requests[self.request_id] = waiter

        message = (
            json.dumps(asdict(JsonRPCRequest(
                method, self.request_id, params))
            )
            + "\r\n"
        )

        self.writer.write(message.encode("utf-8"))

        return await waiter

    async def __handle_result(self, result: JsonRPCResult):
        logger.debug(f"result: {result.id}")

        if result.id in self.requests:
            self.requests.pop(result.id).set_result(result)
            return

        pass

    async def __handle_error(self, id: int, error: JsonRPCError):
        if id in self.requests:
            self.requests.pop(id).set_exception(Exception(error))
        else:
            logger.error(f"cancel with no id found: %d", id)

    async def __handle_notification(self, method: str, params: list[object]):
        if method == "$/cancelRequest":
            await self.__handle_cancellation(params["id"])
            return

        pass

    async def __handle_request(self, request: dict[str, object]):
        with open("debug.log", "+a") as f:
            f.write(f"{request}\n")

        method = request["method"]
        params = request["params"]

        try:
            task = asyncio.create_task(self._methods[method](*params))
            self.tasks[request["id"]] = task

            response = encode_result(request["id"], await task)

            logger.debug("response %s", response.decode("utf-8"))

            self.writer.write(response)
            await self.writer.drain()
            return
        except json.JSONDecodeError:
            err = JsonRPCError(code=-32700, message="JSON decode error")
        except KeyError as e:
            logger.exception(e)
            err = JsonRPCError(
                code=-32601, message="Method not found", data=f"{sys.exc_info()}")
        except TypeError as e:
            logger.exception(e)
            err = JsonRPCError(code=-32602, message="Invalid params")
        except Exception as e:
            logger.exception(e)
            err = JsonRPCError(
                code=-32603, message="Internal error", data=f"{sys.exc_info()}")

        self.writer.write(encode_error(request["id"], err))
        await self.writer.drain()

    async def start_listening(self, methods: dict[str, Method], reader: StreamReader, writer: StreamWriter):
        reader, writer = await aioconsole.get_standard_streams()
        self.reader = reader
        self.writer = writer
        self._methods = methods

        while True:
            bytes = await reader.readline()
            line = bytes.decode("utf-8")

            if line == "":
                continue

            logger.info(line)

            message = json.loads(line)

            if "id" not in message:
                asyncio.create_task(
                    self.__handle_notification(
                        message["method"], message["params"])
                )
            elif "method" in message:
                asyncio.create_task(self.__handle_request(message))
            elif "result" in message:
                asyncio.create_task(
                    self.__handle_result(JsonRPCResult(**message)))
            elif "error" in message:
                asyncio.create_task(
                    self.__handle_error(
                        message["id"], JsonRPCError(**message["error"]))
                )
