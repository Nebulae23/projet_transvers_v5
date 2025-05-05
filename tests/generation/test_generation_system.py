import unittest
from unittest.mock import Mock, patch
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from engine.generation.world_generator import WorldGenerator
from engine.generation.npc_generator import NPCGenerator
from engine.generation.quest_generator import QuestGenerator
from engine.generation.asset_generator import AssetGenerator

class TestWorldGenerator(unittest.TestCase):
    def setUp(self):
        self.world_generator = WorldGenerator()
        self.size = 256
        self.seed = 42

    def test_terrain_generation(self):
        terrain = self.world_generator.generate_terrain(
            size=self.size,
            seed=self.seed,
            octaves=6
        )
        
        self.assertEqual(terrain.shape, (self.size, self.size))
        self.assertTrue(np.all((terrain >= 0) & (terrain <= 1)))

    def test_biome_generation(self):
        terrain = self.world_generator.generate_terrain(self.size, self.seed)
        biomes = self.world_generator.generate_biomes(terrain)
        
        self.assertEqual(biomes.shape, terrain.shape)
        unique_biomes = np.unique(biomes)
        self.assertGreaterEqual(len(unique_biomes), 4)

    def test_resource_distribution(self):
        terrain = self.world_generator.generate_terrain(self.size, self.seed)
        resources = self.world_generator.distribute_resources(terrain)
        
        self.assertEqual(resources.shape, terrain.shape)
        self.assertGreater(np.sum(resources > 0), 0)

class TestNPCGenerator(unittest.TestCase):
    def setUp(self):
        self.npc_generator = NPCGenerator()

    def test_npc_generation(self):
        npc = self.npc_generator.generate_npc(level=50)
        
        self.assertIsNotNone(npc.personality_traits)
        self.assertGreaterEqual(len(npc.personality_traits), 3)
        self.assertEqual(npc.level, 50)

    def test_npc_behavior(self):
        npc = self.npc_generator.generate_npc(level=50)
        schedule = self.npc_generator.generate_schedule(npc)
        
        self.assertEqual(len(schedule), 24)  # 24 hours
        self.assertTrue(all(isinstance(activity, str) for activity in schedule))

    def test_npc_relationships(self):
        npcs = [self.npc_generator.generate_npc(level=50) for _ in range(5)]
        relationships = self.npc_generator.generate_relationships(npcs)
        
        self.assertGreater(len(relationships), 0)

class TestQuestGenerator(unittest.TestCase):
    def setUp(self):
        self.quest_generator = QuestGenerator()

    def test_quest_generation(self):
        quest = self.quest_generator.generate_quest(level=50)
        
        self.assertIn('objectives', quest)
        self.assertIn('rewards', quest)
        self.assertGreater(len(quest['objectives']), 0)

    def test_quest_chain(self):
        chain = self.quest_generator.generate_quest_chain(length=3)
        
        self.assertEqual(len(chain), 3)
        for i in range(len(chain)-1):
            self.assertEqual(
                chain[i]['completion_required_for'],
                chain[i+1]['id']
            )

class TestAssetGenerator(unittest.TestCase):
    def setUp(self):
        self.asset_generator = AssetGenerator()

    def test_building_variation(self):
        base_building = {'type': 'house', 'style': 'medieval'}
        variations = self.asset_generator.generate_variations(
            base_building,
            num_variations=5
        )
        
        self.assertEqual(len(variations), 5)
        self.assertTrue(all(v['type'] == 'house' for v in variations))
        self.assertTrue(any(v != variations[0] for v in variations[1:]))

    def test_prop_generation(self):
        props = self.asset_generator.generate_props(
            biome='forest',
            density=0.5,
            area=100
        )
        
        self.assertGreater(len(props), 0)
        self.assertTrue(all('position' in p for p in props))

if __name__ == '__main__':
    unittest.main()