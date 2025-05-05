import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from engine.skills.skill_system import SkillSystem
from engine.character.character import Character

class TestSkillSystem(unittest.TestCase):
    def setUp(self):
        self.skill_system = SkillSystem()
        self.classes = ['Warrior', 'Mage', 'Ranger', 'Cleric', 'Rogue', 'Paladin', 'Necromancer', 'Druid']

    def test_all_classes_have_principal_skills(self):
        for class_name in self.classes:
            char = Character('Test', class_name)
            skills = self.skill_system.get_class_skills(class_name)
            self.assertEqual(len(skills), 6, f'{class_name} should have 6 principal skills')

    def test_skill_evolution_paths(self):
        for class_name in self.classes:
            skills = self.skill_system.get_class_skills(class_name)
            for skill in skills:
                paths = self.skill_system.get_evolution_paths(skill)
                self.assertEqual(len(paths), 3, f'Skill {skill.name} should have 3 evolution paths')
                
                # Test each evolution path increases power
                for path in paths:
                    self.assertGreater(path.power, skill.base_power)

    def test_procedural_skill_generation(self):
        char = Character('Test', 'Warrior')
        char.level = 51

        # Generate multiple skills to test variation
        generated_skills = []
        for _ in range(10):
            skill = self.skill_system.generate_procedural_skill(char)
            generated_skills.append(skill)

            self.assertIsNotNone(skill)
            self.assertTrue(skill.is_procedural)
            self.assertGreater(skill.power, 0)

        # Verify skills are different
        unique_powers = len(set(skill.power for skill in generated_skills))
        self.assertGreater(unique_powers, 1, 'Procedural skills should have variation')

    def test_skill_requirements(self):
        char = Character('Test', 'Warrior')
        skills = self.skill_system.get_class_skills('Warrior')

        # Test level requirements
        char.level = 1
        self.assertFalse(self.skill_system.can_learn_skill(char, skills[-1]))

        char.level = 50
        self.assertTrue(self.skill_system.can_learn_skill(char, skills[-1]))

    def test_skill_effects(self):
        char = Character('Test', 'Warrior')
        skills = self.skill_system.get_class_skills('Warrior')

        for skill in skills:
            # Apply skill effect
            initial_stats = char.stats.copy()
            self.skill_system.apply_skill_effect(char, skill)
            
            # Verify some stat was modified
            self.assertNotEqual(initial_stats, char.stats)

if __name__ == '__main__':
    unittest.main()