from monad_std import Option
from monad_std.iter import IterMeta
from pydantic import BaseModel, PositiveInt, NonNegativeInt
from typing import Dict, Tuple, Optional

import constant.general
import database.price_db
from . import blp_process

__all__ = [
    "BlueprintPrice",
    "BlueprintProfit",
]


class BlueprintProfit(BaseModel):
    per_hour: database.price_db.MarketPrice
    sum: database.price_db.MarketPrice


class BlueprintPrice(BaseModel):
    blp_id: PositiveInt
    material: Dict[PositiveInt, Tuple[NonNegativeInt, database.price_db.MarketPrice]]
    material_sum: database.price_db.MarketPrice
    product: Optional[Tuple[PositiveInt, NonNegativeInt, database.price_db.MarketPrice]]
    """id, amount, price"""
    profit: BlueprintProfit
    time: PositiveInt

    @staticmethod
    async def from_material(material: blp_process.BlueprintMaterial,
                            server: constant.general.ServerType) -> "BlueprintPrice":
        mkt_ids = set(material.material.keys())
        if material.product_id is not None:
            mkt_ids.add(material.product_id)

        mkt_data = await database.price_db.PriceDB().get_jita_prices(mkt_ids, server)
        materiadata = dict(IterMeta.iter(material.material.items())
                           .map(lambda x: (x[0],
                                           (x[1],
                                            Option.from_nullable(mkt_data.get(x[0]))
                                            .map(lambda v: v * x[1])
                                            .unwrap_or(database.price_db.MarketPrice()))))
                           .to_iter())
        sum_val = sum(map(lambda x: x[1], materiadata.values()), start=database.price_db.MarketPrice())
        prod_time = material.time
        prod_val = (Option.from_nullable(material.product_id)
                    .and_then(lambda x: Option.from_nullable(mkt_data.get(x)))
                    .zip(Option.from_nullable(material.product_amount))
                    .map(lambda x: x[0] * x[1]))
        profit = prod_val.unwrap_or(database.price_db.MarketPrice()) - sum_val
        return BlueprintPrice(
            blp_id=material.blp_id,
            material=materiadata,
            material_sum=sum_val,
            product=((material.product_id, material.product_amount or 0.0, prod_val.unwrap())
                     if material.product_id is not None and prod_val.is_some()
                     else None),
            profit=BlueprintProfit(sum=profit, per_hour=profit / prod_time * 3600),
            time=prod_time
        )
