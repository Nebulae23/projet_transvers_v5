import unittest
from unittest.mock import Mock, patch
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from engine.graphics.shader_system import ShaderSystem
from engine.graphics.post_processor import PostProcessor
from engine.graphics.lighting_system import LightingSystem
from engine.graphics.effect_system import EffectSystem

class TestShaderSystem(unittest.TestCase):
    def setUp(self):
        self.shader_system = ShaderSystem()

    def test_shader_compilation(self):
        shaders = [
            'vertex.glsl',
            'fragment.glsl',
            'compute.glsl'
        ]
        
        for shader in shaders:
            result = self.shader_system.compile_shader(shader)
            self.assertTrue(result.success)
            self.assertIsNotNone(result.shader_id)

    def test_shader_uniforms(self):
        shader_id = self.shader_system.compile_shader('test.glsl').shader_id
        
        # Test various uniform types
        self.shader_system.set_uniform_float(shader_id, 'intensity', 0.5)
        self.shader_system.set_uniform_vec3(shader_id, 'color', [1, 0, 0])
        self.shader_system.set_uniform_mat4(shader_id, 'transform', np.eye(4))

class TestPostProcessor(unittest.TestCase):
    def setUp(self):
        self.post_processor = PostProcessor()

    def test_bloom_effect(self):
        mock_frame = np.random.rand(1080, 1920, 3)
        result = self.post_processor.apply_bloom(mock_frame, intensity=1.5)
        
        self.assertEqual(result.shape, mock_frame.shape)
        self.assertFalse(np.array_equal(result, mock_frame))

    def test_ray_shafts(self):
        mock_frame = np.random.rand(1080, 1920, 3)
        mock_depth = np.random.rand(1080, 1920)
        
        result = self.post_processor.apply_ray_shafts(
            mock_frame,
            mock_depth,
            light_pos=[0.5, 1.0, 0.0]
        )
        
        self.assertEqual(result.shape, mock_frame.shape)

class TestLightingSystem(unittest.TestCase):
    def setUp(self):
        self.lighting_system = LightingSystem()

    def test_shadow_mapping(self):
        light_pos = np.array([100, 100, 100])
        shadow_map = self.lighting_system.generate_shadow_map(
            light_pos,
            resolution=1024
        )
        
        self.assertEqual(shadow_map.shape, (1024, 1024))
        self.assertTrue(np.all((shadow_map >= 0) & (shadow_map <= 1)))

    def test_water_reflections(self):
        camera_pos = np.array([0, 10, 0])
        water_height = 0
        
        reflection_matrix = self.lighting_system.calculate_reflection_matrix(
            camera_pos,
            water_height
        )
        
        self.assertEqual(reflection_matrix.shape, (4, 4))

class TestEffectSystem(unittest.TestCase):
    def setUp(self):
        self.effect_system = EffectSystem()

    def test_aurora_generation(self):
        aurora = self.effect_system.generate_aurora(
            intensity=1.0,
            color=[0, 1, 0]
        )
        
        self.assertIsNotNone(aurora)
        self.assertTrue(hasattr(aurora, 'update'))

    def test_cloud_system(self):
        clouds = self.effect_system.generate_clouds(
            coverage=0.5,
            density=0.7
        )
        
        self.assertIsNotNone(clouds)
        self.assertTrue(hasattr(clouds, 'update'))

    def test_particle_effects(self):
        effects = ['rain', 'snow', 'leaves']
        
        for effect in effects:
            particles = self.effect_system.create_particle_system(
                effect_type=effect,
                num_particles=1000
            )
            
            self.assertEqual(len(particles), 1000)
            self.assertTrue(all(hasattr(p, 'position') for p in particles))
            self.assertTrue(all(hasattr(p, 'velocity') for p in particles))

if __name__ == '__main__':
    unittest.main()