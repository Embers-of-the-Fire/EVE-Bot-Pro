import asyncio
import unittest
import uuid
from devtools import debug

import blueprints
import constant
from database.blueprint_db import BlueprintDB


class TestBlueprintRender(unittest.TestCase):
    def test_blp_getter(self):
        ins = BlueprintDB()
        self.assertEqual(id(ins), id(BlueprintDB()))
        res = blueprints.blp_process.get_blp_material(28660, blueprints.blp_process.BlueprintFactor())
        print(res)
        res = blueprints.blp_process.get_blp_material(28660, blueprints.blp_process.BlueprintFactor(
            manu_material=10,
            extra_material=0.5,
            extra_time=1.5
        ))
        print(res)

    def test_blp_render(self):
        fp = constant.filepath.image_cache_path + str(uuid.uuid4()) + ".png"
        blueprints.blp_render.BlueprintRenderer.render_plain(28660, blueprints.blp_process.BlueprintFactor(
            manu_material=10,
            extra_material=0.5,
            extra_time=1.5
        ), fp)
        print(fp)

    def test_blp_rec_getter(self):
        res = blueprints.blp_process.get_blp_material_recursive(
            28660,
            blueprints.blp_process.BlueprintFactor(
                manu_material=10,
                extra_material=0.5,
            )
        )
        debug(res.unwrap_unchecked())

    def test_blp_rec_render(self):
        fp = constant.filepath.image_cache_path + str(uuid.uuid4()) + ".png"
        blueprints.blp_render.BlueprintRenderer.render_recursive(28660, blueprints.blp_process.BlueprintFactor(
            manu_material=10,
            extra_material=0.5,
            extra_time=1.5
        ), fp)
        print(fp)

    def test_blp_mkt_getter(self):
        loop = asyncio.get_event_loop()
        val = loop.run_until_complete(blueprints.blp_market.BlueprintPrice.from_material(
            blueprints.blp_process.get_blp_material(28660).unwrap(),
            "se"
        ))
        debug(val)

    def test_factor(self):
        v = blueprints.blp_process.BlueprintFactor(
            manu_material=10,
            extra_material=0.5,
            extra_time=1.5
        )
        debug(v.reaction_material_factor ** 5, v.time_factor)

    def test_blp_mkt_render(self):
        fp = constant.filepath.image_cache_path + str(uuid.uuid4()) + ".png"
        loop = asyncio.get_event_loop()
        val = loop.run_until_complete(blueprints.blp_market.BlueprintPrice.from_material(
            blueprints.blp_process.get_blp_material_recursive(
                28660,
                blueprints.blp_process.BlueprintFactor(
                    manu_material=10,
                    manu_time=10,
                    extra_material=5.5,
                    extra_time=7.5,
                )
            ).unwrap(),
            "se"
        ))
        with open(fp, 'wb+') as f:
            blueprints.blp_render.BlueprintRenderer.render_price(val, f)
        print(fp)


if __name__ == '__main__':
    unittest.main()
