# src/engine/weather/weather_effects.py

from .weather_condition import WeatherCondition, WeatherParams
# Importer potentiellement d'autres modules nécessaires (ex: World, EntityManager, etc.)
# from ..ecs.world import World

class WeatherEffects:
    """
    Gère l'application des effets météorologiques sur les entités et le monde du jeu.
    """
    def __init__(self): # Potentiellement passer une référence au World ou EntityManager
        self.current_params: WeatherParams = WeatherParams() # Paramètres par défaut initiaux
        self.target_params: WeatherParams = WeatherParams()
        self.transitioning: bool = False
        self.transition_timer: float = 0.0
        self.transition_duration: float = 0.0
        # self.world = world # Référence au monde si nécessaire pour appliquer les effets

    def start_transition(self, new_condition: WeatherCondition):
        """ Commence la transition vers une nouvelle condition météorologique. """
        self.target_params = new_condition.get_current_params()
        self.transition_duration = self.target_params.transition_duration
        self.transition_timer = 0.0
        self.transitioning = True
        print(f"Début de la transition vers {new_condition.weather_type.name} sur {self.transition_duration}s")

    def update(self, delta_time: float):
        """ Met à jour la transition des effets météorologiques. """
        if not self.transitioning:
            return

        self.transition_timer += delta_time
        progress = min(self.transition_timer / self.transition_duration, 1.0)

        # Interpolation linéaire simple pour les paramètres numériques
        self.current_params.visibility_range = self._lerp(
            self.current_params.visibility_range, self.target_params.visibility_range, progress
        )
        self.current_params.production_modifier = self._lerp(
            self.current_params.production_modifier, self.target_params.production_modifier, progress
        )
        self.current_params.defense_modifier = self._lerp(
            self.current_params.defense_modifier, self.target_params.defense_modifier, progress
        )
        self.current_params.movement_speed_modifier = self._lerp(
            self.current_params.movement_speed_modifier, self.target_params.movement_speed_modifier, progress
        )

        # Pour les systèmes de particules et sons, on pourrait les activer/désactiver
        # ou les fondre enchaînés à mi-transition ou à la fin.
        # Ici, on les change instantanément à la fin pour simplifier.
        if progress >= 1.0:
            self.transitioning = False
            self.current_params.particle_system = self.target_params.particle_system
            self.current_params.sound_effect = self.target_params.sound_effect
            # Copier tous les paramètres finaux pour s'assurer de la cohérence
            self.current_params = self.target_params
            print("Transition terminée.")

        # Appliquer les effets actuels (interpolés) au monde/entités
        self.apply_effects()

    def apply_effects(self):
        """
        Applique les modificateurs de gameplay actuels.
        Ceci est un placeholder. L'implémentation réelle dépendra de la structure du jeu
        (ex: itérer sur les entités avec certains composants, modifier des variables globales, etc.).
        """
        # Exemple: Modifier la visibilité globale (pour le brouillard, etc.)
        # world.set_global_visibility(self.current_params.visibility_range)
        # print(f"Visibilité appliquée: {self.current_params.visibility_range}")

        # Exemple: Modifier les composants des entités (production, défense, vitesse)
        # for entity, (prod_comp, def_comp, move_comp) in self.world.get_components(ProductionComponent, DefenseComponent, MovementComponent):
        #     prod_comp.modifier = self.current_params.production_modifier
        #     def_comp.modifier = self.current_params.defense_modifier
        #     move_comp.speed_modifier = self.current_params.movement_speed_modifier
        # print(f"Modificateurs appliqués: Prod={self.current_params.production_modifier}, Def={self.current_params.defense_modifier}, Move={self.current_params.movement_speed_modifier}")

        # Gérer les systèmes de particules et les sons
        # particle_manager.set_active_system(self.current_params.particle_system)
        # sound_manager.play_ambient(self.current_params.sound_effect)
        pass # L'implémentation réelle est laissée pour l'intégration

    def get_current_params(self) -> WeatherParams:
        """ Retourne les paramètres météorologiques actuellement actifs (interpolés pendant la transition). """
        return self.current_params

    def _lerp(self, start: float, end: float, t: float) -> float:
        """ Interpolation linéaire. """
        return start + (end - start) * t

# Exemple d'utilisation (sera géré par WeatherSystem)
# weather_effects = WeatherEffects()
# sunny_condition = WeatherCondition(WeatherType.CLEAR) # Chargera depuis config
# rainy_condition = WeatherCondition(WeatherType.RAINY) # Chargera depuis config
#
# weather_effects.start_transition(rainy_condition)
# # Dans la boucle de jeu:
# # weather_effects.update(delta_time)