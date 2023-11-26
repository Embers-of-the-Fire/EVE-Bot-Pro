import unittest

import skills.skill_render
import database


class TestSkillRender(unittest.TestCase):
    def test_skill_image_render(self):
        skr = database.skill_db.SkillDB().get_skill_recursive(9955).unwrap()
        skills.skill_render.render_skill_image(skr, True)
        skr = database.skill_db.Skill(type_id=34, group=[])
        skills.skill_render.render_skill_image(skr, True)
        skr = database.skill_db.SkillDB().get_skill_recursive(28659).unwrap()
        skills.skill_render.render_skill_image(skr, True)


if __name__ == '__main__':
    unittest.main()
