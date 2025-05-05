# src/engine/weather/components/weather_component.py

# Potentiellement utilisé si des entités spécifiques doivent suivre l'état météo localement,
# mais souvent l'état météo est géré globalement par WeatherSystem.
# Ce fichier sert de placeholder pour l'instant.

class WeatherComponent:
    """
    Composant pour stocker l'état météorologique pertinent pour une entité spécifique,
    si nécessaire. Pourrait être utilisé pour des effets locaux ou des zones
    avec une météo différente du reste du monde.
    """
    def __init__(self, initial_state=None):
        self.current_state = initial_state # Référence à une WeatherCondition ou état simplifié

    def update_state(self, new_state):
        self.current_state = new_state