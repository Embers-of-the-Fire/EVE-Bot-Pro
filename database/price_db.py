import asyncio
from typing import List, Dict, Iterator, Union, Iterable

import aiohttp
from monad_std.iter import IterMeta
from pydantic import BaseModel, PositiveInt, Field

import constant

__all__ = [
    "PriceDB",
    "MarketPrice",
]

import utils.valueop

serenity_price = "https://www.ceve-market.org/api/market/region/{region}/system/{system}/type/{type_id}.json"
tranquility_price = "https://www.ceve-market.org/tqapi/market/region/{region}/system/{system}/type/{type_id}.json"
jita_serenity_price = "https://www.ceve-market.org/api/market/region/10000002/system/30000142/type/{type_id}.json"
jita_tranquility_price = "https://www.ceve-market.org/tqapi/market/region/10000002/system/30000142/type/{type_id}.json"


class MarketPrice(BaseModel):
    buy: float = Field(default=0.0)
    """Max buy price"""
    sell: float = Field(default=0.0)
    """Min sell price"""
    medium: float = Field(default=0.0)
    """Medium price
    (max + min) / 2"""

    def __add__(self, other: "MarketPrice"):
        assert isinstance(other, MarketPrice)
        return MarketPrice(buy=self.buy + other.buy, sell=self.sell + other.sell, medium=self.medium + other.medium)

    def __sub__(self, other: "MarketPrice"):
        assert isinstance(other, MarketPrice)
        return MarketPrice(buy=self.buy - other.buy, sell=self.sell - other.sell, medium=self.medium - other.medium)

    def __mul__(self, other):
        return MarketPrice(buy=self.buy * other, sell=self.sell * other, medium=self.medium * other)

    def __truediv__(self, other):
        return MarketPrice(buy=self.buy / other, sell=self.sell / other, medium=self.medium / other)

    def __floordiv__(self, other):
        return MarketPrice(buy=self.buy // other, sell=self.sell // other, medium=self.medium // other)

    def __pow__(self, power):
        return MarketPrice(buy=self.buy ** power, sell=self.sell ** power, medium=self.medium ** power)

    def format(self) -> str:
        return "卖单：" + utils.valueop.format_value_comma_separated(self.sell)\
               + "\n买单：" + utils.valueop.format_value_comma_separated(self.buy)\
               + "\n中位：" + utils.valueop.format_value_comma_separated(self.medium)


class PriceDB:
    __instance: "PriceDB" = None

    def __new__(cls, *args, **kwargs):
        if PriceDB.__instance is None:
            PriceDB.__instance = object.__new__(cls, *args, **kwargs)
        return PriceDB.__instance

    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    async def __get_price(self, url) -> MarketPrice:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                val = await response.json()
                bm = val['buy']['max']
                sm = val['sell']['min']
                return MarketPrice(buy=bm, sell=sm, medium=round((sm + bm) / 2, 2))

    # noinspection PyMethodMayBeStatic
    async def get_jita_price(self, type_id: PositiveInt, server: constant.general.ServerType) -> MarketPrice:
        if server == 'tq':
            url = jita_tranquility_price
        else:
            url = jita_serenity_price

        url = url.format(type_id=type_id)
        return await self.__get_price(url)

    # noinspection PyMethodMayBeStatic
    async def get_jita_prices(
            self,
            type_id_list: Union[Iterable[PositiveInt], Iterator[PositiveInt]],
            server: constant.general.ServerType
    ) -> Dict[PositiveInt, MarketPrice]:
        if server == 'tq':
            url = jita_tranquility_price
        else:
            url = jita_serenity_price

        it = IterMeta.iter(type_id_list).array_chunk(5)
        mapping = dict(map(lambda x: (x, 0), type_id_list))

        for chunks in it.to_iter():
            results = await asyncio.gather(*[self.__get_price(url.format(type_id=c)) for c in chunks])
            for i, c in enumerate(chunks):
                mapping[c] = results[i]

        unused = it.get_unused()
        if unused.is_some():
            chunks = unused.unwrap()
            results = await asyncio.gather(*[self.__get_price(url.format(type_id=c)) for c in chunks])
            for i, c in enumerate(chunks):
                mapping[c] = results[i]

        return mapping
