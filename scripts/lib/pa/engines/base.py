from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class FieldRule:
    name: str
    selector: str
    attr: str = "text"       # "text" | "html" | any HTML attribute name
    summarize: bool = False  # True: agent 对此字段内容做摘要提炼，而非直接输出原文

class Engine(ABC):
    @abstractmethod
    async def open(self, url: str) -> None: ...

    @abstractmethod
    async def get_dom(self) -> str: ...

    @abstractmethod
    async def scroll_to_bottom(self) -> None: ...

    @abstractmethod
    async def extract(self, rules: list[FieldRule]) -> list[dict]: ...

    @abstractmethod
    async def close(self) -> None: ...
