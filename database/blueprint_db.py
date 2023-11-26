import sqlite3
from monad_std import Option
from pydantic import BaseModel, PositiveInt, NonNegativeInt, NonNegativeFloat
from typing import Dict, Tuple, Optional, List
from enum import IntFlag, unique
import cbor2

import constant


__all__ = [
    "Blueprint",
    "BlueprintType",
    "BlueprintDB",
]


@unique
class BlueprintType(IntFlag):
    Null = 0
    Manufacture = 1
    Reaction = 2


class Blueprint(BaseModel):
    type_id: PositiveInt
    blp_type: BlueprintType
    material: Dict[PositiveInt, NonNegativeInt]
    product: Optional[Tuple[PositiveInt, NonNegativeInt]]
    time: PositiveInt


class BlpMaterialItem(BaseModel):
    raw_quantity: NonNegativeFloat
    manu_level: NonNegativeInt
    reaction_level: NonNegativeInt


class BlueprintRecursive(BaseModel):
    type_id: PositiveInt
    blp_type: BlueprintType
    material: Dict[PositiveInt, List[BlpMaterialItem]]
    product: Optional[Tuple[PositiveInt, NonNegativeInt]]
    time: PositiveInt


class BlueprintDB:
    __instance: "BlueprintDB" = None
    __db: sqlite3.Connection

    def __new__(cls, *args, **kwargs):
        if BlueprintDB.__instance is None:
            BlueprintDB.__instance = object.__new__(cls, *args, **kwargs)
            BlueprintDB.__instance.__db = sqlite3.connect(constant.filepath.blp_db_path, check_same_thread=False)
        return BlueprintDB.__instance

    def __init__(self):
        pass

    def get_blp_product(self, blp_id: int) -> Option[Tuple[int, int]]:
        """
        :return: int @ 0: product id;
                 int @ 1: product amount
        """
        cursor = self.__db.cursor()
        cursor.execute("select product_id, amount from product where blp_id == ?", (blp_id,))
        return Option.from_nullable(cursor.fetchone()).map(lambda x: (x[0], x[1]))

    def get_blp_by_product(self, product_id: int) -> Option[int]:
        cursor = self.__db.cursor()
        cursor.execute("select blp_id from product where product_id == ?", (product_id,))
        return Option.from_nullable(cursor.fetchone()).map(lambda x: x[0])

    def get_blp(self, blp_id: int) -> Option[Blueprint]:
        cursor = self.__db.cursor()
        cursor.execute("select flag, material, product, `time` from material where type_id == ?", (blp_id,))
        res = cursor.fetchone()
        if res is None:
            return Option.none()
        flag, mat, prod, tm = res
        mat = cbor2.loads(mat)
        prod = tuple(cbor2.loads(prod))
        return Option.some(Blueprint(type_id=blp_id, blp_type=BlueprintType(flag), material=mat, product=prod, time=tm))

    def get_recursive_blp(self, blp_id: int) -> Option[BlueprintRecursive]:
        cursor = self.__db.cursor()
        cursor.execute("select blp_type, material, product, `time` from blp_recursive where blp_id == ?", (blp_id,))
        res = cursor.fetchone()
        if res is None:
            return Option.none()

        bt, mat, prod, tm = res
        mat = {x: [BlpMaterialItem(**z) for z in y] for x, y in cbor2.loads(mat).items()}
        prod = tuple(cbor2.loads(prod))
        return Option.some(BlueprintRecursive(type_id=blp_id, blp_type=bt, material=mat, product=prod, time=tm))
