from __future__ import annotations
from dataclasses import dataclass, field
from multiprocessing import context


FONT_FAMILY = "/Resources/#Segoe Fluent Icons"

@dataclass
class JsonRPCAction:
    id: int
    method: str
    parameters: list = field(default_factory=list)

@dataclass
class Glyph:
    glyph: str
    fontFamily: str = FONT_FAMILY


@dataclass
class Result:
    title: str
    subtitle: str = ""
    icoPath: str = ""
    titleHighlightData: tuple[int] | tuple = field(default_factory=tuple)
    titleTooltip: str = ""
    subtitleTooltip: str = ""
    copyText: str = ""
    contextData: list | None = None
    jsonRPCAction: JsonRPCAction | None = None
    glyph: Glyph | None = None
    score: int | None = None
