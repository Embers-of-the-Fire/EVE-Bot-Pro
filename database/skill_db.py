import sqlite3
from monad_std import Option
from pydantic import BaseModel, NonNegativeInt, PositiveInt
from typing import List, Set
import cbor2
import constant

__all__ = [
    "Skill",
    "SkillObject",
    "SkillGroup",
    "SkillDB"
]


class SkillObject(BaseModel):
    skill_id: PositiveInt
    skill_level: NonNegativeInt

    def __len__(self):
        return 1


class SkillGroup(BaseModel):
    skill: SkillObject
    prerequisites: List["SkillGroup"]

    def __len__(self):
        return 1 + sum(map(lambda x: len(x), self.prerequisites), 0)


class Skill(BaseModel):
    type_id: NonNegativeInt
    total_points: NonNegativeInt
    group: List[SkillGroup]

    def __len__(self):
        return sum(map(lambda x: len(x), self.group), 0)


class SkillDB:
    __instance: "SkillDB" = None
    __db: sqlite3.Connection

    def __new__(cls, *args, **kwargs):
        if SkillDB.__instance is None:
            SkillDB.__instance = object.__new__(cls, *args, **kwargs)
            SkillDB.__instance.__db = sqlite3.connect(constant.filepath.skill_db_path, check_same_thread=False)
        return SkillDB.__instance

    def __init__(self):
        pass

    def get_skill(self, type_id: int) -> Option[List[SkillObject]]:
        cursor = self.__db.cursor()
        cursor.execute("select skill_id, skill_level from skills where type_id == ?", (type_id,))
        res = cursor.fetchall()
        if not res:
            return Option.none()
        else:
            return Option.some(list(map(lambda x: SkillObject(skill_id=x[0], skill_level=x[1]), res)))

    def __recursive_build(self, data: dict) -> SkillGroup:
        skill_id = data['id']
        level = data['level']
        prereq = list(map(lambda x: self.__recursive_build(x), data['prereq']))
        return SkillGroup(
            skill=SkillObject(skill_id=skill_id, skill_level=level),
            prerequisites=prereq
        )

    def get_skill_recursive(self, type_id: int) -> Option[Skill]:
        cursor = self.__db.cursor()
        cursor.execute("select total, prereq from recursive where type_id == ?", (type_id,))
        data = cursor.fetchone()
        if data is None:
            return Option.none()
        else:
            total, skills = data
            skills = cbor2.loads(skills)
            return Option.some(Skill(
                type_id=type_id,
                total_points=total,
                group=list(map(lambda x: self.__recursive_build(x), skills))
            ))

    def get_skill_restriction(self, skill_id: int) -> int:
        cursor = self.__db.cursor()
        cursor.execute("select alpha_level from skill_constant where skill_id == ?;", (skill_id,))
        res = cursor.fetchone()
        if not res:
            return 0
        else:
            return res[0]

    def get_skill_time_factor(self, skill_id: int) -> Option[int]:
        cursor = self.__db.cursor()
        cursor.execute("select time_factor from skill_constant where skill_id == ?;", (skill_id,))
        res = cursor.fetchone()
        return Option.from_nullable(res).map(lambda x: x[0])
