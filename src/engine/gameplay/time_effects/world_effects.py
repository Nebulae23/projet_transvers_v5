# src/engine/gameplay/time_effects/world_effects.py
from engine.time.time_manager import TimeManager
from engine.time.day_night_cycle import TimeOfDay
# Importer d'autres systèmes si nécessaire (ex: météo, audio)
# from engine.environment.weather_system import WeatherSystem
# from engine.audio.environment_audio import EnvironmentAudio

class WorldTimeEffects:
    """
    Gère les effets environnementaux globaux liés au cycle jour/nuit.
    Cela peut inclure des changements de météo, des effets sonores,
    ou le comportement de certains éléments du monde.
    """

    def __init__(self, time_manager: TimeManager, world=None):
        """
        Initialise le gestionnaire d'effets mondiaux.

        Args:
            time_manager (TimeManager): Le gestionnaire de temps du jeu.
            world: Référence au monde du jeu pour accéder à d'autres systèmes si nécessaire.
        """
        if not isinstance(time_manager, TimeManager):
            raise TypeError("WorldTimeEffects requiert une instance de TimeManager.")
        self.time_manager = time_manager
        self.world = world # Garder une référence si besoin d'interagir avec d'autres systèmes

        # Références optionnelles à d'autres systèmes
        # self.weather_system = self.world.get_system(WeatherSystem) if self.world else None
        # self.audio_system = self.world.get_system(EnvironmentAudio) if self.world else None

        # Enregistrer le callback pour les changements de période
        self.time_manager.register_on_period_change(self._on_period_change)
        # Appliquer les effets initiaux basés sur la période de départ
        self._apply_period_effects(self.time_manager.get_current_period())

    def _on_period_change(self, old_period: TimeOfDay, new_period: TimeOfDay):
        """Callback appelé lors du changement de période jour/nuit."""
        # print(f"World Effects: Période changée en {new_period.name}. Application des effets.")
        self._apply_period_effects(new_period)

    def _apply_period_effects(self, period: TimeOfDay):
        """
        Applique les effets spécifiques à la période actuelle sur l'environnement.
        """
        # --- Effets Météo (Exemple) ---
        # if self.weather_system:
        #     if period == TimeOfDay.NIGHT:
        #         # Augmenter la probabilité de brouillard la nuit?
        #         self.weather_system.set_effect_probability("fog", 0.3)
        #         self.weather_system.set_effect_probability("rain", 0.1)
        #     elif period == TimeOfDay.DAY:
        #         self.weather_system.set_effect_probability("fog", 0.05)
        #         self.weather_system.set_effect_probability("rain", 0.05)
        #     else: # DAWN / DUSK
        #         self.weather_system.set_effect_probability("fog", 0.15)
        #         self.weather_system.set_effect_probability("rain", 0.08)

        # --- Effets Audio (Exemple) ---
        # if self.audio_system:
        #     if period in [TimeOfDay.DUSK, TimeOfDay.NIGHT]:
        #         # Jouer des sons d'ambiance nocturne (grillons, hiboux)
        #         self.audio_system.play_ambient_loop("night_ambience")
        #         self.audio_system.stop_ambient_loop("day_ambience")
        #     elif period in [TimeOfDay.DAWN, TimeOfDay.DAY]:
        #         # Jouer des sons d'ambiance diurne (oiseaux)
        #         self.audio_system.play_ambient_loop("day_ambience")
        #         self.audio_system.stop_ambient_loop("night_ambience")

        # --- Autres Effets sur le Monde ---
        # Exemple: Activer/désactiver des lumières spécifiques dans le monde
        # if self.world:
        #     light_components = self.world.get_components(WorldLightComponent) # Composant fictif
        #     for light_comp in light_components:
        #         if period == TimeOfDay.NIGHT and light_comp.type == "street_lamp":
        #             light_comp.turn_on()
        #         elif period == TimeOfDay.DAY and light_comp.type == "street_lamp":
        #             light_comp.turn_off()

        # Exemple: Comportement de la faune/flore
        # Les créatures nocturnes sortent, les fleurs de nuit s'ouvrent, etc.
        # Ceci serait probablement géré par les systèmes IA ou des composants spécifiques.

        print(f"World Effects: Effets pour {period.name} appliqués (simulation).")


    def update(self, dt):
        """
        Mise à jour continue des effets du monde si nécessaire (ex: transitions douces).
        Pour l'instant, les effets sont principalement déclenchés par _on_period_change.

        Args:
            dt (float): Delta time.
        """
        # Possibilité d'implémenter ici des transitions graduelles pour certains effets
        # en utilisant self.time_manager.get_period_progress()
        pass

    def cleanup(self):
        """Nettoie les ressources, notamment en désenregistrant le callback."""
        self.time_manager.unregister_on_period_change(self._on_period_change)
        # print("World Effects: Callback désenregistré.")

# Exemple d'utilisation (dans l'initialisation du jeu/scène)
# time_mgr = TimeManager()
# world_ref = get_world_instance() # Récupérer l'instance du monde
# world_effects_mgr = WorldTimeEffects(time_mgr, world_ref)
#
# # Dans la boucle de jeu (si update est nécessaire):
# # time_mgr.update() # Déjà appelé ailleurs probablement
# # world_effects_mgr.update(dt)
#
# # N'oubliez pas cleanup
# # world_effects_mgr.cleanup()