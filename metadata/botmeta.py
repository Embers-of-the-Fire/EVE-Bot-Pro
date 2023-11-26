from typing import List
from pydantic import BaseModel


class BotVersion(BaseModel):
    major: int
    minor: int
    patch: int
    appendix: List[str]

    def render(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}" + "".join(map(lambda x: "-" + x, self.appendix))


version = BotVersion(
    major=0,
    minor=1,
    patch=0,
    appendix=[],
)
