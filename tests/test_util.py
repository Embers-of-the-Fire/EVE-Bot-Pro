import unittest

from PIL import ImageFont
from devtools import debug

import constant
from database.price_db import MarketPrice
from utils import valueop, imageop


class TestUtil(unittest.TestCase):
    def test_valueop(self):
        fmt = valueop.format_time(8000)
        self.assertEqual(fmt, "0天02小时13分20秒")
        fmt = valueop.format_time(0)
        self.assertEqual(fmt, "0天00小时00分00秒")
        fmt = valueop.format_time(5000000)
        self.assertEqual(fmt, "57天20小时53分20秒")
        fmt = valueop.format_time(-50)
        self.assertEqual(fmt, "0天00小时00分00秒")

        fmt = valueop.format_value_comma_separated(10)
        self.assertEqual(fmt, "10")
        fmt = valueop.format_value_comma_separated(10000)
        self.assertEqual(fmt, "10,000")
        fmt = valueop.format_value_comma_separated(1000.05)
        self.assertEqual(fmt, "1,000.05")

    def test_imageop(self):
        size = imageop.SingletonImage().get_size(
            f"用时：140，是，sf,",
            ImageFont.truetype(constant.filepath.font_root_path + "msyhbd.ttc", 30)
        )
        debug(size)


if __name__ == '__main__':
    unittest.main()
