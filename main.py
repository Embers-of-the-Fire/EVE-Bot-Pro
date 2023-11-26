# External dependencies import
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# Internal dependencies import

# Router import
from metadata import metadata_router
from market import market_router
from skills import skill_router
from blueprints import blueprint_router
from type_items import type_item_router

# FastAPI application configuration
app = FastAPI()

# FastAPI router configuration
app.include_router(metadata_router)
app.include_router(market_router)
app.include_router(skill_router)
app.include_router(blueprint_router)
app.include_router(type_item_router)


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return "EVE Bot-PRO Service"
