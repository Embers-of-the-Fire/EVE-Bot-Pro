from monad_std import Option
from monad_std.iter import IterMeta
from pydantic import BaseModel, NonNegativeInt, NonNegativeFloat, PositiveInt
from typing import Dict, Optional

import database

__all__ = [
    "BlueprintFactor",
    "BlueprintMaterial",
    "get_blp_material",
    "get_blp_material_recursive",
]

from database.blueprint_db import BlueprintType


class BlueprintFactor(BaseModel):
    # factor = level * 0.01
    manu_material: NonNegativeInt = 0
    # factor = level * 0.02
    manu_time: NonNegativeInt = 0
    # factor = value / 100
    extra_material: NonNegativeFloat = 0.0
    # factor = value / 100
    extra_time: NonNegativeFloat = 0.0

    @property
    def material_factor(self) -> NonNegativeFloat:
        return (1 - 0.01 * self.manu_material) * (1 - self.extra_material / 100)

    @property
    def reaction_material_factor(self) -> NonNegativeFloat:
        return 1 - self.extra_material / 100

    @property
    def time_factor(self) -> NonNegativeFloat:
        return (1 - 0.02 * self.manu_time) * (1 - self.extra_time / 100)

    @property
    def reaction_time_factor(self) -> NonNegativeFloat:
        return 1 - self.extra_time / 100


class BlueprintMaterial(BaseModel):
    blp_id: PositiveInt
    product_id: Optional[NonNegativeInt]
    product_amount: Optional[NonNegativeInt]
    material: Dict[PositiveInt, NonNegativeInt]
    time: PositiveInt


def get_blp_material(blp_id: int, factor: BlueprintFactor = BlueprintFactor()) -> Option[BlueprintMaterial]:
    blp = database.blueprint_db.BlueprintDB().get_blp(blp_id)
    if blp.is_none():
        return Option.none()

    prod = database.blueprint_db.BlueprintDB().get_blp_product(blp_id)

    blp = blp.unwrap_unchecked()
    if blp.blp_type == database.blueprint_db.BlueprintType.Null:
        return Option.some(BlueprintMaterial(
            blp_id=blp_id,
            product_id=prod.to_nullable()[0],
            product_amount=prod.to_nullable()[1],
            material={},
            time=blp.time
        ))
    elif blp.blp_type == database.blueprint_db.BlueprintType.Manufacture:
        return Option.some(BlueprintMaterial(
            blp_id=blp_id,
            product_id=prod.to_nullable()[0],
            product_amount=prod.to_nullable()[1],
            material=dict(IterMeta.iter(blp.material.items())
                          .map(lambda x: (x[0], round(x[1] * factor.material_factor)))),
            time=blp.time * factor.time_factor
        ))
    else:
        return Option.some(BlueprintMaterial(
            blp_id=blp_id,
            product_id=prod.to_nullable()[0],
            product_amount=prod.to_nullable()[1],
            material=dict(IterMeta.iter(blp.material.items())
                          .map(lambda x: (x[0], round(x[1] * factor.reaction_material_factor)))),
            time=blp.time * factor.reaction_time_factor
        ))


def get_blp_material_recursive(blp_id: int, factor: BlueprintFactor = BlueprintFactor()) -> Option[BlueprintMaterial]:
    blp = database.blueprint_db.BlueprintDB().get_recursive_blp(blp_id)
    if blp.is_none():
        return Option.none()

    blp = blp.unwrap_unchecked()

    if blp.product is None:
        prod_id = prod_amo = None
    else:
        prod_id, prod_amo = blp.product

    blp_mat = dict(
        IterMeta.iter(blp.material.items())
            .map(lambda type_material_pat: (
            type_material_pat[0],
            int(IterMeta.iter(type_material_pat[1])
                .map(lambda val:
                     val.raw_quantity
                     * (factor.material_factor ** val.manu_level)
                     * (factor.reaction_material_factor ** val.reaction_level)
                     )
                .sum().unwrap_or(0.0))
        ))
    )

    if blp.blp_type == BlueprintType.Manufacture:
        blp_time = blp.time * factor.time_factor
    elif blp.blp_type == BlueprintType.Reaction:
        blp_time = blp.time * factor.reaction_time_factor
    else:
        blp_time = blp.time

    return Option.some(BlueprintMaterial(
        blp_id=blp_id,
        product_id=prod_id,
        product_amount=prod_amo,
        material=blp_mat,
        time=int(blp_time)
    ))
