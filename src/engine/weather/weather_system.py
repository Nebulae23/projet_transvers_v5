# src/engine/weather/weather_system.py

from typing import Optional
from enum import Enum, auto
from pathlib import Path
import json
import time
import os

# Standard imports from the new package structure
from .weather_generator import WeatherGenerator, Season
from .weather_condition import WeatherCondition

class WeatherSystem:
    """
    Système principal pour la gestion de la météo dans le jeu.
    Utilise WeatherGenerator pour déterminer les conditions météo,
    gère les saisons et applique les effets correspondants (logique d'application non implémentée ici).
    """
    def __init__(self, patterns_file: str = "src/engine/weather/data/weather_patterns.json"):
        """
        Initialise le système météo.
        :param patterns_file: Chemin vers le fichier de patterns météo pour le générateur.
        """
        self.weather_generator = WeatherGenerator(patterns_file)
        # Potentiellement, initialiser ici les systèmes d'effets (visuels, audio, gameplay)
        print("WeatherSystem initialized.")

    def update(self, delta_time: float):
        """
        Met à jour le système météo. Appelle le générateur et gère les transitions/effets.
        :param delta_time: Temps écoulé depuis la dernière mise à jour.
        """
        # 1. Mettre à jour le générateur
        previous_condition = self.weather_generator.get_current_condition()
        self.weather_generator.update(delta_time)
        current_condition = self.weather_generator.get_current_condition()

        # 2. Détecter les changements de condition pour déclencher des transitions/effets
        if current_condition != previous_condition:
            print(f"Weather condition changed from {previous_condition} to {current_condition}")
            self.apply_weather_effects(current_condition)

        # 3. Mettre à jour les effets actifs (non implémenté ici)
        # Exemple: self.update_particle_effects(current_condition, delta_time)
        # Exemple: self.update_audio_ambiance(current_condition)

    def get_current_condition(self) -> Optional[WeatherCondition]:
        """Retourne la condition météo actuelle déterminée par le générateur."""
        return self.weather_generator.get_current_condition()

    def set_season(self, season: Season):
        """
        Définit la saison actuelle dans le générateur météo.
        :param season: La nouvelle saison (objet Season).
        """
        print(f"WeatherSystem: Setting season to {season.name}")
        self.weather_generator.update_season(season)

    def force_weather_condition(self, condition_name: str, duration: int):
        """
        Force une condition météo spécifique, en contournant temporairement le générateur.
        Utile pour des événements scriptés ou des tests.
        :param condition_name: Nom de la condition (doit correspondre à une définition connue).
        :param duration: Durée de la condition forcée (en ticks ou unités de temps).
        """
        print(f"WeatherSystem: Forcing weather condition to {condition_name} for {duration} ticks")
        # Il faudrait idéalement avoir accès aux définitions complètes des conditions ici
        # Pour l'instant, on crée une condition simple
        forced_condition = WeatherCondition(condition_name, duration)
        self.weather_generator.set_current_condition(forced_condition)
        self.apply_weather_effects(forced_condition)


    def apply_weather_effects(self, condition: Optional[WeatherCondition]):
        """
        Applique les effets visuels, sonores et de gameplay associés à la condition météo.
        (Logique spécifique à implémenter en fonction des systèmes d'effets).
        """
        if condition:
            print(f"Applying effects for weather condition: {condition.name}")
            # Exemple:
            # self.visual_effects_manager.apply(condition.effects.visual)
            # self.audio_manager.play_ambiance(condition.effects.audio)
            # self.gameplay_effects_manager.apply(condition.effects.gameplay)
        else:
            print("Applying default/clear weather effects.")
            # Appliquer les effets par défaut (ciel clair, etc.)

    def cleanup(self):
        """Clean up resources used by the weather system."""
        # Nothing to clean up for now
        print("Weather system cleaned up")

# Exemple d'utilisation
if __name__ == "__main__":
    # Assurer l'existence des fichiers nécessaires pour l'exemple
    data_dir = Path("src/engine/weather/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    patterns_path = data_dir / "weather_patterns.json"
    condition_path = Path("src/engine/weather/weather_condition.py")
    generator_path = Path("src/engine/weather/weather_generator.py")

    if not patterns_path.exists():
         # Créer un fichier JSON minimal si absent
         print(f"Creating dummy {patterns_path}")
         dummy_patterns = {
             "seasons": {
                 "SPRING": {
                     "conditions": ["Clear", "LightRain"], "weights": [0.8, 0.2],
                     "min_duration": 10, "max_duration": 20,
                     "transitions": {
                         "Clear": {"LightRain": 1.0},
                         "LightRain": {"Clear": 1.0}
                     }
                 }
             },
             "special_events": []
         }
         with open(patterns_path, 'w') as f:
             json.dump(dummy_patterns, f, indent=2)

    if not condition_path.exists():
        print(f"Creating dummy {condition_path}")
        with open(condition_path, "w") as f:
             f.write("class WeatherCondition:\n")
             f.write("    def __init__(self, name: str, duration: int):\n")
             f.write("        self.name = name\n")
             f.write("        self.duration = duration\n")
             f.write("    def __repr__(self):\n")
             f.write("        return f'WeatherCondition(name=\"{self.name}\", duration={self.duration})'\n")

    if not generator_path.exists():
         print(f"Creating dummy {generator_path}")
         # Recréer le générateur si nécessaire (simplifié)
         with open(generator_path, "w") as f:
             f.write("""
import json
import random
from enum import Enum, auto
from typing import Optional, Dict, List, Any
from pathlib import Path
from .weather_condition import WeatherCondition

class Season(Enum): SPRING=auto(); SUMMER=auto(); AUTUMN=auto(); WINTER=auto()

class WeatherGenerator:
    def __init__(self, patterns_file: str):
        self.patterns_file_path = Path(patterns_file)
        self.patterns = {}
        self.special_events = []
        self.current_season = Season.SPRING
        self.current_condition = None
        self.current_condition_duration = 0
        self.load_patterns()
        if not self.current_condition: self.force_next_condition()
    def load_patterns(self):
        try:
            with open(self.patterns_file_path, 'r') as f: data = json.load(f)
            self.patterns = data.get("seasons", {})
            self.special_events = data.get("special_events", [])
        except Exception as e: print(f"Failed to load patterns: {e}")
    def update_season(self, new_season: Season): self.current_season = new_season; self.force_next_condition()
    def update(self, delta_time: float):
        if self.current_condition_duration > 0: self.current_condition_duration -= 1
        else: self.force_next_condition()
    def generate_next_condition(self) -> WeatherCondition:
        season_data = self.patterns.get(self.current_season.name, {})
        conditions = season_data.get("conditions", ["Clear"])
        weights = season_data.get("weights", [1.0] * len(conditions))
        min_dur = season_data.get("min_duration", 10)
        max_dur = season_data.get("max_duration", 20)
        name = random.choices(conditions, weights=weights, k=1)[0]
        duration = random.randint(min_dur, max_dur)
        return WeatherCondition(name, duration)
    def try_generate_special_event(self): return None # Simplifié
    def set_current_condition(self, condition: WeatherCondition): self.current_condition = condition; self.current_condition_duration = condition.duration
    def force_next_condition(self): self.set_current_condition(self.generate_next_condition())
    def get_current_condition(self): return self.current_condition
""")

    # Recharger les modules après création potentielle
    import importlib
    import sys
    # Ajouter le répertoire parent de 'src' au path pour permettre l'import
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir.parent.parent.parent # Ajuster si nécessaire
    sys.path.insert(0, str(project_root))

    # Import the local modules explicitly
    from src.engine.weather.weather_condition import WeatherCondition
    from src.engine.weather.weather_generator import WeatherGenerator, Season

    weather_system = WeatherSystem(str(patterns_path))
    print(f"Initial weather: {weather_system.get_current_condition()}")

    # Simuler le temps qui passe
    for i in range(50):
        weather_system.update(1.0) # Simule 1 tick
        print(f"Tick {i+1}: Current Weather: {weather_system.get_current_condition()}")
        time.sleep(0.1) # Pause pour lisibilité

        # Changer de saison après 25 ticks
        if i == 24:
            print("\nChanging season to WINTER\n")
            weather_system.set_season(Season.WINTER)