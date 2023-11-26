from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import aiofiles

import database

from . import skill_render


__all__ = [
    "skill_router",
]


skill_router = APIRouter(
    prefix='/skill',
    tags=['static', 'skill'],
)


@skill_router.get('/prereq/{item_id}/')
def get_skill_prereq(item_id: int) -> List[database.skill_db.SkillObject]:
    res = database.skill_db.SkillDB().get_skill(item_id)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found or has no prerequisity skill")
    return res.unwrap_unchecked()


@skill_router.get('/prereq/{item_id}/recursive/')
def get_skill_prereq_recursive(item_id: int) -> database.skill_db.Skill:
    res = database.skill_db.SkillDB().get_skill_recursive(item_id)
    if res.is_none():
        raise HTTPException(status_code=404, detail="item not found or has no prerequisity skill")
    return res.unwrap_unchecked()


@skill_router.get('/prereq/{item_id}/image/', tags=['image'])
async def get_skill_prereq_image(item_id: int) -> StreamingResponse:
    skill = database.skill_db.SkillDB().get_skill_recursive(item_id)
    fp = skill_render.render_skill_image(
        skill.unwrap_or_else(lambda: database.skill_db.Skill(type_id=item_id, group=[]))
    )
    file = await aiofiles.open(fp, 'rb')
    return StreamingResponse(file, media_type="image/png")
