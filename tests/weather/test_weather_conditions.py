# tests/weather/test_weather_conditions.py
import unittest
from src.engine.weather.weather_condition import WeatherType, WeatherCondition, WeatherParams

class TestWeatherConditions(unittest.TestCase):
    def setUp(self):
        # Define some sample weather parameters for testing
        self.clear_params = WeatherParams(
            visibility_range=1000.0, production_modifier=1.0, defense_modifier=1.0,
            movement_speed_modifier=1.0, transition_duration=5.0, min_duration=300.0,
            max_duration=900.0, particle_system="clear", sound_effect="ambient_day"
        )
        self.rain_params = WeatherParams(
            visibility_range=500.0, production_modifier=0.9, defense_modifier=1.0,
            movement_speed_modifier=0.95, transition_duration=10.0, min_duration=600.0,
            max_duration=1800.0, particle_system="rain", sound_effect="rain_light"
        )
        self.storm_params = WeatherParams(
            visibility_range=200.0, production_modifier=0.7, defense_modifier=0.9,
            movement_speed_modifier=0.8, transition_duration=15.0, min_duration=1200.0,
            max_duration=3600.0, particle_system="storm", sound_effect="storm_heavy"
        )

        # Create WeatherCondition instances
        self.clear_condition = WeatherCondition(WeatherType.CLEAR, self.clear_params)
        self.rain_condition = WeatherCondition(WeatherType.RAIN, self.rain_params)
        self.storm_condition = WeatherCondition(WeatherType.STORM, self.storm_params)

    def test_weather_type_creation(self):
        """Test the creation and basic parameters of WeatherCondition."""
        self.assertEqual(self.clear_condition.weather_type, WeatherType.CLEAR)
        self.assertEqual(self.clear_condition.params.visibility_range, 1000.0)
        self.assertEqual(self.clear_condition.params.production_modifier, 1.0)
        self.assertEqual(self.clear_condition.params.defense_modifier, 1.0)
        self.assertEqual(self.clear_condition.params.movement_speed_modifier, 1.0)
        self.assertEqual(self.clear_condition.params.transition_duration, 5.0)
        self.assertEqual(self.clear_condition.params.min_duration, 300.0)
        self.assertEqual(self.clear_condition.params.max_duration, 900.0)
        self.assertEqual(self.clear_condition.params.particle_system, "clear")
        self.assertEqual(self.clear_condition.params.sound_effect, "ambient_day")

        self.assertEqual(self.rain_condition.weather_type, WeatherType.RAIN)
        self.assertEqual(self.rain_condition.params.visibility_range, 500.0)
        self.assertEqual(self.rain_condition.params.production_modifier, 0.9)
        self.assertEqual(self.rain_condition.params.movement_speed_modifier, 0.95)


        self.assertEqual(self.storm_condition.weather_type, WeatherType.STORM)
        self.assertEqual(self.storm_condition.params.visibility_range, 200.0)
        self.assertEqual(self.storm_condition.params.production_modifier, 0.7)
        self.assertEqual(self.storm_condition.params.defense_modifier, 0.9)


    def test_weather_transitions(self):
        """Test the transitions between weather conditions."""
        # This test verifies access to transition-related parameters.
        # Actual transition logic is handled by WeatherSystem/WeatherGenerator.
        self.assertEqual(self.clear_condition.params.transition_duration, 5.0)
        self.assertEqual(self.rain_condition.params.transition_duration, 10.0)
        self.assertEqual(self.storm_condition.params.transition_duration, 15.0)
        # A more complex test would involve mocking the system managing transitions.
        # print("Note: Transition logic testing requires WeatherSystem/Generator context.")
        self.assertTrue(True) # Placeholder confirmation

    def test_weather_effects(self):
        """Test the application of weather effects (parameter access)."""
        # This test checks if the parameters representing effects are accessible.
        # Actual effect application is tested elsewhere (e.g., integration tests).
        self.assertEqual(self.clear_condition.params.production_modifier, 1.0)
        self.assertEqual(self.rain_condition.params.movement_speed_modifier, 0.95)
        self.assertEqual(self.storm_condition.params.defense_modifier, 0.9)
        self.assertEqual(self.storm_condition.params.particle_system, "storm")
        self.assertEqual(self.rain_condition.params.sound_effect, "rain_light")
        self.assertTrue(True) # Placeholder confirmation

if __name__ == '__main__':
    unittest.main()