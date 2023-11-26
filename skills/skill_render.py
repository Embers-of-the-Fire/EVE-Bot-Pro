from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
import os.path

import utils.valueop
from database.skill_db import Skill, SkillGroup, SkillDB
from database.typename_db import TypeNameDB, TypeName
import constant
from utils.imageop import TextSize, SingletonImage, text_on_image

skill_title_font = ImageFont.truetype(constant.filepath.font_root_path + "msyhbd.ttc", 45)
skill_content_font = ImageFont.truetype(constant.filepath.font_root_path + "msyh.ttc", 30)

nodata_content_size = TextSize(width=254, height=23)
nodata_content = "NO DATA FOUND"

content_text_height = 15
content_text_spacing = 11


def seriealize_skill_text(data: Skill) -> str:
    def ser(d: SkillGroup, level: int) -> str:
        space: str = constant.util_char.chinese_full_space * level
        t: str = space + TypeNameDB().get_name(d.skill.skill_id).type_name + '\n'
        for s in d.prerequisites:
            t += ser(s, level + 1)
        return t

    text = ""
    for g in data.group:
        text += ser(g, 0)
    return text


def seriealize_level_block(data: Skill) -> List[Tuple[int, int]]:
    def ser(d: SkillGroup) -> List[Tuple[int, int]]:
        s = SkillDB().get_skill_restriction(d.skill.skill_id)
        ls = [(s, d.skill.skill_level - s) if s < d.skill.skill_level else (d.skill.skill_level, 0)]
        for p in d.prerequisites:
            ls += ser(p)
        return ls

    res = []
    for g in data.group:
        res += ser(g)
    return res


def seriealize_training_point(data: Skill) -> Tuple[str, int]:
    """
    :return: int: 总量 str: 文字
    """
    dc = {}

    def cnt(d: SkillGroup):
        nonlocal dc
        if d.skill.skill_id not in dc.keys() or dc[d.skill.skill_id] < d.skill.skill_level:
            dc[d.skill.skill_id] = d.skill.skill_level
        for p in d.prerequisites:
            cnt(p)

    for g in data.group:
        cnt(g)

    def ser(d: SkillGroup) -> str:
        nonlocal dc
        v = SkillDB().get_skill_time_factor(d.skill.skill_id)
        if v.is_none():
            t: str = "[-]"
        elif d.skill.skill_id not in dc.keys() or dc[d.skill.skill_id] > d.skill.skill_level:
            t: str = "[{:,d}]".format(constant.skills.skill_time_factor[d.skill.skill_level] * v.unwrap())
        elif d.skill.skill_id in dc.keys() and dc[d.skill.skill_id] == d.skill.skill_level:
            calced = constant.skills.skill_time_factor[d.skill.skill_level] * v.unwrap()
            t: str = "{:,d}".format(calced)
            dc.pop(d.skill.skill_id)
        else:
            t: str = "[-]"

        t += '\n'
        for p in d.prerequisites:
            t += ser(p)
        return t

    text = ""
    for g in data.group:
        text += ser(g)

    return text, data.total_points


def render_skill_image(data: Skill, overwrite: bool = False) -> str:
    """Return: file path"""
    path = constant.filepath.image_root_path + rf"skills\{data.type_id}.png"
    if not overwrite and os.path.exists(path) and os.path.isfile(path):
        return path

    skill_length = len(data)
    if skill_length == 0:
        title = TypeNameDB().get_name(data.type_id).type_name
        size = SingletonImage().get_size(text=title, font=skill_title_font)
        # noinspection DuplicatedCode
        base_image = Image.new("RGB", (100 + max(size.width, nodata_content_size.width), 250), "white")
        image = ImageDraw.Draw(base_image, "RGB")
        text_on_image(image, xy=(50, 50), text=title, font=skill_title_font)
        text_on_image(image, xy=(50, 130), text=nodata_content, font=skill_content_font)
        base_image.save(path, "png", bitmap_format="png")
        return path

    skt = seriealize_skill_text(data)
    block = seriealize_level_block(data)
    training_point_text, training_time = seriealize_training_point(data)
    training_sum_text = "总技能点：" + utils.valueop.format_value_comma_separated(training_time)\
                        + "\n预估用时：" + utils.valueop.format_time(training_time)
    title = TypeNameDB().get_name(data.type_id).type_name

    title_size = SingletonImage().get_size(text=title, font=skill_title_font)
    skt_size = SingletonImage().get_size(text=skt, font=skill_content_font, spacing=11)
    training_point_size = SingletonImage().get_size(text=training_point_text, font=skill_content_font, spacing=11)
    training_sum_text_size = SingletonImage().get_size(text=training_sum_text, font=skill_content_font, spacing=11)

    base_image = Image.new(
        "RGB",
        # 211: 25 + 25 + 29 * 5 + 4 * 4
        (100 + max(title_size.width, skt_size.width + training_point_size.width + 211, training_sum_text_size.width),
         # 181: 50 + 29 * 5 + 4 * 4
         180 + skt_size.height + 25 + training_sum_text_size.height),
        "white"
    )
    image = ImageDraw.Draw(base_image)

    # Padding: 25
    text_on_image(image, xy=(50, 50), text=title, font=skill_title_font, spacing=11)
    text_on_image(image, xy=(50, 130), text=skt, font=skill_content_font, spacing=11)
    text_on_image(image, xy=(280 + skt_size.width, 130), text=training_point_text, font=skill_content_font, spacing=11)
    text_on_image(image, xy=(50, 155 + skt_size.height), text=training_sum_text, font=skill_content_font, spacing=11)
    # Character Height: 29
    # Row Spacing: 14
    # Column Spacing(Per Rectangle): 6
    # Rectangle Top Offset: 8
    for row_index, row in enumerate(block):
        # 46: 75 - 29
        x = 46 + skt_size.width
        for alpha in range(row[0]):
            # 35: 29 + 6
            x += 35
            # 43: 29 + 14
            # 167: 138 + 29
            image.rectangle(xy=(x, 138 + row_index * 43, x + 29, 167 + row_index * 43), fill="lightblue", outline=None)

        for omega in range(row[1]):
            x += 35
            image.rectangle(xy=(x, 138 + row_index * 43, x + 29, 167 + row_index * 43), fill="orange", outline=None)

    base_image.save(path, "png", bitmap_format="png")
    return path
