from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from io import BytesIO
from pydantic import PositiveInt
from typing_extensions import Annotated

import constant.general
import database
from . import blp_process, blp_render, blp_market


__all__ = [
    "blueprint_router",
]


blueprint_router = APIRouter(
    prefix='/blueprint',
    tags=['dynamic', 'blueprint'],
)


@blueprint_router.get('/{blueprint_id}/plain/raw/')
def get_plain_blp(blueprint_id: PositiveInt) -> database.blueprint_db.Blueprint:
    res = database.blueprint_db.BlueprintDB().get_blp(blueprint_id)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")

    return res.unwrap_unchecked()


@blueprint_router.get('/{blueprint_id}/recursive/raw/')
def get_rec_blp(blueprint_id: PositiveInt) -> database.blueprint_db.BlueprintRecursive:
    res = database.blueprint_db.BlueprintDB().get_recursive_blp(blueprint_id)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")

    return res.unwrap_unchecked()


@blueprint_router.post('/{blueprint_id}/plain/')
def get_blp_formatted(blueprint_id: PositiveInt, factor: blp_process.BlueprintFactor) -> blp_process.BlueprintMaterial:
    res = blp_process.get_blp_material(blueprint_id, factor)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")

    return res.unwrap_unchecked()


@blueprint_router.post('/{blueprint_id}/recursive/')
def get_blp_formatted(blueprint_id: PositiveInt, factor: blp_process.BlueprintFactor) -> blp_process.BlueprintMaterial:
    res = blp_process.get_blp_material_recursive(blueprint_id, factor)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")

    return res.unwrap_unchecked()


@blueprint_router.post('/{blueprint_id}/plain/image/', tags=['image'])
async def get_plain_blp_image(blueprint_id: PositiveInt, factor: blp_process.BlueprintFactor) -> StreamingResponse:
    bio = BytesIO()
    blp_render.BlueprintRenderer.render_plain(blueprint_id, factor, bio)
    return StreamingResponse(iter([bio.getvalue()]), status_code=200, media_type="image/png")


@blueprint_router.post('/{blueprint_id}/recursive/image/', tags=['image'])
async def get_recursive_blp_image(blueprint_id: PositiveInt, factor: blp_process.BlueprintFactor) -> StreamingResponse:
    bio = BytesIO()
    blp_render.BlueprintRenderer.render_recursive(blueprint_id, factor, bio)
    return StreamingResponse(iter([bio.getvalue()]), status_code=200, media_type="image/png")


@blueprint_router.get('/{blueprint_id}/product/')
def get_blp_product(blueprint_id) -> int:
    res = database.blueprint_db.BlueprintDB().get_blp_product(blueprint_id)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")

    return res.unwrap_unchecked()[0]


@blueprint_router.post('/market/', tags=['market'])
async def calc_blp_market_price(
        server: Annotated[constant.general.ServerType, Query(..., alias="s")],
        blueprint_data: blp_process.BlueprintMaterial
) -> blp_market.BlueprintPrice:
    return await blp_market.BlueprintPrice.from_material(blueprint_data, server)


@blueprint_router.post('/market/image/', tags=['image'])
def create_market_image(blueprint_data: blp_market.BlueprintPrice) -> StreamingResponse:
    bio = BytesIO()
    blp_render.BlueprintRenderer.render_price(blueprint_data, bio)
    return StreamingResponse(iter([bio.getvalue()]), status_code=200, media_type="image/png")


@blueprint_router.get('/search/product/')
def search_product(product: PositiveInt) -> int:
    res = database.blueprint_db.BlueprintDB().get_blp_by_product(product)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")

    return res.unwrap_unchecked()

