# src/engine/weather/weather_condition.py

import json
import random
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Optional

class WeatherType(Enum):
    """ Énumération des différents types de conditions météorologiques possibles. """
    CLEAR = auto()
    CLOUDY = auto()
    RAINY = auto()
    STORMY = auto()
    FOGGY = auto()
    SNOWY = auto()

@dataclass
class WeatherParams:
    """ Paramètres définissant les effets d'une condition météorologique. """
    visibility_range: float = 100.0  # En unités de jeu
    production_modifier: float = 1.0  # Multiplicateur
    defense_modifier: float = 1.0  # Multiplicateur
    movement_speed_modifier: float = 1.0  # Multiplicateur
    transition_duration: float = 5.0  # En secondes pour la transition vers cet état
    min_duration: float = 60.0  # En secondes
    max_duration: float = 300.0 # En secondes
    particle_system: Optional[str] = None  # Nom du système de particules
    sound_effect: Optional[str] = None  # Nom de l'effet sonore

# Type alias pour la configuration
WeatherConfig = Dict[str, Dict]

DEFAULT_CONFIG_PATH = "src/engine/weather/data/weather_config.json"

@dataclass
class WeatherCondition:
    """
    Représente l'état actuel de la météo, y compris le type,
    les paramètres associés et la gestion de la durée.
    """
    weather_type: str | WeatherType
    duration: int = 0  # Duration in ticks
    params: WeatherParams = field(init=False)
    current_duration: float = 0.0
    target_duration: float = 0.0
    _config: WeatherConfig = field(init=False, repr=False)

    def __post_init__(self):
        """ Initialisation après la création de l'instance. """
        # Convert string to WeatherType if needed
        if isinstance(self.weather_type, str):
            try:
                self.weather_type = WeatherType[self.weather_type.upper()]
            except KeyError:
                print(f"Warning: Unknown weather type '{self.weather_type}'. Using CLEAR.")
                self.weather_type = WeatherType.CLEAR
        
        self._load_config()
        self.update_params_from_config()
        self.reset_duration()
        
    @property
    def name(self):
        """Make the class compatible with the prior implementation that expects a name property."""
        if isinstance(self.weather_type, WeatherType):
            return self.weather_type.name
        return str(self.weather_type)

    def _load_config(self, config_path: str = DEFAULT_CONFIG_PATH):
        """ Charge la configuration météo depuis un fichier JSON. """
        try:
            # Utiliser un chemin relatif au script ou une configuration globale serait mieux
            # Pour l'instant, on suppose que le script est lancé depuis la racine du projet
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            print(f"Erreur: Fichier de configuration météo introuvable: {config_path}")
            self._config = {} # Utiliser une config vide en cas d'erreur
        except json.JSONDecodeError:
            print(f"Erreur: Impossible de décoder le JSON depuis: {config_path}")
            self._config = {}

    def update_params_from_config(self):
        """ Met à jour les paramètres de la condition météo actuelle depuis la configuration chargée. """
        type_name = self.weather_type.name
        if type_name in self._config.get("conditions", {}):
            config_params = self._config["conditions"][type_name]
            self.params = WeatherParams(
                visibility_range=config_params.get("visibility_range", 100.0),
                production_modifier=config_params.get("production_modifier", 1.0),
                defense_modifier=config_params.get("defense_modifier", 1.0),
                movement_speed_modifier=config_params.get("movement_speed_modifier", 1.0),
                transition_duration=config_params.get("transition_duration", 5.0),
                min_duration=config_params.get("min_duration", 60.0),
                max_duration=config_params.get("max_duration", 300.0),
                particle_system=config_params.get("particle_system"),
                sound_effect=config_params.get("sound_effect")
            )
        else:
            print(f"Avertissement: Configuration non trouvée pour {type_name}. Utilisation des paramètres par défaut.")
            self.params = WeatherParams() # Utilise les valeurs par défaut définies dans WeatherParams

    def reset_duration(self):
        """ Réinitialise la durée de la condition météo actuelle. """
        if self.params.min_duration > self.params.max_duration:
             print(f"Avertissement: min_duration ({self.params.min_duration}) > max_duration ({self.params.max_duration}) pour {self.weather_type.name}. Utilisation de min_duration.")
             self.target_duration = self.params.min_duration
        elif self.params.min_duration == self.params.max_duration:
             self.target_duration = self.params.min_duration
        else:
             self.target_duration = random.uniform(self.params.min_duration, self.params.max_duration)
        self.current_duration = 0.0

    def get_current_params(self) -> WeatherParams:
        """ Retourne les paramètres actuels de la condition météo. """
        # Pour l'instant, retourne directement les paramètres.
        # Pourrait être étendu pour gérer les transitions graduelles.
        return self.params

    def update(self, delta_time: float) -> bool:
        """
        Met à jour la durée de la condition météo actuelle.
        Retourne True si la durée est écoulée, False sinon.
        """
        self.current_duration += delta_time
        return self.current_duration >= self.target_duration

    def get_next_weather_type(self) -> WeatherType:
        """ Détermine le prochain type de météo basé sur les probabilités de transition. """
        type_name = self.weather_type.name
        transitions = self._config.get("transitions", {}).get(type_name, {})

        if not transitions:
            print(f"Avertissement: Aucune probabilité de transition définie pour {type_name}. Retour à CLEAR.")
            return WeatherType.CLEAR # Retour par défaut

        possible_next_types = list(transitions.keys())
        probabilities = list(transitions.values())

        # Vérifier si les probabilités somment à 1 (ou proche)
        prob_sum = sum(probabilities)
        if not abs(prob_sum - 1.0) < 1e-6:
             print(f"Avertissement: Les probabilités de transition pour {type_name} ne somment pas à 1 ({prob_sum}). Normalisation.")
             if prob_sum > 0:
                 probabilities = [p / prob_sum for p in probabilities]
             else: # Si la somme est 0, on ne peut pas choisir aléatoirement
                 print(f"Erreur: Somme des probabilités nulle pour {type_name}. Retour à CLEAR.")
                 return WeatherType.CLEAR


        next_type_name = random.choices(possible_next_types, weights=probabilities, k=1)[0]

        try:
            return WeatherType[next_type_name]
        except KeyError:
            print(f"Erreur: Type de météo '{next_type_name}' défini dans les transitions mais inconnu. Retour à CLEAR.")
            return WeatherType.CLEAR