# tests/weather/test_weather_effects.py
import unittest
from unittest.mock import MagicMock, patch

# Assuming these imports based on project structure and context
from src.engine.weather.weather_effects import WeatherEffects # Assuming this class manages applying effects
from src.engine.weather.weather_condition import WeatherType, WeatherCondition, WeatherParams
# Mocks for dependencies
from tests.weather.mocks.mock_effects import MockParticleSystem, MockPostProcessSystem, MockAudioSystem
from src.engine.ecs.components import TransformComponent, StatsComponent # Example components affected by weather
from src.engine.ecs.entity import Entity # Assuming an Entity class

# Sample WeatherParams focusing on effects
CLEAR_PARAMS = WeatherParams(particle_system="clear_particles", sound_effect="ambient_day", post_process_effect="standard_pp", production_modifier=1.0, defense_modifier=1.0, movement_speed_modifier=1.0)
RAIN_PARAMS = WeatherParams(particle_system="rain_particles", sound_effect="rain_light", post_process_effect="wet_screen_pp", production_modifier=0.9, defense_modifier=1.0, movement_speed_modifier=0.95)
STORM_PARAMS = WeatherParams(particle_system="storm_particles", sound_effect="storm_heavy", post_process_effect="heavy_rain_pp", production_modifier=0.7, defense_modifier=0.9, movement_speed_modifier=0.8)

class TestWeatherEffects(unittest.TestCase):

    def setUp(self):
        """Set up mocks and the WeatherEffects instance."""
        self.mock_particle_system = MockParticleSystem()
        self.mock_post_process_system = MockPostProcessSystem()
        self.mock_audio_system = MockAudioSystem()

        # Instantiate WeatherEffects with mocked dependencies
        self.weather_effects = WeatherEffects(
            particle_system=self.mock_particle_system,
            post_process_system=self.mock_post_process_system,
            audio_system=self.mock_audio_system
        )

        # Create sample weather conditions
        self.clear_condition = WeatherCondition(WeatherType.CLEAR, CLEAR_PARAMS)
        self.rain_condition = WeatherCondition(WeatherType.RAIN, RAIN_PARAMS)
        self.storm_condition = WeatherCondition(WeatherType.STORM, STORM_PARAMS)

        # Create a mock entity with relevant components for gameplay tests
        self.mock_entity = Entity(entity_id=1)
        self.mock_entity.add_component(TransformComponent(x=0, y=0)) # Needed for particle positioning?
        self.mock_entity.add_component(StatsComponent(base_production=10, base_defense=5, base_movement_speed=100))


    def test_visual_effects(self):
        """Test the application of visual effects (particles and post-processing)."""
        # Apply effects for rain
        self.weather_effects.apply_visuals(self.rain_condition)

        # Check if particle system was called correctly
        self.mock_particle_system.start_effect.assert_called_once_with(
            self.rain_condition.params.particle_system,
            # Add position/area parameters if apply_visuals needs them
        )
        # Check if post-processing system was called correctly
        self.mock_post_process_system.apply_effect.assert_called_once_with(
            self.rain_condition.params.post_process_effect
        )

        # Reset mocks and test another condition
        self.mock_particle_system.reset_mock()
        self.mock_post_process_system.reset_mock()

        self.weather_effects.apply_visuals(self.clear_condition)
        self.mock_particle_system.start_effect.assert_called_once_with(self.clear_condition.params.particle_system)
        self.mock_post_process_system.apply_effect.assert_called_once_with(self.clear_condition.params.post_process_effect)


    def test_audio_effects(self):
        """Test the application of audio effects."""
        # Apply effects for storm
        self.weather_effects.apply_audio(self.storm_condition)

        # Check if audio system was called correctly
        self.mock_audio_system.play_ambient_sound.assert_called_once_with(
            self.storm_condition.params.sound_effect
        )

        # Reset mock and test another condition
        self.mock_audio_system.reset_mock()
        self.weather_effects.apply_audio(self.clear_condition)
        self.mock_audio_system.play_ambient_sound.assert_called_once_with(self.clear_condition.params.sound_effect)


    def test_gameplay_impact(self):
        """Test the application of gameplay modifiers to entities."""
        # Assume apply_gameplay_modifiers takes a condition and a list of entities
        entities_to_affect = [self.mock_entity]

        # Apply storm effects
        self.weather_effects.apply_gameplay_modifiers(self.storm_condition, entities_to_affect)

        # Check if the entity's stats were modified correctly
        stats = self.mock_entity.get_component(StatsComponent)
        self.assertAlmostEqual(stats.current_production, 10 * self.storm_condition.params.production_modifier) # 10 * 0.7 = 7
        self.assertAlmostEqual(stats.current_defense, 5 * self.storm_condition.params.defense_modifier)       # 5 * 0.9 = 4.5
        self.assertAlmostEqual(stats.current_movement_speed, 100 * self.storm_condition.params.movement_speed_modifier) # 100 * 0.8 = 80

        # Apply clear weather (should reset modifiers or apply 1.0x)
        # This depends on how modifiers are handled (additive/multiplicative, reset logic)
        # Assuming a reset or re-application based on the new condition:
        self.weather_effects.apply_gameplay_modifiers(self.clear_condition, entities_to_affect)
        stats = self.mock_entity.get_component(StatsComponent)
        self.assertAlmostEqual(stats.current_production, 10 * self.clear_condition.params.production_modifier) # 10 * 1.0 = 10
        self.assertAlmostEqual(stats.current_defense, 5 * self.clear_condition.params.defense_modifier)       # 5 * 1.0 = 5
        self.assertAlmostEqual(stats.current_movement_speed, 100 * self.clear_condition.params.movement_speed_modifier) # 100 * 1.0 = 100


if __name__ == '__main__':
    unittest.main()