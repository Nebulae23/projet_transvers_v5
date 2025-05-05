# src/engine/weather/components/weather_modifier_component.py

class WeatherModifierComponent:
    """
    Composant pour stocker et gérer les modificateurs de gameplay
    appliqués à une entité en raison des conditions météorologiques.
    Par exemple, réduction de la vitesse de déplacement sous la pluie,
    augmentation des dégâts de feu par temps sec, etc.
    """
    def __init__(self):
        self.modifiers = {} # Dictionnaire pour stocker les modificateurs actifs (e.g., {'speed': 0.8, 'fire_damage': 1.2})

    def apply_modifier(self, modifier_type: str, value: float):
        """ Applique ou met à jour un modificateur spécifique. """
        self.modifiers[modifier_type] = value

    def remove_modifier(self, modifier_type: str):
        """ Supprime un modificateur spécifique. """
        if modifier_type in self.modifiers:
            del self.modifiers[modifier_type]

    def get_modifier(self, modifier_type: str, default_value: float = 1.0) -> float:
        """ Récupère la valeur d'un modificateur, ou une valeur par défaut. """
        return self.modifiers.get(modifier_type, default_value)

    def clear_modifiers(self):
        """ Supprime tous les modificateurs actifs. """
        self.modifiers.clear()