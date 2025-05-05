# src/engine/environment/light_system.py
import math
from engine.ecs.system import System
from engine.time.time_manager import TimeManager # Remplacé TimeSystem par TimeManager
from engine.time.day_night_cycle import TimeOfDay # Remplacé TimePhase par TimeOfDay

# Constantes pour les niveaux de lumière par période
LIGHT_LEVELS = {
    TimeOfDay.NIGHT: 0.15, # Nuit très sombre
    TimeOfDay.DAWN: 0.6,   # Transition montante
    TimeOfDay.DAY: 1.0,    # Pleine lumière
    TimeOfDay.DUSK: 0.6    # Transition descendante
}
# Niveaux de lumière cibles pour l'interpolation
TRANSITION_TARGETS = {
    TimeOfDay.DAWN: (LIGHT_LEVELS[TimeOfDay.NIGHT], LIGHT_LEVELS[TimeOfDay.DAY]), # De Nuit à Jour
    TimeOfDay.DUSK: (LIGHT_LEVELS[TimeOfDay.DAY], LIGHT_LEVELS[TimeOfDay.NIGHT])  # De Jour à Nuit
}

class LightSystem(System):
    """
    Gère l'éclairage ambiant global en fonction du cycle jour/nuit fourni par TimeManager.
    """
    def __init__(self, time_manager: TimeManager):
        """
        Initialise le système d'éclairage.

        Args:
            time_manager (TimeManager): Le gestionnaire de temps du jeu.
        """
        if not isinstance(time_manager, TimeManager):
            raise TypeError("LightSystem requiert une instance de TimeManager.")
        self.time_manager = time_manager
        self.ambient_light = LIGHT_LEVELS[TimeOfDay.DAY] # Initialiser à la lumière du jour par défaut
        self.current_period = TimeOfDay.DAY

    def _calculate_ambient_light(self):
        """Calcule le niveau de lumière ambiante actuel basé sur TimeManager."""
        self.current_period = self.time_manager.get_current_period()
        period_progress = self.time_manager.get_period_progress() # Progression dans la période actuelle (0-1)

        if self.current_period in TRANSITION_TARGETS:
            # Période de transition (Aube ou Crépuscule)
            start_light, end_light = TRANSITION_TARGETS[self.current_period]
            # Interpolation linéaire simple
            # Pourrait être remplacé par une courbe plus douce (ex: smoothstep) si nécessaire
            self.ambient_light = start_light + (end_light - start_light) * period_progress
        else:
            # Période stable (Jour ou Nuit)
            self.ambient_light = LIGHT_LEVELS[self.current_period]

        # S'assurer que la lumière reste dans les bornes [0, 1]
        self.ambient_light = max(0.0, min(1.0, self.ambient_light))

    def update(self, dt, world):
        """
        Met à jour le niveau de lumière ambiante et l'applique aux entités concernées.

        Args:
            dt (float): Delta time (non utilisé directement ici, mais standard pour les systèmes).
            world (World): L'instance du monde ECS contenant les entités.
        """
        # 1. Calculer le niveau de lumière actuel basé sur le TimeManager
        self._calculate_ambient_light()

        # 2. Appliquer l'effet de lumière aux entités (si nécessaire)
        #    Cette partie dépend de la conception des composants.
        #    Exemple : Mettre à jour un composant 'Lighting' ou 'Visibility'.
        #    L'implémentation précédente modifiait directement 'entity.visibility'.
        #    On garde une logique similaire pour l'instant.
        #    TODO: Remplacer par une approche basée composants (ex: world.get_components(VisibilityComponent))
        for entity in world.entities: # Accès via world.entities (supposé)
            if hasattr(entity, 'light_sensitive') and entity.light_sensitive:
                 # Exemple: Moduler la visibilité ou une autre propriété
                 # Ici, on affecte directement, mais un composant serait mieux
                 entity.visibility_multiplier = self.ambient_light
                 # print(f"Entity {entity.id} visibility set to {self.ambient_light:.2f}")


    def get_ambient_light(self):
        """Retourne le niveau de lumière ambiante actuel (0.0 à 1.0)."""
        return self.ambient_light

    def get_current_period(self):
        """Retourne la période actuelle de la journée (TimeOfDay)."""
        return self.current_period