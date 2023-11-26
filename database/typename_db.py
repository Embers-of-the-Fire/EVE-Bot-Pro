import sqlite3
from monad_std import Option
from pydantic import BaseModel

import constant

__all__ = [
    "TypeNameDB",
    "TypeName",
]


class TypeName(BaseModel):
    type_id: int
    type_name: str
    published: bool

    @staticmethod
    def fallback_name(type_id: int) -> str:
        return f"无名称物品（{type_id}）"

    @staticmethod
    def unknown_name(type_id: int) -> str:
        return f"未知物品（{type_id}）"


class TypeNameDB:
    __instance: "TypeNameDB" = None
    __db: sqlite3.Connection

    def __new__(cls, *args, **kwargs):
        if TypeNameDB.__instance is None:
            TypeNameDB.__instance = object.__new__(cls, *args, **kwargs)
            TypeNameDB.__instance.__db = sqlite3.connect(constant.filepath.typename_db_path, check_same_thread=False)
        return TypeNameDB.__instance

    def __init__(self):
        pass

    def get_name(self, type_id: int) -> TypeName:
        return self.get_name_safe(type_id).unwrap_or_else(lambda: TypeName(
            type_id=type_id,
            type_name=TypeName.unknown_name(type_id),
            published=False
        ))

    def get_name_safe(self, type_id: int) -> Option[TypeName]:
        cursor = self.__db.cursor()
        cursor.execute("select type_name, published from typename where type_id == ?;", (type_id,))
        val = cursor.fetchone()
        if val is None:
            return Option.none()
        tn, p = val
        return Option.some(TypeName(
            type_id=type_id,
            type_name=tn if tn else TypeName.fallback_name(type_id),
            published=p == 1
        ))

    def get_id(self, type_name: str) -> Option[TypeName]:
        cursor = self.__db.cursor()
        cursor.execute("select type_id, published from typename where type_name == ?;", (type_name,))
        val = cursor.fetchone()
        if val is None:
            return Option.none()
        ti, p = val
        return Option.some(TypeName(
            type_id=ti,
            type_name=type_name,
            published=p == 1
        ))

    def get_id_likely(self, type_name: str) -> Option[TypeName]:
        cursor = self.__db.cursor()
        cursor.execute("select type_name, type_id, published from typename where type_name like ?;",
                       ("%" + type_name + "%",))
        val = cursor.fetchone()
        if val is None:
            return Option.none()
        tn, ti, p = val
        return Option.some(TypeName(
            type_id=ti,
            type_name=tn if tn else TypeName.fallback_name(ti),
            published=p == 1
        ))

    def get_id_with_pattern(self, pattern: str) -> Option[TypeName]:
        cursor = self.__db.cursor()
        cursor.execute("select type_name, type_id, published from typename where type_name like ?;",
                       (pattern.replace("'", "''"),))
        val = cursor.fetchone()
        if val is None:
            return Option.none()
        tn, ti, p = val
        return Option.some(TypeName(
            type_id=ti,
            type_name=tn if tn else TypeName.fallback_name(ti),
            published=p == 1
        ))
