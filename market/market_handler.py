from typing import List, Dict

from fastapi import APIRouter, HTTPException
from pydantic import PositiveInt

import constant
import database.price_db

market_router = APIRouter(
    prefix='/market',
    tags=['market', 'dynamic'],
)


@market_router.get('/jita/type/{server}/{type_id}/')
async def get_jita_price(server: constant.general.ServerType, type_id: PositiveInt) -> database.price_db.MarketPrice:
    if server != 'tq' and server != 'se':
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unknown server",
                "input": server, "expect": [constant.general.serenity, constant.general.tranquility]
            }
        )
    return await database.price_db.PriceDB().get_jita_price(type_id, server)


@market_router.post('/jita/types/{server}/')
async def get_jita_prices(
        server: constant.general.ServerType,
        type_id: List[PositiveInt]
) -> Dict[PositiveInt, database.price_db.MarketPrice]:
    if server != 'tq' and server != 'se':
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unknown server",
                "input": server, "expect": [constant.general.serenity, constant.general.tranquility]
            }
        )
    return await database.price_db.PriceDB().get_jita_prices(type_id, server)
