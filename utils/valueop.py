from typing import Union

import constant.util_char
import database


__all__ = [
    "format_time",
    "format_value_comma_separated",
    "format_item_pair",
    "cn_indented",
]


def format_time(tm: int) -> str:
    """
    :param tm: unit: s
    :return: "(yy年)?dd天hh小时mm分ss秒"
    """
    tm = max(int(tm), 0)
    day = tm // 86400
    hour = tm % 86400 // 3600
    minute = tm % 3600 // 60
    second = tm % 60
    if day < 365:
        return f"{day:01}天{hour:02}小时{minute:02}分{second:02}秒"
    else:
        year = day // 365
        day = day % 365
        return f"{y:01}年{day:02}天{hour:02}小时{minute:02}分{second:02}秒"


def format_value_comma_separated(value: Union[float, int]) -> str:
    if isinstance(value, float):
        return "{:,.2f}".format(value)
    else:
        return "{:,d}".format(value)


def format_item_pair(type_id: int, value: Union[float, int], newline: bool = True) -> str:
    return (
        database.typename_db.TypeNameDB().get_name(type_id).type_name
        + constant.util_char.multiply_seperator
        + format(value, ",")
        + "\n" if newline else ""
    )


def indent(text: str, text_indent: str) -> str:
    return "\n".join(text_indent + line for line in text.split("\n"))


def cn_indented(text: str, indent_level: int = 0) -> str:
    return indent(text, constant.util_char.chinese_full_space * indent_level)
