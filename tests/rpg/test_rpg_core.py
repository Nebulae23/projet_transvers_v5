import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from engine.skills.skill_system import SkillSystem
from engine.progression.level_system import LevelSystem
from engine.inventory.equipment_system import EquipmentSystem
from engine.character.character import Character

class TestRPGCore(unittest.TestCase):
    def setUp(self):
        self.skill_system = SkillSystem()
        self.level_system = LevelSystem()
        self.equipment_system = EquipmentSystem()
        self.character = Character('Test', 'Warrior')

    def test_skill_system(self):
        # Test principal skills
        skills = self.skill_system.get_class_skills('Warrior')
        self.assertEqual(len(skills), 6)

        # Test skill evolution
        skill = skills[0]
        evolutions = self.skill_system.get_evolution_paths(skill)
        self.assertEqual(len(evolutions), 3)

        # Test procedural skills
        self.character.level = 51
        proc_skill = self.skill_system.generate_procedural_skill(self.character)
        self.assertIsNotNone(proc_skill)
        self.assertTrue(proc_skill.is_procedural)

    def test_level_system(self):
        # Test normal leveling
        initial_level = self.character.level
        self.level_system.gain_experience(self.character, 1000)
        self.assertGreater(self.character.level, initial_level)

        # Test paragon levels
        self.character.level = 50
        self.level_system.gain_experience(self.character, 10000)
        self.assertGreater(self.character.paragon_level, 0)

    def test_equipment_system(self):
        # Test equipment generation
        weapon = self.equipment_system.generate_item('weapon', 50)
        self.assertGreater(weapon.power, 0)

        # Test relic system
        relic = self.equipment_system.generate_relic(50)
        self.assertGreater(len(relic.effects), 0)

        # Test equipment effects
        initial_power = self.character.total_power
        self.equipment_system.equip_item(self.character, weapon)
        self.assertGreater(self.character.total_power, initial_power)

if __name__ == '__main__':
    unittest.main()