from devtools import debug
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont

import database
import utils
from utils.imageop import text_on_image, TextSize, SingletonImage
from . import blp_process
import constant.filepath
from .blp_market import BlueprintPrice
from .blp_process import get_blp_material, BlueprintFactor, get_blp_material_recursive

__all__ = [
    "BlueprintRenderer",
]

blp_title_font = ImageFont.truetype(constant.filepath.font_root_path + "msyhbd.ttc", 45)
blp_subtitle_font = ImageFont.truetype(constant.filepath.font_root_path + "msyhbd.ttc", 35)
blp_content_font = ImageFont.truetype(constant.filepath.font_root_path + "msyh.ttc", 30)

nodata_content_size = TextSize(width=254, height=23)
nodata_content = "NO DATA FOUND"

# size: 170, 35
material_title: str = "材料信息"
product_title: str = "产物信息"
material_sum_title: str = "材料总价"
profit_sum_title: str = "利润"


class BlueprintRenderer:
    @staticmethod
    def render_price(data: BlueprintPrice, to_write):
        title = database.typename_db.TypeNameDB().get_name(data.blp_id).type_name
        title_size = SingletonImage().get_size(text=title, font=blp_title_font, spacing=11)

        # material text
        if not data.material:
            material_text_col1 = "NO MATERIAL DATA"
            material_text_col2 = ""
        else:
            material_text_col1 = ""
            material_text_col2 = ""
            _flag = True
            for _mat_id, (_quantity, _price) in data.material.items():
                _title = database.typename_db.TypeNameDB().get_name(_mat_id).type_name \
                         + constant.util_char.multiply_seperator \
                         + utils.valueop.format_value_comma_separated(_quantity)
                _price_text = _price.format()
                if _flag:
                    _flag = False
                    material_text_col1 += _title + "\n"
                    material_text_col1 += utils.valueop.indent(
                        _price_text,
                        constant.util_char.price_indent
                    ) + "\n"
                else:
                    _flag = True
                    material_text_col2 += _title + "\n"
                    material_text_col2 += utils.valueop.indent(
                        _price_text,
                        constant.util_char.price_indent
                    ) + "\n"
        material_col1_size = SingletonImage().get_size(text=material_text_col1, font=blp_content_font, spacing=8)
        material_col2_size = SingletonImage().get_size(text=material_text_col2, font=blp_content_font, spacing=8)

        # product text
        if data.product is None:
            prod_text = "NO PRODUCT DATA"
        else:
            _product_id, _product_amount, _product_price = data.product
            prod_text = database.typename_db.TypeNameDB().get_name(_product_id).type_name \
                        + constant.util_char.multiply_seperator \
                        + utils.valueop.format_value_comma_separated(_product_amount) + "\n" \
                        + utils.valueop.indent(_product_price.format(), constant.util_char.price_indent) + "\n"
        product_text_size = SingletonImage().get_size(text=prod_text, font=blp_content_font, spacing=8)

        # sum text
        material_sum_text = utils.valueop.indent(data.material_sum.format(), constant.util_char.price_indent)
        profit_sum_text_col1 = "总利润\n" \
                               + utils.valueop.indent(data.profit.sum.format(), constant.util_char.price_indent)
        profit_sum_text_col2 = "每小时\n" \
                               + utils.valueop.indent(data.profit.per_hour.format(), constant.util_char.price_indent)
        material_sum_text_size = SingletonImage().get_size(text=material_sum_text, font=blp_content_font, spacing=8)
        profit_sum_col1_size = SingletonImage().get_size(text=profit_sum_text_col1, font=blp_content_font, spacing=8)
        profit_sum_col2_size = SingletonImage().get_size(text=profit_sum_text_col2, font=blp_content_font, spacing=8)
        # time text
        time_text = "制造用时：" + utils.valueop.format_time(data.time)
        time_text_size = SingletonImage().get_size(text=time_text, font=blp_content_font)
        base_image = Image.new(
            "RGB",
            (
                # padding(left, right): 50 * 2; inner padding: 25 * 2;
                100 + max(
                    title_size.width,
                    50 + max(140, material_col1_size.width + material_col2_size.width, material_sum_text_size.width)
                    + max(140, product_text_size.width, profit_sum_col1_size.width + profit_sum_col2_size.width),
                    time_text_size.width
                ),
                # padding(top, bottom): 50 * 2; title(with padding): 80;
                # sumed price subtitle(with padding): 50; sumed price(with padding): 150;
                # time text(with padding): 50; material/product subtitle(with padding): 50;
                480 + max(
                    material_col1_size.height,
                    material_col2_size.height,
                    product_text_size.height
                ),
            ),
            "white"
        )
        image = ImageDraw.Draw(base_image, "RGB")
        text_on_image(image, xy=(50, 50), text=title, font=blp_title_font, spacing=11)
        text_on_image(image, xy=(50, 130), text=material_sum_title, font=blp_subtitle_font, spacing=11)
        text_on_image(
            image,
            xy=(100 + max(140, material_col1_size.width + material_col2_size.width,
                          material_sum_text_size.width), 130),
            text=profit_sum_title,
            font=blp_subtitle_font,
            spacing=11
        )
        text_on_image(image, xy=(50, 180), text=material_sum_text, font=blp_content_font, spacing=8)
        text_on_image(
            image,
            xy=(100 + max(140, material_col1_size.width + material_col2_size.width,
                          material_sum_text_size.width), 180),
            text=profit_sum_text_col1,
            font=blp_content_font,
            spacing=8
        )
        text_on_image(
            image,
            xy=(100 + max(140, material_col1_size.width + material_col2_size.width,
                          material_sum_text_size.width) + profit_sum_col1_size.width, 180),
            text=profit_sum_text_col2,
            font=blp_content_font,
            spacing=8
        )
        text_on_image(image, xy=(50, 330), text=time_text, font=blp_content_font)
        text_on_image(image, xy=(50, 380), text=material_title, font=blp_subtitle_font)
        text_on_image(
            image,
            xy=(100 + max(140, material_col1_size.width + material_col2_size.width,
                          material_sum_text_size.width), 380),
            text=product_title,
            font=blp_subtitle_font
        )
        text_on_image(image, xy=(50, 430), text=material_text_col1, font=blp_content_font, spacing=8)
        text_on_image(
            image,
            xy=(75 + material_col1_size.width, 420),
            text=material_text_col2,
            font=blp_content_font,
            spacing=8
        )
        text_on_image(
            image,
            xy=(100 + max(140, material_col1_size.width + material_col2_size.width,
                          material_sum_text_size.width), 430),
            text=prod_text,
            font=blp_content_font,
            spacing = 8
        )
        base_image.save(to_write, "png", bitmap_format="png")

    @staticmethod
    def render_plain(blp_id: int, factor: BlueprintFactor, to_write):
        # fp = constant.filepath.image_cache_path + str(uuid.uuid4()) + ".png"
        get_blp_material(blp_id, factor) \
            .map(lambda x: BlueprintRenderer.__render(x, to_write)) \
            .unwrap_or_else(lambda: BlueprintRenderer.__render_null(blp_id, to_write))

    @staticmethod
    def render_recursive(blp_id: int, factor: BlueprintFactor, to_write):
        # fp = constant.filepath.image_cache_path + str(uuid.uuid4()) + ".png"
        get_blp_material_recursive(blp_id, factor) \
            .map(lambda x: BlueprintRenderer.__render(x, to_write)) \
            .unwrap_or_else(lambda: BlueprintRenderer.__render_null(blp_id, to_write))

    @staticmethod
    def __render_null(blp_id: int, to_write):
        blp_name = database.typename_db.TypeNameDB().get_name(blp_id).type_name
        # noinspection DuplicatedCode
        size = SingletonImage().get_size(text=blp_name, font=blp_title_font)
        base_image = Image.new("RGB", (100 + max(size.width, nodata_content_size.width), 250), "white")
        image = ImageDraw.Draw(base_image, "RGB")
        text_on_image(image, xy=(50, 50), text=blp_name, font=blp_title_font)
        text_on_image(image, xy=(50, 130), text=nodata_content, font=blp_content_font)
        base_image.save(to_write, "png", bitmap_format="png")

    # noinspection DuplicatedCode
    @staticmethod
    def __render(blp: blp_process.BlueprintMaterial, to_write):
        blp_name = database.typename_db.TypeNameDB().get_name(blp.blp_id).type_name
        product_expr = ("产物：" + utils.valueop.format_item_pair(blp.product_id, blp.product_amount or 0)
                        if blp.product_id is not None else "无产物信息")
        time_expr = "用时：" + utils.valueop.format_time(blp.time)
        if not blp.material:
            material_expr = "无材料信息"
            mat_amo_expr = ""
        else:
            material_expr = ""
            mat_amo_expr = ""
            for k, v in sorted(blp.material.items(), key=lambda x: x[1], reverse=True):
                material_expr += database.typename_db.TypeNameDB().get_name(k).type_name + "\n"
                mat_amo_expr += utils.valueop.format_value_comma_separated(v) + "\n"

        mat_size = utils.imageop.SingletonImage().get_size(material_expr, blp_content_font, spacing=11)
        mat_amo_size = utils.imageop.SingletonImage().get_size(mat_amo_expr, blp_content_font, spacing=11)
        prod_size = utils.imageop.SingletonImage().get_size(product_expr, blp_content_font)
        time_size = utils.imageop.SingletonImage().get_size(time_expr, blp_content_font)
        title_size = utils.imageop.SingletonImage().get_size(blp_name, blp_title_font)

        base_image = Image.new(
            "RGB",
            (
                100 + max(
                    title_size.width,
                    time_size.width,
                    prod_size.width,
                    mat_size.width + 50 + mat_amo_size.width
                ),
                260 + max(mat_size.height, mat_amo_size.height)
            ),
            "white"
        )
        image = ImageDraw.Draw(base_image, "RGB")
        text_on_image(image, xy=(50, 50), text=blp_name, font=blp_title_font)
        text_on_image(image, xy=(50, 120), text=product_expr, font=blp_content_font)
        text_on_image(image, xy=(50, 160), text=time_expr, font=blp_content_font)
        text_on_image(image, xy=(50, 210), text=material_expr, font=blp_content_font, spacing=11)
        text_on_image(image, xy=(100 + mat_size.width, 210), text=mat_amo_expr, font=blp_content_font, spacing=11)
        base_image.save(to_write, "png", bitmap_format="png")
