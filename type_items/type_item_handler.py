from fastapi import APIRouter, HTTPException
from pydantic import NonNegativeInt
import database.typename_db


__all__ = [
    "type_item_router",
]

type_item_router = APIRouter(
    prefix="/types",
    tags=['static', 'types']
)


@type_item_router.get('/{type_id}/')
def get_item_type(type_id: NonNegativeInt) -> database.typename_db.TypeName:
    res = database.typename_db.TypeNameDB().get_name_safe(type_id)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")
    return res.unwrap_unchecked()


@type_item_router.get('/{type_id}/unchecked/')
def get_item_type_unchecked(type_id: NonNegativeInt) -> database.typename_db.TypeName:
    res = database.typename_db.TypeNameDB().get_name(type_id)
    return res


@type_item_router.get('/search/absolute/')
def search_item(name: str) -> database.typename_db.TypeName:
    res = database.typename_db.TypeNameDB().get_id(name)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")

    return res.unwrap_unchecked()


@type_item_router.get('/search/fuzzy/')
def search_item(name: str) -> database.typename_db.TypeName:
    res = database.typename_db.TypeNameDB().get_id_likely(name)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")

    return res.unwrap_unchecked()


@type_item_router.get('/search/manual/')
def search_item(pattern: str) -> database.typename_db.TypeName:
    res = database.typename_db.TypeNameDB().get_id_with_pattern(pattern)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found")

    return res.unwrap_unchecked()
