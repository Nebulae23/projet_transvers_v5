# src/engine/weather/weather_generator.py

import json
import random
from enum import Enum, auto
from typing import Optional, Dict, List, Any
from pathlib import Path

# Standard import from the new package structure
from .weather_condition import WeatherCondition

class Season(Enum):
    SPRING = auto()
    SUMMER = auto()
    AUTUMN = auto()
    FALL = AUTUMN # Alias
    WINTER = auto()

class WeatherGenerator:
    """
    Génère des conditions météorologiques basées sur les saisons,
    les patterns définis et les événements spéciaux.
    """
    def __init__(self, patterns_file: str = "src/engine/weather/data/weather_patterns.json"):
        """
        Initialise le générateur météo.
        :param patterns_file: Chemin vers le fichier JSON contenant les patterns météo.
        """
        self.patterns_file_path = Path(patterns_file)
        self.patterns: Dict[str, Any] = {}
        self.special_events: List[Dict[str, Any]] = []
        self.current_season: Season = Season.SPRING # Saison par défaut
        self.current_condition: Optional[WeatherCondition] = None
        self.current_condition_duration: int = 0 # Durée restante en ticks/updates
        self.time_in_current_season: int = 0 # Pourrait être utilisé pour la logique de saison

        self.load_patterns()
        # Initialiser la première condition
        if not self.current_condition:
             self.force_next_condition()

    def load_patterns(self):
        """Charge les patterns météo depuis le fichier JSON."""
        try:
            with open(self.patterns_file_path, 'r') as f:
                data = json.load(f)
            self.patterns = data.get("seasons", {})
            self.special_events = data.get("special_events", [])
            print(f"Weather patterns loaded successfully from {self.patterns_file_path}")
        except FileNotFoundError:
            print(f"Error: Weather patterns file not found at {self.patterns_file_path}")
            self.patterns = {}
            self.special_events = []
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {self.patterns_file_path}")
            self.patterns = {}
            self.special_events = []

    def update_season(self, new_season: Season):
        """
        Met à jour la saison actuelle.
        Peut forcer un changement de météo si la condition actuelle n'est pas valide
        pour la nouvelle saison.
        """
        if self.current_season != new_season:
            print(f"Season changed to {new_season.name}")
            self.current_season = new_season
            self.time_in_current_season = 0
            # Vérifier si la condition actuelle est valide pour la nouvelle saison
            season_patterns = self.patterns.get(self.current_season.name)
            if season_patterns and self.current_condition:
                 allowed_conditions = season_patterns.get("conditions", [])
                 if self.current_condition.name not in allowed_conditions:
                     print(f"Current condition {self.current_condition.name} not valid for {new_season.name}. Forcing change.")
                     self.force_next_condition()


    def update(self, delta_time: float):
        """
        Met à jour l'état du générateur météo. Doit être appelé à chaque tick/frame.
        :param delta_time: Temps écoulé depuis la dernière mise à jour (peut être utilisé si la durée est en secondes).
                          Ici, nous supposons que la durée est en ticks, donc delta_time n'est pas directement utilisé pour décrémenter.
        """
        self.time_in_current_season += 1
        if self.current_condition_duration > 0:
            self.current_condition_duration -= 1
        else:
            # Essayer de déclencher un événement spécial avant de passer à la condition suivante
            special_condition = self.try_generate_special_event()
            if special_condition:
                self.set_current_condition(special_condition)
            else:
                next_condition = self.generate_next_condition()
                self.set_current_condition(next_condition)

    def generate_next_condition(self) -> WeatherCondition:
        """
        Génère la prochaine condition météo normale basée sur la saison actuelle
        et les probabilités de transition.
        """
        season_name = self.current_season.name
        if season_name not in self.patterns:
            print(f"Warning: No weather patterns defined for season {season_name}. Using default.")
            # Retourner une condition par défaut ou gérer l'erreur
            return WeatherCondition("Clear", 3600) # Exemple de défaut

        season_data = self.patterns[season_name]
        transitions = season_data.get("transitions", {})
        possible_conditions = season_data.get("conditions", ["Clear"])
        weights = season_data.get("weights", [1.0] * len(possible_conditions))
        min_duration = season_data.get("min_duration", 600)
        max_duration = season_data.get("max_duration", 3600)

        next_condition_name = "Clear" # Défaut

        if self.current_condition and self.current_condition.name in transitions:
            # Utiliser les probabilités de transition si la condition actuelle a des transitions définies
            transition_rules = transitions[self.current_condition.name]
            cond_names = list(transition_rules.keys())
            cond_weights = list(transition_rules.values())
            if sum(cond_weights) > 0: # Éviter l'erreur avec random.choices si tous les poids sont 0
                 next_condition_name = random.choices(cond_names, weights=cond_weights, k=1)[0]
            else:
                 # Si pas de transition possible, choisir aléatoirement parmi les conditions de la saison
                 next_condition_name = random.choices(possible_conditions, weights=weights, k=1)[0]

        else:
            # Si pas de condition actuelle ou pas de transition définie, choisir selon les poids de la saison
            next_condition_name = random.choices(possible_conditions, weights=weights, k=1)[0]

        duration = random.randint(min_duration, max_duration)
        print(f"Generated next condition: {next_condition_name} for {duration} ticks")
        return WeatherCondition(next_condition_name, duration)

    def try_generate_special_event(self) -> Optional[WeatherCondition]:
        """
        Tente de générer un événement météorologique spécial basé sur les probabilités définies.
        """
        for event in self.special_events:
            prob = event.get("probability", 0)
            if random.random() < prob:
                allowed_seasons = event.get("allowed_seasons", [])
                required_condition = event.get("required_condition")

                season_ok = self.current_season.name in allowed_seasons
                condition_ok = (required_condition is None or
                                (self.current_condition and self.current_condition.name == required_condition))

                if season_ok and condition_ok:
                    name = event.get("name", "SpecialEvent")
                    min_dur = event.get("min_duration", 600)
                    max_dur = event.get("max_duration", 1800)
                    duration = random.randint(min_dur, max_dur)
                    print(f"Generated special event: {name} for {duration} ticks")
                    return WeatherCondition(name, duration)
        return None

    def set_current_condition(self, condition: WeatherCondition):
        """Met à jour la condition météo actuelle."""
        self.current_condition = condition
        self.current_condition_duration = condition.duration
        print(f"Setting current condition to: {condition.name} for {condition.duration} ticks")

    def force_next_condition(self):
        """Force la génération et l'application immédiate d'une nouvelle condition."""
        print("Forcing next weather condition...")
        # Tenter un événement spécial d'abord
        special_condition = self.try_generate_special_event()
        if special_condition:
            self.set_current_condition(special_condition)
        else:
            next_condition = self.generate_next_condition()
            self.set_current_condition(next_condition)

    def get_current_condition(self) -> Optional[WeatherCondition]:
        """Retourne la condition météo actuelle."""
        return self.current_condition

# Exemple d'utilisation (peut être retiré ou mis dans un bloc if __name__ == "__main__")
if __name__ == "__main__":
    # Create directory if needed
    data_dir = Path("src/engine/weather/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Make sure weather_condition.py exists
    condition_path = Path("src/engine/weather/weather_condition.py")
    if not condition_path.exists():
        print(f"Creating {condition_path}")
        with open(condition_path, "w") as f:
            f.write("class WeatherCondition:\n")
            f.write("    def __init__(self, name: str, duration: int):\n")
            f.write("        self.name = name\n")
            f.write("        self.duration = duration\n")
            f.write("    def __repr__(self):\n")
            f.write("        return f'WeatherCondition(name=\"{self.name}\", duration={self.duration})'\n")

    generator = WeatherGenerator()
    print(f"Initial condition: {generator.get_current_condition()}")

    # Simuler quelques mises à jour
    for i in range(5):
        print(f"\n--- Update Cycle {i+1} ---")
        # Simuler le passage du temps jusqu'à la fin de la condition actuelle
        ticks_to_simulate = generator.current_condition_duration + 1
        print(f"Simulating {ticks_to_simulate} ticks...")
        for _ in range(ticks_to_simulate):
            generator.update(1.0) # delta_time = 1 tick

        print(f"Condition after simulation: {generator.get_current_condition()}")

        # Changer de saison aléatoirement pour tester
        if i == 2:
            new_season = random.choice(list(Season))
            generator.update_season(new_season)