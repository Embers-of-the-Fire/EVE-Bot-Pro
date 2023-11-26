from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel


__all__ = [
    "TextSize",
    "SingletonImage",
    "text_on_image",
]


def text_on_image(image: ImageDraw.ImageDraw, *args, **kwargs):
    image.text(fill="black", anchor='la', language='zh-Hans', *args, **kwargs)


class TextSize(BaseModel):
    width: int
    height: int


class SingletonImage:
    __instance: "SingletonImage" = None
    __draw = ImageDraw
    __img = Image

    def __new__(cls, *args, **kwargs):
        if SingletonImage.__instance is None:
            SingletonImage.__instance = object.__new__(cls, *args, **kwargs)
            SingletonImage.__instance.__img = Image.new("RGB", (1000, 1000))
            SingletonImage.__instance.__draw = ImageDraw.Draw(SingletonImage.__instance.__img, "RGB")

        return SingletonImage.__instance

    def __init__(self):
        pass

    def get_size(self, text: str, font: ImageFont, spacing: int = 4) -> TextSize:
        size = self.__draw.textbbox(xy=(0, 0), text=text, font=font, anchor='la', language='zh-Hans', spacing=spacing)
        return TextSize(width=size[2] - size[0], height=size[3] - size[1])
