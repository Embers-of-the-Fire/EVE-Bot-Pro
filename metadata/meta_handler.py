from fastapi import APIRouter
from pydantic import BaseModel
from . import botmeta

metadata_router = APIRouter(
    prefix='/metadata',
    tags=['metadata', 'static'],
)


class MetaData(BaseModel):
    version: str
    raw_version: botmeta.BotVersion


@metadata_router.get("/")
def render_metadata() -> MetaData:
    """Get bot's metadata."""
    return MetaData(version=botmeta.version.render(), raw_version=botmeta.version)
