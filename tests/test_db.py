import asyncio
import unittest
from devtools import debug

import database
import monad_std


class TestDB(unittest.TestCase):
    def test_typename_db(self):
        ins = database.typename_db.TypeNameDB()
        self.assertEqual(id(ins), id(database.typename_db.TypeNameDB()))
        exp_value = database.typename_db.TypeName(type_id=34, type_name='三钛合金', published=True)
        name = ins.get_name(34)
        self.assertEqual(name, exp_value)
        typeid = ins.get_id("三钛合金")
        self.assertEqual(typeid.unwrap(), exp_value)
        typeidl = ins.get_id_likely("三钛")
        self.assertEqual(typeidl.unwrap(), exp_value)
        typeidl = ins.get_id_with_pattern("三%金")
        self.assertEqual(typeidl.unwrap(), exp_value)

    def test_skill_db(self):
        ins = database.skill_db.SkillDB()
        self.assertEqual(id(ins), id(database.skill_db.SkillDB()))
        sk = ins.get_skill(266)
        self.assertIsInstance(sk, monad_std.option.OpSome)
        skr = ins.get_skill_recursive(9955)
        debug(skr)
        self.assertEqual(len(skr.unwrap()), 3)
        self.assertEqual(ins.get_skill_restriction(9955), 0)
        self.assertEqual(ins.get_skill_restriction(3300), 5)

    def test_blp_db(self):
        ins = database.blueprint_db.BlueprintDB()
        self.assertEqual(id(ins), id(database.blueprint_db.BlueprintDB()))
        blp = ins.get_blp(77405)
        debug(blp.unwrap_unchecked())
        blp = ins.get_recursive_blp(28660)
        debug(blp.unwrap_unchecked())

    def test_market_db(self):
        ins = database.price_db.PriceDB()
        self.assertEqual(id(ins), id(database.price_db.PriceDB()))
        loop = asyncio.get_event_loop()
        debug(loop.run_until_complete(ins.get_jita_price(34, 'se')))
        debug(loop.run_until_complete(ins.get_jita_prices([34, 28659], 'se')))


if __name__ == '__main__':
    unittest.main()
