from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class JsonRPCAction:
    id: int
    method: str
    parameters: list = field(default_factory=list)


@dataclass
class Result:
    title: str
    subtitle: str = ""
    icoPath: str = ""
    titleHighlightData: tuple[int] | tuple = field(default_factory=tuple)
    titleTooltip: str = ""
    subtitleTooltip: str = ""
    copyText: str = ""
    jsonRPCAction: JsonRPCAction | None = None
    score: int | None = None
